"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Stream native macOS and Windows ping output.
"""

from __future__ import annotations

from collections.abc import Callable

from core.command_runner import CommandResult
from core.platform_commands import ping_command
from core.streaming_command import OutputCallback, run_streaming_command

Runner = Callable[[tuple[str, ...], float, OutputCallback | None], CommandResult]


def ping(
    target: str,
    count: int = 4,
    timeout: float = 8.0,
    output_callback: OutputCallback | None = None,
    runner: Runner = run_streaming_command,
) -> str:
    """Ping a target and return the complete diagnostic output."""
    target = target.strip()
    if not target:
        raise ValueError("Enter a ping target.")
    result = runner(ping_command(target, count), timeout, output_callback)
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if not output:
        raise RuntimeError("Ping produced no output.")
    return output
