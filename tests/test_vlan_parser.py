"""
Version: 0.3.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify VLAN input validation and device parsing.
"""

import pytest

from core.vlan_parser import parse_vlan_devices, parse_vlan_ids


def test_parse_vlan_ids_deduplicates_and_sorts() -> None:
    assert parse_vlan_ids("20, 1-3, 2, 4094") == (1, 2, 3, 20, 4094)


@pytest.mark.parametrize("expression", ["", "0", "4095", "10-2", "1,,2", "abc"])
def test_parse_vlan_ids_rejects_invalid_input(expression: str) -> None:
    with pytest.raises(ValueError):
        parse_vlan_ids(expression)


def test_parse_vlan_devices() -> None:
    output = "VLAN Name: NetCheck VLAN 20\nDevice: vlan0\nParent Device: en7\nTag: 20"
    assert parse_vlan_devices(output) == {("en7", 20): "vlan0"}
