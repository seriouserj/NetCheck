"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add data-aware table items for correct IP and numeric sorting.
"""

from __future__ import annotations

import ipaddress

from PySide6.QtWidgets import QTableWidgetItem


class IpAddressItem(QTableWidgetItem):
    """Sort IP address cells by their numeric value instead of text."""

    def __init__(self, value: str) -> None:
        super().__init__(value)
        self._sort_value = int(ipaddress.ip_address(value))

    def __lt__(self, other: QTableWidgetItem) -> bool:
        if isinstance(other, IpAddressItem):
            return self._sort_value < other._sort_value
        return super().__lt__(other)


class NumericItem(QTableWidgetItem):
    """Sort formatted numeric cells by their underlying number."""

    def __init__(self, text: str, value: float) -> None:
        super().__init__(text)
        self._sort_value = value

    def __lt__(self, other: QTableWidgetItem) -> bool:
        if isinstance(other, NumericItem):
            return self._sort_value < other._sort_value
        return super().__lt__(other)
