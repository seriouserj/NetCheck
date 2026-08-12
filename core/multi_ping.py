"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Run concurrent payload-controlled ping sessions on macOS and Windows.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from core.command_runner import CommandResult
from core.platform_commands import ping_command
from core.streaming_command import OutputCallback, run_streaming_command

Runner = Callable[[tuple[str, ...], float, OutputCallback | None, Event | None], CommandResult]
_SEPARATORS = re.compile(r"[,;\s]+")


def parse_ping_targets(value: str, maximum: int = 16) -> tuple[str, ...]:
    """Parse a comma, semicolon, space, or newline separated target list."""
    targets = tuple(dict.fromkeys(part for part in _SEPARATORS.split(value.strip()) if part))
    if not targets:
        raise ValueError("Enter at least one ping target.")
    if len(targets) > maximum:
        raise ValueError(f"A maximum of {maximum} simultaneous targets is supported.")
    if any(target.startswith("-") for target in targets):
        raise ValueError("Ping targets cannot begin with a hyphen.")
    return targets


def run_multi_ping(
    targets: tuple[str, ...],
    *,
    packet_size: int = 56,
    continuous: bool = False,
    output_callback: OutputCallback | None = None,
    cancel_event: Event | None = None,
    runner: Runner = run_streaming_command,
) -> str:
    """Ping multiple targets concurrently and publish terminal output as it arrives."""
    if not targets:
        raise ValueError("Enter at least one ping target.")
    if not 0 <= packet_size <= 65507:
        raise ValueError("Packet payload must be between 0 and 65507 bytes.")
    stop = cancel_event or Event()
    summaries: list[str] = []

    def run_target(target: str) -> str:
        batch_size = 100 if continuous else 4
        batch = 0
        last_result = CommandResult(0, "", "")
        while not stop.is_set():
            batch += 1
            _emit(f"=== {target} · batch {batch} · {packet_size} byte payload ===", output_callback)
            command = ping_command(target, batch_size, packet_size)
            last_result = runner(
                command,
                max(12.0, batch_size * 2.0 + 5.0),
                lambda line: _emit(f"[{target}] {line}", output_callback),
                stop,
            )
            if not continuous or last_result.return_code not in (0, 130, -15):
                break
        return f"{target}: stopped" if stop.is_set() else f"{target}: exit {last_result.return_code}"

    with ThreadPoolExecutor(max_workers=len(targets), thread_name_prefix="netcheck-ping") as pool:
        summaries.extend(pool.map(run_target, targets))
    summary = "\n".join(summaries)
    _emit(summary, output_callback)
    return summary


def _emit(message: str, callback: OutputCallback | None) -> None:
    """Publish output when a UI callback is present."""
    if callback is not None:
        callback(message)
