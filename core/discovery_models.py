"""
Version: 0.4.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add immutable network host discovery model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiscoveredHost:
    """One host observed during an active local network scan."""

    hostname: str
    ip_address: str
    mac_address: str
    vendor: str
    latency_ms: float
