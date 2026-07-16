"""Subprocess runner with live console streaming (Windows-friendly)."""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable
from typing import Optional

# Windows: kill entire tree spawned by shell=True (cmd.exe -> keyhunt.exe)
_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


class ProcessRunner:
    def __init__(self, on_line: Callable[[str], None], on_done: Callable[[int], None]):
        self.on_line = on_line
        self.on_done = on_done
        self.proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stopping = False
        self._generation = 0  # bump on each start/stop to ignore stale pump callbacks

    @property
    def running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def start(self, command: str, cwd: Optional[str] = None, shell: bool = True) -> None:
        with self._lock:
            if self.running:
                self.on_line("[TrueNexus] A process is already running. Stop it first.\n")
                return

            command = (command or "").strip()
            if not command:
                self.on_line("[TrueNexus] Empty command.\n")
                self.on_done(-1)
                return

            if cwd and not os.path.isdir(cwd):
                self.on_line(f"[TrueNexus] Working directory does not exist: {cwd}\n")
                self.on_done(-1)
                return

            # Ensure any orphaned previous tree is gone before starting again
            self._kill_proc_tree(self.proc)
            self.proc = None
            self._stopping = False
            self._generation += 1
            gen = self._generation

            self.on_line(f"$ {command}\n")
            if cwd:
                self.on_line(f"[TrueNexus] cwd: {cwd}\n")

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            creationflags = 0
            if os.name == "nt":
                creationflags = _CREATE_NO_WINDOW | _CREATE_NEW_PROCESS_GROUP

            try:
                self.proc = subprocess.Popen(
                    command,
                    cwd=cwd or None,
                    shell=shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    env=env,
                    bufsize=0,
                    creationflags=creationflags,
                )
            except Exception as exc:
                self.on_line(f"[TrueNexus] Failed to start: {exc}\n")
                self.proc = None
                self.on_done(-1)
                return

            proc = self.proc

            def _pump() -> None:
                code = -1
                try:
                    assert proc.stdout is not None
                    buf = b""
                    while True:
                        if self._stopping and self._generation != gen:
                            break
                        chunk = proc.stdout.read(256)
                        if not chunk:
                            break
                        # Drop output after stop so console doesn't look "alive"
                        if self._stopping:
                            continue
                        buf += chunk
                        while b"\n" in buf or b"\r" in buf:
                            if b"\n" in buf:
                                line, buf = buf.split(b"\n", 1)
                                text = line.decode("utf-8", errors="replace").rstrip("\r") + "\n"
                            else:
                                line, buf = buf.split(b"\r", 1)
                                text = line.decode("utf-8", errors="replace") + "\r"
                            if text.strip("\r\n"):
                                self.on_line(
                                    text if text.endswith("\n") or text.endswith("\r") else text + "\n"
                                )
                    if buf.strip() and not self._stopping:
                        self.on_line(buf.decode("utf-8", errors="replace") + "\n")
                except Exception as exc:
                    if not self._stopping:
                        self.on_line(f"[TrueNexus] Reader error: {exc}\n")
                finally:
                    try:
                        code = proc.wait(timeout=3)
                    except Exception:
                        self._kill_proc_tree(proc)
                        try:
                            code = proc.wait(timeout=3)
                        except Exception:
                            code = -1
                    if self._generation == gen:
                        if self._stopping:
                            self.on_line("\n[TrueNexus] Stopped.\n")
                            self.on_done(code if code is not None else -1)
                        else:
                            self.on_line(f"\n[TrueNexus] Process exited with code {code}\n")
                            self.on_done(code)
                        with self._lock:
                            if self.proc is proc:
                                self.proc = None

            self._thread = threading.Thread(target=_pump, daemon=True, name="TrueNexus-runner")
            self._thread.start()

    def send(self, text: str) -> None:
        if not self.running or not self.proc or not self.proc.stdin:
            return
        try:
            data = (text if text.endswith("\n") else text + "\n").encode("utf-8", errors="replace")
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        except Exception as exc:
            self.on_line(f"[TrueNexus] stdin error: {exc}\n")

    def stop(self) -> None:
        with self._lock:
            proc = self.proc
            if not proc and not self.running:
                self.on_line("[TrueNexus] Nothing running.\n")
                return
            self._stopping = True
            self._generation += 1  # invalidate pump "still running" output
            self.on_line("[TrueNexus] Stop requested — killing process tree...\n")

        self._kill_proc_tree(proc)

        # Hard fallback: stop known engine binaries that may have detached
        if os.name == "nt":
            for image in ("keyhunt.exe", "keyhunt_cuda.exe", "TrueMkeyCollider.exe"):
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", image],
                        capture_output=True,
                        creationflags=_CREATE_NO_WINDOW,
                        timeout=8,
                    )
                except Exception:
                    pass

        # Give Windows a moment, then clear handle
        time.sleep(0.15)
        with self._lock:
            if self.proc is not None and self.proc.poll() is not None:
                self.proc = None
            elif self.proc is not None:
                try:
                    self.proc.kill()
                except Exception:
                    pass
                self.proc = None

        self.on_line("[TrueNexus] Stop complete.\n")
        self._status_done_safe(-1)

    def _status_done_safe(self, code: int) -> None:
        try:
            self.on_done(code)
        except Exception:
            pass

    @staticmethod
    def _kill_proc_tree(proc: Optional[subprocess.Popen]) -> None:
        if proc is None:
            return
        pid = getattr(proc, "pid", None)
        if not pid:
            return
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    capture_output=True,
                    creationflags=_CREATE_NO_WINDOW,
                    timeout=10,
                )
            except Exception:
                pass
            try:
                proc.kill()
            except Exception:
                pass
            return
        # POSIX: kill process group if possible
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass
        time.sleep(0.2)
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
