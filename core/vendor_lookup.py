"""
Version: 0.4.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add offline MAC manufacturer lookup using the packaged manuf database.
"""

from __future__ import annotations

from typing import Any


class VendorLookup:
    """Resolve MAC manufacturers without sending network inventory externally."""

    def __init__(self) -> None:
        self._parser: Any | None = None
        try:
            from manuf import manuf

            self._parser = manuf.MacParser(update=False)
        except (ImportError, OSError, ValueError):
            self._parser = None

    def resolve(self, mac_address: str) -> str:
        """Return a manufacturer label or a stable unknown value."""
        if not mac_address or self._parser is None:
            return "Unknown"
        try:
            return self._parser.get_manuf_long(mac_address) or self._parser.get_manuf(mac_address) or "Unknown"
        except (KeyError, TypeError, ValueError):
            return "Unknown"
