"""
Version: 0.6.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add Wake-on-LAN magic packet transmission.
"""

from __future__ import annotations

import re
import socket


def normalize_mac_address(value: str) -> str:
    """Validate and normalize a six-byte MAC address."""
    compact = re.sub(r"[:-]", "", value.strip())
    if not re.fullmatch(r"[0-9a-fA-F]{12}", compact):
        raise ValueError("Enter a valid MAC address, for example AA:BB:CC:DD:EE:FF.")
    return compact.lower()


def send_magic_packet(mac_address: str, broadcast: str = "255.255.255.255", port: int = 9) -> str:
    """Send a standard Wake-on-LAN magic packet over UDP broadcast."""
    normalized = normalize_mac_address(mac_address)
    try:
        socket.inet_aton(broadcast)
    except OSError as error:
        raise ValueError("Enter a valid IPv4 broadcast address.") from error
    payload = b"\xff" * 6 + bytes.fromhex(normalized) * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        connection.sendto(payload, (broadcast, port))
    formatted = ":".join(normalized[index:index + 2] for index in range(0, 12, 2))
    return f"Magic packet sent to {formatted} via {broadcast}:{port}."
