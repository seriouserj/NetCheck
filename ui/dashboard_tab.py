"""
Version: 1.9.3
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Present physical and active VPN interfaces without false tunnel diagnostics.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.diagnostic_engine import DiagnosticEngine
from core.i18n import tr
from core.interface_models import InterfaceDiagnostics
from core.interface_service import InterfaceService
from ui.async_task import BackgroundTask
from ui.diagnostics_widget import DiagnosticsWidget
from ui.hover_table import HoverRowTableWidget


class DashboardTab(QWidget):
    """Display a live summary of local physical and VPN network interfaces."""

    HEADERS = ("Interface", "Status", "Speed", "Duplex", "MAC", "IPv4", "IPv6", "Gateway", "DNS", "Internet")

    def __init__(self, service: InterfaceService | None = None) -> None:
        super().__init__()
        self._service = service or InterfaceService()
        self._diagnostic_engine = DiagnosticEngine()
        self._pool = QThreadPool.globalInstance()
        self._active_task: BackgroundTask | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel(tr("Dashboard"))
        title.setObjectName("sectionTitle")
        self._status = QLabel(tr("Ready"))
        self._status.setObjectName("mutedLabel")
        self._refresh = QPushButton(tr("Refresh"))
        self._refresh.clicked.connect(self.refresh)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._status)
        header.addWidget(self._refresh)

        self._table = HoverRowTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in self.HEADERS))
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSortingEnabled(True)

        layout.addLayout(header)
        layout.addWidget(self._table)
        self._diagnostics = DiagnosticsWidget()
        layout.addWidget(self._diagnostics)

    def refresh(self) -> None:
        """Refresh interface data in a worker thread."""
        if self._active_task is not None:
            return
        self._refresh.setEnabled(False)
        self._status.setText(tr("Scanning network interfaces…"))
        task = BackgroundTask(self._service.collect)
        task.signals.completed.connect(self._display_results)
        task.signals.failed.connect(self._display_error)
        self._active_task = task
        self._pool.start(task)

    def _display_results(self, diagnostics: object) -> None:
        rows = list(diagnostics) if isinstance(diagnostics, list) else []
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(rows))
        for row_index, interface in enumerate(rows):
            if isinstance(interface, InterfaceDiagnostics):
                self._populate_row(row_index, interface)
        self._table.resizeColumnsToContents()
        self._table.setSortingEnabled(True)
        self._status.setText(tr("{count} network interface(s)", count=len(rows)))
        typed_rows = [
            item
            for item in rows
            if isinstance(item, InterfaceDiagnostics)
            and not item.name.startswith(("utun", "wg"))
        ]
        self._diagnostics.set_findings(self._diagnostic_engine.analyze_interfaces(typed_rows))
        self._finish_refresh()

    def _populate_row(self, row: int, interface: InterfaceDiagnostics) -> None:
        values = (
            interface.name,
            tr(interface.status),
            interface.speed,
            interface.duplex,
            interface.mac,
            "\n".join(interface.ipv4) or "—",
            "\n".join(interface.ipv6) or "—",
            interface.gateway,
            ", ".join(interface.dns_servers) or "—",
            tr(interface.internet),
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self._table.setItem(row, column, item)

    def _display_error(self, message: str) -> None:
        self._status.setText(f"Refresh failed: {message}")
        self._finish_refresh()

    def _finish_refresh(self) -> None:
        self._active_task = None
        self._refresh.setEnabled(True)
