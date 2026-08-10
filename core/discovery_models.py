"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Include NetBIOS identity in discovered host results.
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
    netbios_info: str = "—"
