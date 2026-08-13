"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify Windows VLAN and packet-capture capability parsing.
"""

import json

from core.neighbor_parser import parse_lldp
from core.neighbor_service import parse_tshark_interface_id
from core.windows_vlan_capability import parse_vlan_driver_properties


def test_filters_windows_vlan_driver_properties() -> None:
    payload = json.dumps(
        [
            {"DisplayName": "VLAN ID", "DisplayValue": "20", "RegistryKeyword": "VlanID"},
            {"DisplayName": "Jumbo Packet", "DisplayValue": "Disabled", "RegistryKeyword": "*JumboPacket"},
        ]
    )
    properties = parse_vlan_driver_properties(payload)

    assert len(properties) == 1
    assert properties[0].registry_keyword == "VlanID"


def test_matches_windows_tshark_interface() -> None:
    output = "1. \\Device\\NPF_{A} (Ethernet)\n2. \\Device\\NPF_{B} (Wi-Fi)"
    assert parse_tshark_interface_id(output, "Ethernet") == "1"


def test_parses_windows_tshark_lldp_fields() -> None:
    output = """
Link Layer Discovery Protocol
    Port ID: GigabitEthernet1/0/1
    System Name: access-switch
    System Description: Cisco IOS
    System Capabilities: Bridge, Router
"""
    neighbor = parse_lldp(output)

    assert neighbor is not None
    assert neighbor.system_name == "access-switch"
    assert neighbor.port_id == "GigabitEthernet1/0/1"
