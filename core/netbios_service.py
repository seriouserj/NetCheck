"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add dependency-free NetBIOS node-status discovery over UDP/137.
"""

from __future__ import annotations

import secrets
import socket
import struct
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NetBiosInfo:
    """Primary workstation and workgroup names from an NBSTAT response."""

    hostname: str = ""
    workgroup: str = ""

    @property
    def display_name(self) -> str:
        """Return a compact Angry IP Scanner-like identity string."""
        if self.workgroup and self.hostname:
            return f"{self.workgroup}\\{self.hostname}"
        return self.hostname or self.workgroup or "—"


def query_netbios_node_status(address: str, timeout: float = 0.4) -> NetBiosInfo:
    """Request a NetBIOS node-status table from one IPv4 host."""
    transaction_id = secrets.randbits(16)
    query = build_node_status_query(transaction_id)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.settimeout(max(0.1, timeout))
            connection.sendto(query, (address, 137))
            response, _ = connection.recvfrom(4096)
    except OSError:
        return NetBiosInfo()
    return parse_node_status_response(response, transaction_id)


def build_node_status_query(transaction_id: int) -> bytes:
    """Build an RFC 1002 NBSTAT query for the wildcard NetBIOS name."""
    wildcard = b"*" + (b"\x00" * 15)
    encoded = bytearray()
    for value in wildcard:
        encoded.extend((ord("A") + (value >> 4), ord("A") + (value & 0x0F)))
    header = struct.pack("!HHHHHH", transaction_id & 0xFFFF, 0, 1, 0, 0, 0)
    question = bytes((len(encoded),)) + bytes(encoded) + b"\x00" + struct.pack("!HH", 0x21, 1)
    return header + question


def parse_node_status_response(packet: bytes, transaction_id: int | None = None) -> NetBiosInfo:
    """Parse workstation and workgroup names from an NBSTAT response."""
    if len(packet) < 12:
        return NetBiosInfo()
    response_id, flags, questions, answers, authorities, additionals = struct.unpack_from(
        "!HHHHHH", packet, 0
    )
    if transaction_id is not None and response_id != transaction_id:
        return NetBiosInfo()
    if not flags & 0x8000:
        return NetBiosInfo()
    offset = 12
    try:
        for _ in range(questions):
            offset = _skip_dns_name(packet, offset) + 4
        for _ in range(answers + authorities + additionals):
            offset = _skip_dns_name(packet, offset)
            record_type, _, _, data_length = struct.unpack_from("!HHIH", packet, offset)
            offset += 10
            record_data = packet[offset : offset + data_length]
            offset += data_length
            if record_type == 0x21:
                return _parse_node_status_names(record_data)
    except (IndexError, struct.error, ValueError):
        return NetBiosInfo()
    return NetBiosInfo()


def _skip_dns_name(packet: bytes, offset: int) -> int:
    while True:
        length = packet[offset]
        if length & 0xC0 == 0xC0:
            return offset + 2
        offset += 1
        if length == 0:
            return offset
        offset += length
        if offset > len(packet):
            raise ValueError("truncated encoded name")


def _parse_node_status_names(data: bytes) -> NetBiosInfo:
    if not data:
        return NetBiosInfo()
    hostname = ""
    workgroup = ""
    count = data[0]
    for index in range(count):
        start = 1 + (index * 18)
        if start + 18 > len(data):
            break
        name = data[start : start + 15].decode("ascii", errors="ignore").strip()
        suffix = data[start + 15]
        flags = struct.unpack_from("!H", data, start + 16)[0]
        is_group = bool(flags & 0x8000)
        if name and not is_group and suffix in (0x00, 0x20) and not hostname:
            hostname = name
        if name and is_group and suffix in (0x00, 0x1E) and not workgroup:
            workgroup = name
    return NetBiosInfo(hostname, workgroup)
