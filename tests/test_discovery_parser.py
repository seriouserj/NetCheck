"""
Version: 0.4.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify discovery input and system output parsers.
"""

import pytest

from core.discovery_parser import parse_arp_mac, parse_ping_latency, parse_scan_network


def test_parse_scan_network_normalizes_host_address() -> None:
    assert str(parse_scan_network("192.168.10.25/24")) == "192.168.10.0/24"


def test_parse_scan_network_rejects_large_or_ipv6_ranges() -> None:
    with pytest.raises(ValueError):
        parse_scan_network("10.0.0.0/8")
    with pytest.raises(ValueError):
        parse_scan_network("2001:db8::/64")


def test_parse_ping_and_arp_output() -> None:
    assert parse_ping_latency("64 bytes from 192.0.2.1: time=1.247 ms") == 1.247
    assert parse_arp_mac("host (192.0.2.1) at a:b:c:d:e:f on en7") == "0a:0b:0c:0d:0e:0f"
