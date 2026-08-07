"""
Version: 1.1.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add safe JSON serialization for the privileged VLAN batch worker.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CheckState(str, Enum):
    """Normalized health state for a diagnostic check."""

    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class VlanTestResult:
    """Complete result for one temporary VLAN interface."""

    vlan_id: int
    link: CheckState
    dhcp: CheckState
    gateway: CheckState
    dns: CheckState
    internet: CheckState
    ping: CheckState
    lldp: CheckState
    address: str = ""
    gateway_address: str = ""
    detail: str = ""

    def to_payload(self) -> dict[str, object]:
        """Return a JSON-safe representation for process communication."""
        return {
            "vlan_id": self.vlan_id,
            "link": self.link.value,
            "dhcp": self.dhcp.value,
            "gateway": self.gateway.value,
            "dns": self.dns.value,
            "internet": self.internet.value,
            "ping": self.ping.value,
            "lldp": self.lldp.value,
            "address": self.address,
            "gateway_address": self.gateway_address,
            "detail": self.detail,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> VlanTestResult:
        """Validate and restore a result returned by the privileged worker."""
        return cls(
            vlan_id=int(payload["vlan_id"]),
            link=CheckState(str(payload["link"])),
            dhcp=CheckState(str(payload["dhcp"])),
            gateway=CheckState(str(payload["gateway"])),
            dns=CheckState(str(payload["dns"])),
            internet=CheckState(str(payload["internet"])),
            ping=CheckState(str(payload["ping"])),
            lldp=CheckState(str(payload["lldp"])),
            address=str(payload.get("address", "")),
            gateway_address=str(payload.get("gateway_address", "")),
            detail=str(payload.get("detail", "")),
        )
