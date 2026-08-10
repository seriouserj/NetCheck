"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify multi-target parsing, payload selection, and finite batches.
"""

from threading import Event

import pytest

from core.command_runner import CommandResult
from core.multi_ping import parse_ping_targets, run_multi_ping


def test_parses_and_deduplicates_multiple_ping_targets() -> None:
    assert parse_ping_targets("router.local, 192.0.2.1\nrouter.local;server") == (
        "router.local",
        "192.0.2.1",
        "server",
    )


def test_rejects_ping_option_injection() -> None:
    with pytest.raises(ValueError, match="hyphen"):
        parse_ping_targets("-f")


def test_finite_multi_ping_uses_four_requests_and_payload_size() -> None:
    commands: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...], timeout: float, callback: object, stop: Event | None) -> CommandResult:
        commands.append(command)
        return CommandResult(0, "ok", "")

    output = run_multi_ping(("192.0.2.1", "192.0.2.2"), packet_size=65000, runner=runner)

    assert set(commands) == {
        ("ping", "-n", "-c", "4", "-s", "65000", "192.0.2.1"),
        ("ping", "-n", "-c", "4", "-s", "65000", "192.0.2.2"),
    }
    assert "192.0.2.1: exit 0" in output
    assert "192.0.2.2: exit 0" in output


def test_rejects_oversized_payload() -> None:
    with pytest.raises(ValueError, match="65507"):
        run_multi_ping(("example.com",), packet_size=65508)


def test_continuous_mode_uses_hundred_request_batches() -> None:
    stop = Event()
    commands: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...], timeout: float, callback: object, event: Event | None) -> CommandResult:
        commands.append(command)
        stop.set()
        return CommandResult(0, "statistics", "")

    run_multi_ping(("router",), continuous=True, cancel_event=stop, runner=runner)

    assert commands == [("ping", "-n", "-c", "100", "-s", "56", "router")]
