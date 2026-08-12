"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify Windows PowerShell adapter snapshot parsing.
"""

from core.interface_service import _parse_windows_snapshot


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
