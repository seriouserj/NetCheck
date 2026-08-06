"""
Version: 0.2.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify macOS network command parsing.
"""

from core.network_parsers import (
    is_ethernet_port,
    parse_default_gateway,
    parse_dns_servers,
    parse_hardware_ports,
    parse_media,
)


def test_parse_hardware_ports() -> None:
    output = """Hardware Port: USB 10/100/1000 LAN
Device: en7
Ethernet Address: aa:bb:cc:dd:ee:ff

Hardware Port: Wi-Fi
Device: en0
Ethernet Address: 00:11:22:33:44:55"""
    assert parse_hardware_ports(output) == {"en7": "USB 10/100/1000 LAN", "en0": "Wi-Fi"}
    assert is_ethernet_port("USB 10/100/1000 LAN")
    assert not is_ethernet_port("Wi-Fi")


def test_parse_media_and_status() -> None:
    output = "media: autoselect (1000baseT <full-duplex>)\n\tstatus: active"
    assert parse_media(output) == ("1000 Mbps", "Full", True)


def test_parse_route_and_dns() -> None:
    route = "   gateway: 192.168.1.1\n interface: en7"
    dns = "nameserver[0] : 1.1.1.1\nnameserver[1] : 2606:4700:4700::1111\nnameserver[2] : invalid"
    assert parse_default_gateway(route) == ("192.168.1.1", "en7")
    assert parse_dns_servers(dns) == ("1.1.1.1", "2606:4700:4700::1111")
