"""
Version: 1.6.2
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Copy an individual result value immediately when its cell is clicked.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QModelIndex, QPoint, Qt
from PySide6.QtGui import QCursor, QKeyEvent, QKeySequence, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QToolTip,
)

from core.i18n import tr


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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_copy_menu)
        self.cellClicked.connect(self._copy_clicked_cell)

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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Copy selected cells using the platform-standard shortcut."""
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selected_cells()
            return
        super().keyPressEvent(event)

    def copy_selected_cells(self) -> None:
        """Copy selected cells as tab-separated rows."""
        indexes = sorted(self.selectedIndexes(), key=lambda index: (index.row(), index.column()))
        if not indexes:
            return
        rows: dict[int, dict[int, str]] = {}
        for index in indexes:
            item = self.item(index.row(), index.column())
            rows.setdefault(index.row(), {})[index.column()] = item.text() if item else ""
        first_column = min(index.column() for index in indexes)
        last_column = max(index.column() for index in indexes)
        text = "\n".join(
            "\t".join(cells.get(column, "") for column in range(first_column, last_column + 1))
            for cells in rows.values()
        )
        QApplication.clipboard().setText(text)

    def copy_all(self) -> None:
        """Copy column headings and the entire table as TSV."""
        QApplication.clipboard().setText(self.as_tsv())

    def _copy_clicked_cell(self, row: int, column: int) -> None:
        """Copy one clicked value and show brief, non-blocking feedback."""
        item = self.item(row, column)
        if item is None or not item.text():
            return
        QApplication.clipboard().setText(item.text())
        QToolTip.showText(QCursor.pos(), tr("Copied: {value}", value=item.text()), self)

    def as_tsv(self) -> str:
        """Serialize visible table data to tab-separated text."""
        headers = [self.horizontalHeaderItem(column) for column in range(self.columnCount())]
        lines = ["\t".join(item.text() if item else "" for item in headers)]
        for row in range(self.rowCount()):
            lines.append(
                "\t".join(
                    self.item(row, column).text() if self.item(row, column) else ""
                    for column in range(self.columnCount())
                )
            )
        return "\n".join(lines)

    def _show_copy_menu(self, position: QPoint) -> None:
        menu = QMenu(self)
        cell = self.itemAt(position)
        copy_cell = menu.addAction(tr("Copy cell"))
        copy_cell.setEnabled(cell is not None)
        copy_selection = menu.addAction(tr("Copy selection"))
        copy_all = menu.addAction(tr("Copy entire table"))
        chosen = menu.exec(self.viewport().mapToGlobal(position))
        if chosen is copy_cell and cell is not None:
            QApplication.clipboard().setText(cell.text())
        elif chosen is copy_selection:
            self.copy_selected_cells()
        elif chosen is copy_all:
            self.copy_all()
