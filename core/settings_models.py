"""
Version: 0.7.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add validated immutable application settings model.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from enum import Enum


class ThemePreference(str, Enum):
    """Supported application appearance preferences."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True, slots=True)
class AppSettings:
    """User-configurable defaults shared by diagnostic modules."""

    timeout_seconds: float = 3.0
    preferred_dns: str = ""
    default_interface: str = ""
    theme: ThemePreference = ThemePreference.SYSTEM

    def validate(self) -> AppSettings:
        """Return this instance after enforcing supported values."""
        if not 0.1 <= self.timeout_seconds <= 120.0:
            raise ValueError("Timeout must be between 0.1 and 120 seconds.")
        if self.preferred_dns:
            try:
                ipaddress.ip_address(self.preferred_dns)
            except ValueError as error:
                raise ValueError("Preferred DNS must be a valid IPv4 or IPv6 address.") from error
        return self
