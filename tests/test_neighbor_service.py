"""
Version: 1.5.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify combined LLDP and CDP capture uses one authorization.
"""

from pathlib import Path

from core.command_runner import CommandResult
from core.neighbor_service import NeighborService


def test_neighbor_discovery_uses_one_privileged_worker() -> None:
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

    neighbors = NeighborService(runner, privileged).discover("en7", 2.0)

    assert [item.protocol for item in neighbors] == ["LLDP", "CDP"]
    assert len(calls) == 1
    assert "--neighbor-worker" in calls[0]
