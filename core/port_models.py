"""
Version: 0.5.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add TCP port scan result models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PortState(str, Enum):
    """Observable TCP connect-scan state."""

    OPEN = "Open"
    CLOSED = "Closed"
    FILTERED = "Filtered"


@dataclass(frozen=True, slots=True)
class PortScanResult:
    """Result for one TCP port on a resolved target."""

    port: int
    state: PortState
    service: str
    latency_ms: float | None
