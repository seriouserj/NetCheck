"""
Version: 0.3.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add VLAN test state and result models.
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
