"""
Version: 1.9.4
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Describe the hardware role of every network interface.
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
    interface_type: str = "Network"
    hardware_port: str = ""


@dataclass(frozen=True, slots=True)
class InterfaceChoice:
    """Stable system name and human-readable hardware identity for a selector."""

    name: str
    interface_type: str
    hardware_port: str = ""
