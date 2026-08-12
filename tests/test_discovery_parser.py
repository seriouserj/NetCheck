"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify macOS and Windows discovery parsing.
"""

import pytest

from core.discovery_parser import (
    parse_arp_mac,
    parse_cached_hostname,
    parse_ping_latency,
    parse_scan_network,
)


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


def test_parse_windows_ping_and_arp_output() -> None:
    assert parse_ping_latency("Reply from 192.0.2.1: bytes=32 time<1ms TTL=128") == 1.0
    assert parse_ping_latency("Antwort von 192.0.2.1: Bytes=32 Zeit=4ms TTL=128") == 4.0
    assert parse_arp_mac("  192.0.2.1          0-a-b-c-d-e           dynamic") == "00:0a:0b:0c:0d:0e"


def test_parse_cached_hostname() -> None:
    assert parse_cached_hostname("name: printer-office.local.\nip_address: 192.0.2.20") == "printer-office.local"
    assert parse_cached_hostname("No entry found") == ""
