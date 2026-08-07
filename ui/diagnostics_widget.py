"""
Version: 1.1.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Localize diagnostic headings, states, findings, and recommendations.
"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QGroupBox, QTableWidget, QTableWidgetItem, QVBoxLayout

from core.diagnostic_models import DiagnosticFinding, DiagnosticSeverity
from core.i18n import tr


class DiagnosticsWidget(QGroupBox):
    """Present probable causes and recommendations after diagnostic runs."""

    COLORS = {DiagnosticSeverity.INFO: QColor("#0a84ff"), DiagnosticSeverity.WARNING: QColor("#ffcc00"), DiagnosticSeverity.ERROR: QColor("#ff3b30")}

    def __init__(self) -> None:
        super().__init__(tr("Smart Diagnostics"))
        layout = QVBoxLayout(self)
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in ("Severity", "Finding", "Probable reason", "Recommendation", "Source")))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setMaximumHeight(210)
        layout.addWidget(self._table)

    def set_findings(self, findings: list[DiagnosticFinding]) -> None:
        """Replace displayed findings with the latest inference output."""
        self._table.setRowCount(max(1, len(findings)))
        if not findings:
            self._table.setItem(0, 0, QTableWidgetItem("OK"))
            self._table.setItem(0, 1, QTableWidgetItem(tr("No likely problems detected")))
            return
        for row, finding in enumerate(findings):
            values = tuple(tr(value) for value in (finding.severity.value, finding.title, finding.probable_reason, finding.recommendation, finding.source))
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setForeground(self.COLORS[finding.severity])
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()
