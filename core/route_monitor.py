"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Monitor route quality through native macOS or Windows tracing.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from threading import Event

from core.command_runner import CommandResult
from core.platform_commands import traceroute_command
from core.streaming_command import OutputCallback, run_streaming_command

Runner = Callable[[tuple[str, ...], float, OutputCallback | None, Event | None], CommandResult]
UpdateCallback = Callable[[tuple["RouteHopStats", ...]], None]
_HOP_LINE = re.compile(r"^\s*(?P<hop>\d+)\s+(?P<body>.+)$")
_LATENCY = re.compile(r"(?P<latency>\d+(?:\.\d+)?)\s*ms")
_IPV4_ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


@dataclass(frozen=True, slots=True)
class RouteHopStats:
    """Aggregated reachability and latency for one route hop."""

    hop: int
    address: str
    sent: int
    received: int
    last_ms: float | None
    average_ms: float | None
    best_ms: float | None
    worst_ms: float | None

    @property
    def loss_percent(self) -> float:
        """Return packet loss as a percentage."""
        return ((self.sent - self.received) / self.sent * 100.0) if self.sent else 0.0


@dataclass(slots=True)
class _Accumulator:
    hop: int
    address: str = "—"
    sent: int = 0
    received: int = 0
    last_ms: float | None = None
    total_ms: float = 0.0
    best_ms: float | None = None
    worst_ms: float | None = None

    def record(self, address: str, latency_ms: float | None) -> None:
        self.sent += 1
        self.address = address
        self.last_ms = latency_ms
        if latency_ms is None:
            return
        self.received += 1
        self.total_ms += latency_ms
        self.best_ms = latency_ms if self.best_ms is None else min(self.best_ms, latency_ms)
        self.worst_ms = latency_ms if self.worst_ms is None else max(self.worst_ms, latency_ms)

    def snapshot(self) -> RouteHopStats:
        average = self.total_ms / self.received if self.received else None
        return RouteHopStats(
            self.hop,
            self.address,
            self.sent,
            self.received,
            self.last_ms,
            average,
            self.best_ms,
            self.worst_ms,
        )


def parse_route_hop(line: str) -> tuple[int, str, float | None] | None:
    """Parse one numeric traceroute output line."""
    match = _HOP_LINE.match(line)
    if match is None:
        return None
    body = match.group("body").strip()
    windows_addresses = _IPV4_ADDRESS.findall(body)
    address = windows_addresses[-1] if windows_addresses else "—" if body.startswith("*") else body.split()[0]
    latency_match = _LATENCY.search(body)
    latency = float(latency_match.group("latency")) if latency_match else None
    return int(match.group("hop")), address, latency


def monitor_route(
    target: str,
    *,
    cycles: int = 10,
    interval_seconds: float = 1.0,
    continuous: bool = False,
    update_callback: UpdateCallback | None = None,
    cancel_event: Event | None = None,
    runner: Runner = run_streaming_command,
) -> tuple[RouteHopStats, ...]:
    """Repeatedly trace a route and publish WinMTR-style hop statistics."""
    target = target.strip()
    if not target or target.startswith("-"):
        raise ValueError("Enter a valid route monitor target.")
    if not 1 <= cycles <= 1000:
        raise ValueError("Cycles must be between 1 and 1000.")
    if not 0.1 <= interval_seconds <= 60.0:
        raise ValueError("Interval must be between 0.1 and 60 seconds.")
    stop = cancel_event or Event()
    accumulators: dict[int, _Accumulator] = {}
    cycle = 0
    while not stop.is_set() and (continuous or cycle < cycles):
        cycle += 1

        def receive(line: str) -> None:
            parsed = parse_route_hop(line)
            if parsed is None:
                return
            hop, address, latency = parsed
            accumulator = accumulators.setdefault(hop, _Accumulator(hop))
            accumulator.record(address, latency)
            if update_callback is not None:
                update_callback(_snapshot(accumulators))

        result = runner(
            traceroute_command(target),
            35.0,
            receive,
            stop,
        )
        if result.return_code == 127:
            raise RuntimeError(result.stderr or "Traceroute is unavailable.")
        if not continuous and cycle >= cycles:
            break
        if stop.wait(interval_seconds):
            break
    return _snapshot(accumulators)


def _snapshot(accumulators: dict[int, _Accumulator]) -> tuple[RouteHopStats, ...]:
    """Return immutable hop statistics ordered by hop number."""
    return tuple(accumulators[hop].snapshot() for hop in sorted(accumulators))
