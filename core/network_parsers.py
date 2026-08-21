"""
Version: 1.9.4
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Parse Wi-Fi device identities from the macOS system profile.
"""

from __future__ import annotations

import ipaddress
import json
import re

_HARDWARE_PORT_PATTERN = re.compile(
    r"Hardware Port:\s*(?P<port>.+?)\nDevice:\s*(?P<device>\S+)", re.MULTILINE
)
_MEDIA_PATTERN = re.compile(r"media:\s*.+?\((?P<media>[^)]+)\)", re.IGNORECASE)


def parse_hardware_ports(output: str) -> dict[str, str]:
    """Return device-to-service labels from networksetup output."""
    return {
        match.group("device"): match.group("port").strip()
        for match in _HARDWARE_PORT_PATTERN.finditer(output)
    }


def parse_wifi_interfaces(output: str) -> set[str]:
    """Return Wi-Fi BSD device names from a system_profiler JSON snapshot."""
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        return set()
    devices: set[str] = set()
    for section in payload.get("SPAirPortDataType", []):
        if not isinstance(section, dict):
            continue
        for interface in section.get("spairport_airport_interfaces", []):
            if isinstance(interface, dict) and interface.get("_name"):
                devices.add(str(interface["_name"]))
    return devices


def is_ethernet_port(label: str) -> bool:
    """Identify wired network services while excluding wireless devices."""
    normalized = label.casefold()
    if "bridge" in normalized:
        return False
    return (
        "ethernet" in normalized
        or "usb lan" in normalized
        or normalized.endswith(" lan")
    )


def parse_media(output: str) -> tuple[str, str, bool]:
    """Extract link speed, duplex, and active status from ifconfig output."""
    active = bool(re.search(r"status:\s*active", output, re.IGNORECASE))
    match = _MEDIA_PATTERN.search(output)
    if not match:
        return "Unknown", "Unknown", active
    media = match.group("media")
    speed_match = re.search(r"(\d+(?:\.\d+)?)([KMG]?)base", media, re.IGNORECASE)
    speed = "Unknown"
    if speed_match:
        unit = speed_match.group(2).upper()
        suffix = {"G": "Gbps", "M": "Mbps", "K": "Kbps", "": "Mbps"}[unit]
        speed = f"{speed_match.group(1)} {suffix}"
    duplex = "Full" if "full-duplex" in media.casefold() else "Half" if "half-duplex" in media.casefold() else "Unknown"
    return speed, duplex, active


def parse_ifconfig_addresses(output: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """Return normalized interface addresses from macOS ifconfig output."""
    mac_match = re.search(r"^\s*ether\s+([0-9a-f:]{17})\s*$", output, re.MULTILINE | re.IGNORECASE)
    ipv4 = tuple(
        dict.fromkeys(
            re.findall(r"^\s*inet\s+(\d+(?:\.\d+){3})\b", output, re.MULTILINE)
        )
    )
    ipv6 = tuple(
        dict.fromkeys(
            address.split("%", 1)[0]
            for address in re.findall(r"^\s*inet6\s+(\S+)", output, re.MULTILINE)
        )
    )
    return (mac_match.group(1).lower() if mac_match else "", ipv4, ipv6)


def parse_default_gateway(output: str) -> tuple[str, str]:
    """Return gateway and interface from macOS route output."""
    gateway = re.search(r"^\s*gateway:\s*(\S+)", output, re.MULTILINE)
    interface = re.search(r"^\s*interface:\s*(\S+)", output, re.MULTILINE)
    return (gateway.group(1) if gateway else "", interface.group(1) if interface else "")


def parse_dns_servers(output: str) -> tuple[str, ...]:
    """Return unique valid IP addresses from scutil DNS resolver output."""
    servers: list[str] = []
    for candidate in re.findall(r"nameserver\[\d+\]\s*:\s*(\S+)", output):
        try:
            normalized = str(ipaddress.ip_address(candidate))
        except ValueError:
            continue
        if normalized not in servers:
            servers.append(normalized)
    return tuple(servers)
