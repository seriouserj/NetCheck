"""
Version: 0.10.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify LLDP and CDP tcpdump parsing.
"""

from core.neighbor_parser import parse_cdp, parse_lldp


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
