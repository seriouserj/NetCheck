"""
Version: 1.9.2
Date: 2026-08-18
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify unprivileged passive capture and authorization fallback.
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

    def capture(command, timeout, output_callback, cancel_event) -> CommandResult:
        return CommandResult(1, "", "tcpdump: /dev/bpf0: Permission denied")

    result = VlanDiscoveryService(privileged, capture).discover("en7", 2.0)

    assert result == [162, 192]
    assert len(calls) == 1
    assert "--vlan-discovery-worker" in calls[0]


def test_discovery_avoids_authorization_when_bpf_is_accessible() -> None:
    def privileged(command: tuple[str, ...], timeout: float) -> CommandResult:
        raise AssertionError("Privilege fallback must not run")

    def capture(command, timeout, output_callback, cancel_event) -> CommandResult:
        return CommandResult(124, "12:00:00 aa > bb, vlan 20, IPv4", "timed out")

    assert VlanDiscoveryService(privileged, capture).discover("en7", 2.0) == [20]
