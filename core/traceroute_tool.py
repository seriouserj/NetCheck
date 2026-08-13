"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Support cancelling a running route trace from the user interface.
"""

from __future__ import annotations

from collections.abc import Callable
from threading import Event

from core.command_runner import CommandResult
from core.platform_commands import traceroute_command
from core.streaming_command import OutputCallback, run_streaming_command

Runner = Callable[[tuple[str, ...], float, OutputCallback | None, Event | None], CommandResult]


def traceroute(
    target: str,
    maximum_hops: int = 30,
    timeout: float = 45.0,
    output_callback: OutputCallback | None = None,
    cancel_event: Event | None = None,
    runner: Runner = run_streaming_command,
) -> str:
    """Trace the route to a hostname or IP address."""
    target = target.strip()
    if not target:
        raise ValueError("Enter a traceroute target.")
    command = traceroute_command(target, maximum_hops)
    result = runner(command, timeout, output_callback, cancel_event)
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if not output:
        raise RuntimeError("Traceroute produced no output.")
    return output
