"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify macOS and Windows route-hop monitoring.
"""

from threading import Event

from core.command_runner import CommandResult
from core.platform_commands import traceroute_command
from core.route_monitor import monitor_route, parse_route_hop


def test_parses_reachable_and_timed_out_route_hops() -> None:
    assert parse_route_hop(" 1  192.168.1.1  1.234 ms") == (1, "192.168.1.1", 1.234)
    assert parse_route_hop(" 2  *") == (2, "—", None)
    assert parse_route_hop("traceroute to example.com") is None


def test_parses_windows_tracert_hop() -> None:
    assert parse_route_hop("  2    <1 ms    <1 ms     1 ms  192.168.1.1") == (
        2,
        "192.168.1.1",
        1.0,
    )


def test_monitor_aggregates_loss_and_latency() -> None:
    calls = 0
    updates: list[object] = []

    def runner(command: tuple[str, ...], timeout: float, callback: object, stop: Event | None) -> CommandResult:
        nonlocal calls
        calls += 1
        assert callable(callback)
        callback(" 1  192.0.2.1  1.0 ms")
        callback(" 2  *" if calls == 1 else " 2  198.51.100.1  4.0 ms")
        return CommandResult(0, "", "")

    result = monitor_route(
        "example.com",
        cycles=2,
        interval_seconds=0.1,
        update_callback=updates.append,
        runner=runner,
    )

    assert calls == 2
    assert result[0].sent == 2
    assert result[0].average_ms == 1.0
    assert result[1].sent == 2
    assert result[1].received == 1
    assert result[1].loss_percent == 50.0
    assert updates


def test_monitor_builds_bounded_numeric_traceroute_command() -> None:
    commands: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...], timeout: float, callback: object, stop: Event | None) -> CommandResult:
        commands.append(command)
        return CommandResult(0, "", "")

    monitor_route("router", cycles=1, runner=runner)

    assert commands == [traceroute_command("router")]
