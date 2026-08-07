"""
Version: 0.10.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add tolerant tcpdump LLDP and CDP decoding.
"""

from __future__ import annotations

import re

from core.neighbor_models import NetworkNeighbor


def parse_lldp(output: str) -> NetworkNeighbor | None:
    """Parse verbose tcpdump LLDP TLV output."""
    if "LLDP" not in output.upper():
        return None
    return NetworkNeighbor(
        protocol="LLDP",
        system_name=_match(output, r"System Name TLV[^:]*:\s*([^\n]+)"),
        port_id=_match(output, r"Port ID TLV[^:]*:\s*(?:[^:]+:\s*)?([^\n]+)"),
        platform=_match(output, r"System Description TLV[^:]*:\s*([^\n]+)"),
        management_address=_match(output, r"Management Address TLV[^\n]*\n(?:.*\n)*?\s*(?:IPv4|Address)\s*:\s*([0-9a-fA-F:.]+)"),
        native_vlan=_match(output, r"(?:Port VLAN ID|PVID)[^:]*:\s*(\d+)"),
        capabilities=_match(output, r"System Capabilities TLV[^:]*:\s*([^\n]+)"),
    )


def parse_cdp(output: str) -> NetworkNeighbor | None:
    """Parse verbose tcpdump Cisco Discovery Protocol output."""
    if "CDP" not in output.upper():
        return None
    return NetworkNeighbor(
        protocol="CDP",
        system_name=_match(output, r"Device-ID[^:]*:\s*['\"]?([^'\"\n]+)"),
        port_id=_match(output, r"Port-ID[^:]*:\s*['\"]?([^'\"\n]+)"),
        platform=_match(output, r"Platform[^:]*:\s*['\"]?([^'\"\n]+)"),
        management_address=_match(output, r"IPv4[^0-9]*([0-9]+(?:\.[0-9]+){3})"),
        native_vlan=_match(output, r"Native VLAN[^:]*:\s*(\d+)"),
        capabilities=_match(output, r"Capabilities[^:]*:\s*([^\n]+)"),
    )


def _match(output: str, pattern: str) -> str:
    match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else "—"
