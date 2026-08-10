"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add consistent whole-row hover feedback for diagnostic tables.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QModelIndex
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QTableWidget


class _HoverRowDelegate(QStyledItemDelegate):
    """Apply the hover state to every cell in the row under the pointer."""

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        super().initStyleOption(option, index)
        table = self.parent()
        if isinstance(table, HoverRowTableWidget) and index.row() == table.hovered_row:
            option.state |= QStyle.StateFlag.State_MouseOver


class HoverRowTableWidget(QTableWidget):
    """QTableWidget that highlights a complete row while it is hovered."""

    def __init__(self, rows: int, columns: int) -> None:
        super().__init__(rows, columns)
        self.hovered_row = -1
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.setItemDelegate(_HoverRowDelegate(self))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        row = self.indexAt(event.position().toPoint()).row()
        if row != self.hovered_row:
            self.hovered_row = row
            self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.hovered_row = -1
        self.viewport().update()
        super().leaveEvent(event)
