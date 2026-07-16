"""Subprocess runner with live console streaming."""

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

    @property
    def running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def start(self, command: str, cwd: Optional[str] = None, shell: bool = True) -> None:
        if self.running:
            self.on_line("[TrueNexus] A process is already running. Stop it first.\n")
            return
        self.on_line(f"$ {command}\n")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        try:
            self.proc = subprocess.Popen(
                command,
                cwd=cwd or None,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                bufsize=1,
            )
        except Exception as exc:
            self.on_line(f"[TrueNexus] Failed to start: {exc}\n")
            self.on_done(-1)
            return

        def _pump() -> None:
            assert self.proc is not None
            try:
                if self.proc.stdout:
                    for line in self.proc.stdout:
                        self.on_line(line)
            finally:
                code = self.proc.wait()
                self.on_line(f"\n[TrueNexus] Process exited with code {code}\n")
                self.on_done(code)

        self._thread = threading.Thread(target=_pump, daemon=True)
        self._thread.start()

    def send(self, text: str) -> None:
        if not self.running or not self.proc or not self.proc.stdin:
            return
        try:
            self.proc.stdin.write(text if text.endswith("\n") else text + "\n")
            self.proc.stdin.flush()
        except Exception as exc:
            self.on_line(f"[TrueNexus] stdin error: {exc}\n")

    def stop(self) -> None:
        if not self.proc:
            return
        try:
            self.proc.terminate()
        except Exception:
            pass
        try:
            self.proc.kill()
        except Exception:
            pass
        self.on_line("[TrueNexus] Stop requested.\n")
