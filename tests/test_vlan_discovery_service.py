"""
Version: 1.2.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify passive VLAN parsing and single authorized worker execution.
"""

from pathlib import Path

from core.command_runner import CommandResult
from core.vlan_discovery_service import VlanDiscoveryService, parse_observed_vlan_ids


def test_parses_unique_valid_vlan_tags() -> None:
    capture = """
    12:00:00 aa > bb, ethertype 802.1Q, vlan 162, p 0, IPv4
    12:00:01 aa > bb, ethertype 802.1Q, vlan 4094, p 0, IPv6
    12:00:02 aa > bb, ethertype 802.1Q, vlan 162, p 0, ARP
    12:00:03 aa > bb, ethertype 802.1Q, vlan 4095, p 0, IPv4
    """

    assert parse_observed_vlan_ids(capture) == [162, 4094]


def test_discovery_uses_one_privileged_worker() -> None:
    calls: list[tuple[str, ...]] = []

    def privileged(command: tuple[str, ...], timeout: float) -> CommandResult:
        calls.append(command)
        Path(command[-1]).write_text("[192,162,192]", encoding="utf-8")
        return CommandResult(0, "", "")

    result = VlanDiscoveryService(privileged).discover("en7", 2.0)

    assert result == [162, 192]
    assert len(calls) == 1
    assert "--vlan-discovery-worker" in calls[0]
