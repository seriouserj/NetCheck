"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Export diagnostic tables to TXT, PDF, and SVG reports.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QPdfWriter, QTextDocument
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QWidget

from core.i18n import tr
from core.tabular_report import report_as_html, report_as_tsv
from ui.hover_table import HoverRowTableWidget


class ReportExportBar(QWidget):
    """Offer copy and explicit TXT/PDF/SVG export actions for a table."""

    def __init__(self, table: HoverRowTableWidget, title: str) -> None:
        super().__init__()
        self._table = table
        self._title = title
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        copy = QPushButton(tr("Copy"))
        copy.clicked.connect(table.copy_all)
        layout.addWidget(copy)
        for file_type in ("TXT", "PDF", "SVG"):
            button = QPushButton(file_type)
            button.setToolTip(tr("Export report as {format}", format=file_type))
            button.clicked.connect(lambda checked=False, kind=file_type: self._save(kind.lower()))
            layout.addWidget(button)

    def _save(self, kind: str) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("Export report"),
            f"NetCheck-report.{kind}",
            f"{kind.upper()} (*.{kind})",
        )
        if not path:
            return
        destination = Path(path)
        if destination.suffix.lower() != f".{kind}":
            destination = destination.with_suffix(f".{kind}")
        try:
            headers, rows = _table_data(self._table)
            if kind == "txt":
                destination.write_text(report_as_tsv(headers, rows) + "\n", encoding="utf-8")
            elif kind == "pdf":
                _write_pdf(destination, self._title, headers, rows)
            else:
                _write_svg(destination, self._title, headers, rows)
        except OSError as error:
            QMessageBox.warning(self, tr("Export failed"), str(error))


def _table_data(table: HoverRowTableWidget) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    headers = tuple(
        table.horizontalHeaderItem(column).text() if table.horizontalHeaderItem(column) else ""
        for column in range(table.columnCount())
    )
    rows = tuple(
        tuple(
            table.item(row, column).text() if table.item(row, column) else ""
            for column in range(table.columnCount())
        )
        for row in range(table.rowCount())
    )
    return headers, rows


def _write_pdf(path: Path, title: str, headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> None:
    writer = QPdfWriter(str(path))
    writer.setTitle(title)
    writer.setCreator("NetCheck")
    document = QTextDocument()
    document.setHtml(report_as_html(title, headers, rows))
    document.print_(writer)


def _write_svg(path: Path, title: str, headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> None:
    generator = QSvgGenerator()
    generator.setFileName(str(path))
    generator.setTitle(title)
    generator.setDescription("NetCheck vector diagnostic report")
    generator.setSize(QSize(1800, max(500, 120 + len(rows) * 42)))
    document = QTextDocument()
    document.setHtml(report_as_html(title, headers, rows))
    document.setTextWidth(1760)
    painter = QPainter(generator)
    document.drawContents(painter)
    painter.end()
