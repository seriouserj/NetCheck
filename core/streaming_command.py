"""
Version: 1.5.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add bounded subprocess execution with line-by-line output delivery.
"""

from __future__ import annotations

import os
import pty
import selectors
import subprocess
import time
from collections.abc import Callable, Sequence

from core.command_runner import CommandResult

OutputCallback = Callable[[str], None]


def run_streaming_command(
    command: Sequence[str],
    timeout: float,
    output_callback: OutputCallback | None = None,
) -> CommandResult:
    """Run a command without a shell and deliver each output line immediately."""
    if timeout <= 0:
        raise ValueError("Timeout must be greater than zero.")
    master_fd, slave_fd = pty.openpty()
    try:
        process = subprocess.Popen(
            list(command),
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
    except (FileNotFoundError, PermissionError, OSError) as error:
        os.close(master_fd)
        os.close(slave_fd)
        return CommandResult(127, "", str(error))
    os.close(slave_fd)
    os.set_blocking(master_fd, False)

    lines: list[str] = []
    pending = b""
    deadline = time.monotonic() + timeout
    timed_out = False
    selector = selectors.DefaultSelector()
    selector.register(master_fd, selectors.EVENT_READ)
    try:
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                process.terminate()
                try:
                    process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=1.0)
                break
            if selector.select(min(0.1, remaining)):
                pending, _ = _read_available(master_fd, pending, lines, output_callback)
        while selector.select(0.01):
            pending, received_data = _read_available(
                master_fd, pending, lines, output_callback
            )
            if not received_data:
                break
        if pending:
            _publish(pending.decode("utf-8", errors="replace").rstrip("\r"), lines, output_callback)
    finally:
        selector.close()
        os.close(master_fd)

    if timed_out:
        message = f"Command timed out after {timeout:.1f} seconds."
        _notify(message, output_callback)
        return CommandResult(124, "\n".join(lines), message)
    return CommandResult(process.returncode or 0, "\n".join(lines), "")


def _read_available(
    descriptor: int,
    pending: bytes,
    lines: list[str],
    output_callback: OutputCallback | None,
) -> tuple[bytes, bool]:
    """Read available pseudo-terminal bytes and publish complete lines."""
    try:
        chunk = os.read(descriptor, 4096)
    except (BlockingIOError, OSError):
        return pending, False
    pending += chunk
    while b"\n" in pending:
        raw_line, pending = pending.split(b"\n", 1)
        _publish(raw_line.decode("utf-8", errors="replace").rstrip("\r"), lines, output_callback)
    return pending, bool(chunk)


def _publish(line: str, lines: list[str], output_callback: OutputCallback | None) -> None:
    """Store and publish one normalized output line."""
    lines.append(line)
    _notify(line, output_callback)


def _notify(line: str, output_callback: OutputCallback | None) -> None:
    """Protect command execution from a deleted optional UI callback."""
    if output_callback is None:
        return
    try:
        output_callback(line)
    except RuntimeError:
        pass
