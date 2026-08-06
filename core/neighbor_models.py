"""
Version: 0.10.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add link-layer neighbor discovery model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NetworkNeighbor:
    """Switch or router advertised through LLDP or CDP."""

    protocol: str
    system_name: str
    port_id: str
    platform: str
    management_address: str
    native_vlan: str
    capabilities: str
