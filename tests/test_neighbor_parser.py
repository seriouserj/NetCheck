"""
Version: 1.9.2
Date: 2026-08-18
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify real tcpdump CDP metadata and multiple neighbor parsing.
"""

from core.neighbor_parser import parse_cdp, parse_lldp, parse_neighbors


def test_parse_lldp_neighbor() -> None:
    output = "LLDP, System Name TLV (5), length 7: switch1\nPort ID TLV (2), length 5: Interface Name: Gi1/0/1\nPort VLAN ID: 20"
    neighbor = parse_lldp(output)
    assert neighbor is not None
    assert neighbor.system_name == "switch1"
    assert neighbor.native_vlan == "20"


def test_parse_cdp_neighbor() -> None:
    output = "CDP v2, Device-ID (0x01), length: 'core-sw'\nPort-ID (0x03), length: 'Gi0/24'\nNative VLAN: 100"
    neighbor = parse_cdp(output)
    assert neighbor is not None
    assert neighbor.system_name == "core-sw"


def test_parse_cdp_tcpdump_length_metadata() -> None:
    output = (
        "CDPv2, ttl: 180s\n"
        "Device-ID (0x01), length: 16 bytes: CORE-SWITCH-01\n"
        "Port-ID (0x03), length: 8 bytes: Gi1/0/48\n"
        "Platform (0x06), length: 4 bytes: cisco\n"
        "Capabilities (0x04), length: 6 bytes: Router Switch\n"
    )

    neighbor = parse_cdp(output)

    assert neighbor is not None
    assert neighbor.system_name == "CORE-SWITCH-01"
    assert neighbor.port_id == "Gi1/0/48"
    assert neighbor.platform == "cisco"


def test_parse_multiple_cdp_neighbors() -> None:
    output = (
        "12:00:00 aa > bb, CDPv2, ttl: 180s\n"
        "    Device-ID (0x01), length: 8 bytes: switch-a\n"
        "    Port-ID (0x03), length: 7 bytes: Gi1/0/1\n"
        "12:00:01 cc > bb, CDPv2, ttl: 180s\n"
        "    Device-ID (0x01), length: 8 bytes: switch-b\n"
        "    Port-ID (0x03), length: 7 bytes: Gi1/0/2\n"
    )

    neighbors = parse_neighbors(output)

    assert [neighbor.system_name for neighbor in neighbors] == ["switch-a", "switch-b"]
