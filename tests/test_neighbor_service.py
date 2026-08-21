"""
Version: 1.9.3
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify the complete default CDP capture interval.
"""

from pathlib import Path

import core.neighbor_service as neighbor_service
from core.command_runner import CommandResult
from core.neighbor_service import DEFAULT_NEIGHBOR_TIMEOUT, NeighborService


def test_neighbor_discovery_uses_one_privileged_worker(monkeypatch) -> None:
    monkeypatch.setattr(neighbor_service.sys, "platform", "darwin")
    calls: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...], timeout: float) -> CommandResult:
        return CommandResult(0, "/usr/sbin/tcpdump", "")

    def privileged(command: tuple[str, ...], timeout: float) -> CommandResult:
        calls.append(command)
        Path(command[-1]).write_text(
            "LLDP, System Name TLV (5), length 7: switch1\n"
            "Port ID TLV (2), length 5: Interface Name: Gi1/0/1\n"
            "CDP v2, Device-ID (0x01), length: 'core-sw'\n"
            "Port-ID (0x03), length: 'Gi0/24'",
            encoding="utf-8",
        )
        return CommandResult(0, "", "")

    def capture(command, timeout, output_callback, cancel_event) -> CommandResult:
        return CommandResult(1, "", "tcpdump: /dev/bpf0: Permission denied")

    neighbors = NeighborService(runner, privileged, capture).discover("en7", 2.0)

    assert [item.protocol for item in neighbors] == ["LLDP", "CDP"]
    assert len(calls) == 1
    assert "--neighbor-worker" in calls[0]


def test_neighbor_discovery_avoids_authorization_when_bpf_is_accessible(monkeypatch) -> None:
    monkeypatch.setattr(neighbor_service.sys, "platform", "darwin")

    def runner(command: tuple[str, ...], timeout: float) -> CommandResult:
        return CommandResult(0, "/usr/sbin/tcpdump", "")

    def privileged(command: tuple[str, ...], timeout: float) -> CommandResult:
        raise AssertionError("Privilege fallback must not run")

    def capture(command, timeout, output_callback, cancel_event) -> CommandResult:
        return CommandResult(
            124,
            "CDPv2, Device-ID (0x01), length: 9 bytes: edge-sw-1",
            "Command timed out after 2.0 seconds.",
        )

    neighbors = NeighborService(runner, privileged, capture).discover("en7", 2.0)

    assert [neighbor.system_name for neighbor in neighbors] == ["edge-sw-1"]


def test_neighbor_discovery_uses_complete_cdp_interval(monkeypatch) -> None:
    monkeypatch.setattr(neighbor_service.sys, "platform", "darwin")
    observed: list[float] = []

    def runner(command: tuple[str, ...], timeout: float) -> CommandResult:
        return CommandResult(0, "/usr/sbin/tcpdump", "")

    def capture(command, timeout, output_callback, cancel_event) -> CommandResult:
        observed.append(timeout)
        return CommandResult(124, "", "timed out")

    assert NeighborService(runner, capture_runner=capture).discover("en0") == []
    assert observed == [DEFAULT_NEIGHBOR_TIMEOUT]
    assert DEFAULT_NEIGHBOR_TIMEOUT >= 65.0
