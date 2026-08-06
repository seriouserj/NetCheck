"""
Version: 0.4.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add subnet, ping, and ARP parsing for discovery.
"""

from __future__ import annotations

import ipaddress
import re


def parse_scan_network(value: str, maximum_hosts: int = 1024) -> ipaddress.IPv4Network:
    """Validate an IPv4 subnet and constrain active scan size."""
    try:
        network = ipaddress.ip_network(value.strip(), strict=False)
    except ValueError as error:
        raise ValueError("Enter a valid IPv4 subnet, for example 192.168.1.0/24.") from error
    if not isinstance(network, ipaddress.IPv4Network):
        raise ValueError("Discovery currently supports IPv4 subnets only.")
    if network.prefixlen > 30:
        raise ValueError("Discovery requires a subnet containing usable host addresses.")
    if network.num_addresses - 2 > maximum_hosts:
        raise ValueError(f"Subnet is too large for one scan; use {maximum_hosts} hosts or fewer.")
    return network


def parse_ping_latency(output: str) -> float | None:
    """Extract a millisecond round-trip time from macOS ping output."""
    match = re.search(r"time[=<]([0-9.]+)\s*ms", output)
    return float(match.group(1)) if match else None


def parse_arp_mac(output: str) -> str:
    """Extract and normalize a MAC address from macOS arp output."""
    match = re.search(r"\bat\s+([0-9a-f]{1,2}(?::[0-9a-f]{1,2}){5})\b", output, re.IGNORECASE)
    if not match:
        return ""
    return ":".join(part.zfill(2) for part in match.group(1).lower().split(":"))
