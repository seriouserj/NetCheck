"""
Version: 0.2.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add immutable Ethernet interface diagnostics model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InterfaceDiagnostics:
    """Current diagnostic state for one Ethernet-capable interface."""

    name: str
    status: str
    speed: str
    duplex: str
    mac: str
    ipv4: tuple[str, ...]
    ipv6: tuple[str, ...]
    gateway: str
    dns_servers: tuple[str, ...]
    internet: str
