"""Subprocess runner with live console streaming (Windows-friendly)."""

from __future__ import annotations

import os
import subprocess
import threading
from collections.abc import Callable
from typing import Optional


class ProcessRunner:
    def __init__(self, on_line: Callable[[str], None], on_done: Callable[[int], None]):
        self.on_line = on_line
        self.on_done = on_done
        self.proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

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

            self.on_line(f"$ {command}\n")
            if cwd:
                self.on_line(f"[TrueNexus] cwd: {cwd}\n")

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            # Encourage C runtime line buffering where supported
            env["NSUNBUFFERED"] = "1"

            creationflags = 0
            if os.name == "nt":
                # Avoid freezing GUI on Ctrl handlers; keep a console-less child
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            try:
                self.proc = subprocess.Popen(
                    command,
                    cwd=cwd or None,
                    shell=shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    env=env,
                    bufsize=0,  # unbuffered binary
                    creationflags=creationflags,
                )
            except Exception as exc:
                self.on_line(f"[TrueNexus] Failed to start: {exc}\n")
                self.proc = None
                self.on_done(-1)
                return

            def _pump() -> None:
                assert self.proc is not None
                code = -1
                try:
                    assert self.proc.stdout is not None
                    buf = b""
                    while True:
                        chunk = self.proc.stdout.read(256)
                        if not chunk:
                            break
                        buf += chunk
                        while b"\n" in buf or b"\r" in buf:
                            # Prefer newline; also flush bare CR progress lines
                            if b"\n" in buf:
                                line, buf = buf.split(b"\n", 1)
                                text = line.decode("utf-8", errors="replace").rstrip("\r") + "\n"
                            else:
                                line, buf = buf.split(b"\r", 1)
                                text = line.decode("utf-8", errors="replace") + "\r"
                            if text.strip("\r\n"):
                                self.on_line(text if text.endswith("\n") or text.endswith("\r") else text + "\n")
                    if buf.strip():
                        self.on_line(buf.decode("utf-8", errors="replace") + "\n")
                except Exception as exc:
                    self.on_line(f"[TrueNexus] Reader error: {exc}\n")
                finally:
                    try:
                        code = self.proc.wait(timeout=5)
                    except Exception:
                        try:
                            self.proc.kill()
                            code = self.proc.wait(timeout=3)
                        except Exception:
                            code = -1
                    self.on_line(f"\n[TrueNexus] Process exited with code {code}\n")
                    self.on_done(code)

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
        proc = self.proc
        if not proc:
            return
        self.on_line("[TrueNexus] Stop requested.\n")
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            if proc.poll() is None:
                proc.kill()
        except Exception:
            pass
