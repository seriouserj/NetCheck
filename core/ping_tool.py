"""
Version: 1.5.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Stream bounded ICMP ping output as each response arrives.
"""

from __future__ import annotations

from collections.abc import Callable

from core.command_runner import CommandResult
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
    result = runner(("ping", "-n", "-c", str(count), target), timeout, output_callback)
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if not output:
        raise RuntimeError("Ping produced no output.")
    return output
