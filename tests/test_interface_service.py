"""
Version: 1.9.3
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify macOS physical-interface and configured-tunnel selection.
"""

import socket
from types import SimpleNamespace

from core.interface_service import _parse_windows_snapshot, _select_macos_devices


def test_parse_windows_network_snapshot() -> None:
    adapters, configurations = _parse_windows_snapshot(
        '{"Adapters":{"Name":"Ethernet","Status":"Up","LinkSpeed":"1 Gbps",'
        '"MacAddress":"00-11-22-33-44-55","FullDuplex":true},'
        '"Configs":{"Name":"Ethernet","Gateway":"192.168.1.1",'
        '"DNS":["192.168.1.1","1.1.1.1"]}}'
    )

    assert len(adapters) == 1
    assert adapters[0]["Name"] == "Ethernet"
    assert configurations["Ethernet"]["Gateway"] == "192.168.1.1"


def test_rejects_invalid_windows_network_snapshot() -> None:
    assert _parse_windows_snapshot("not JSON") == ((), {})


def test_selects_active_physical_interfaces_and_configured_tunnel() -> None:
    def address(family: object, value: str) -> SimpleNamespace:
        return SimpleNamespace(family=family, address=value)
    devices = _select_macos_devices(
        {"en0": "Ethernet", "en2": "USB 10/100/1000 LAN", "en3": "Thunderbolt Bridge"},
        {
            "en0": [address(socket.AF_INET, "192.168.50.24")],
            "en1": [address(socket.AF_INET, "192.168.50.107")],
            "en2": [address(socket.AF_INET6, "fe80::1%en2")],
            "utun0": [address(socket.AF_INET6, "fe80::2%utun0")],
            "utun3": [address(socket.AF_INET, "10.20.30.2")],
            "awdl0": [address(socket.AF_INET6, "fd00::1")],
        },
    )

    assert devices == ["en0", "en1", "en2", "utun3"]
