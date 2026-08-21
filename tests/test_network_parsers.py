"""
Version: 1.9.4
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify macOS address and Wi-Fi identity parsers.
"""

from core.network_parsers import (
    is_ethernet_port,
    parse_default_gateway,
    parse_dns_servers,
    parse_hardware_ports,
    parse_ifconfig_addresses,
    parse_media,
    parse_wifi_interfaces,
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
    assert not is_ethernet_port("Thunderbolt Bridge")
    assert is_ethernet_port("Thunderbolt Ethernet")


def test_parse_media_and_status() -> None:
    output = "media: autoselect (1000baseT <full-duplex>)\n\tstatus: active"
    assert parse_media(output) == ("1000 Mbps", "Full", True)


def test_parse_wifi_interfaces() -> None:
    output = '{"SPAirPortDataType":[{"spairport_airport_interfaces":[{"_name":"en1"}]}]}'

    assert parse_wifi_interfaces(output) == {"en1"}
    assert parse_wifi_interfaces("not json") == set()


def test_parse_ifconfig_addresses() -> None:
    output = """
en7: flags=8863<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500
    ether 00:e0:4c:68:16:c0
    inet6 fe80::8b8:c628:7390:87bf%en7 prefixlen 64 secured scopeid 0x17
    inet 192.168.10.103 netmask 0xffffff00 broadcast 192.168.10.255
"""
    assert parse_ifconfig_addresses(output) == (
        "00:e0:4c:68:16:c0",
        ("192.168.10.103",),
        ("fe80::8b8:c628:7390:87bf",),
    )


def test_parse_route_and_dns() -> None:
    route = "   gateway: 192.168.1.1\n interface: en7"
    dns = "nameserver[0] : 1.1.1.1\nnameserver[1] : 2606:4700:4700::1111\nnameserver[2] : invalid"
    assert parse_default_gateway(route) == ("192.168.1.1", "en7")
    assert parse_dns_servers(dns) == ("1.1.1.1", "2606:4700:4700::1111")
