"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Derive the default discovery subnet on macOS and Windows.
"""

from __future__ import annotations

import ipaddress
import socket
import sys

import psutil

FALLBACK_SUBNET = "192.168.1.0/24"


def detect_default_subnet() -> str:
    """Prefer en0, then another active en interface, then the static fallback."""
    addresses = psutil.net_if_addrs()
    statistics = psutil.net_if_stats()
    ethernet_names = [name for name in addresses if _is_candidate(name)]
    ordered = sorted(
        ethernet_names,
        key=lambda name: (
            _preference(name),
            not bool(statistics.get(name) and statistics[name].isup),
            name,
        ),
    )
    for name in ordered:
        for address in addresses.get(name, []):
            if address.family != socket.AF_INET or not address.address:
                continue
            try:
                ip_address = ipaddress.ip_address(address.address)
                if ip_address.is_loopback or ip_address.is_link_local:
                    continue
                interface = ipaddress.ip_interface(
                    f"{address.address}/{address.netmask or '255.255.255.0'}"
                )
            except ValueError:
                continue
            return str(interface.network)
    return FALLBACK_SUBNET


def _preference(name: str) -> int:
    normalized = name.casefold()
    if name == "en0":
        return 0
    if sys.platform == "darwin":
        return 1
    if sys.platform == "win32":
        return 1 if "ethernet" in normalized else 2
    return 1


def _is_candidate(name: str) -> bool:
    normalized = name.casefold()
    if sys.platform == "darwin":
        return name.startswith("en")
    return not any(
        marker in normalized
        for marker in ("loopback", "bluetooth", "tunnel", "vethernet")
    )
