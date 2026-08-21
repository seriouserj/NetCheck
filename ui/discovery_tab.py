"""
Version: 1.9.7
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add responsive hosts to the report while discovery is still running.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.discovery_models import DiscoveredHost
from core.discovery_parser import parse_scan_network
from core.discovery_service import DiscoveryService
from core.i18n import tr
from core.network_defaults import FALLBACK_SUBNET, detect_default_subnet
from ui.action_icons import decorate_action
from ui.async_task import BackgroundTask
from ui.hover_table import HoverRowTableWidget
from ui.report_export import ReportExportBar
from ui.sortable_items import IpAddressItem, NumericItem


class DiscoveryTab(QWidget):
    """Scan and display responsive hosts on a selected IPv4 subnet."""

    host_found = Signal(object)

    HEADERS = ("IP", "MAC", "Latency", "Hostname", "NetBIOS Info", "Vendor")

    def __init__(self) -> None:
        super().__init__()
        self._service = DiscoveryService()
        self._task: BackgroundTask | None = None
        self._subnet_was_edited = False
        self._displayed_addresses: set[str] = set()
        self._scan_host_count = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        controls = QHBoxLayout()
        controls.addWidget(QLabel(tr("Subnet")))
        self._subnet = QLineEdit(detect_default_subnet())
        self._subnet.setPlaceholderText(FALLBACK_SUBNET)
        self._subnet.textEdited.connect(lambda: setattr(self, "_subnet_was_edited", True))
        self._subnet.returnPressed.connect(self._start_scan)
        self._scan = QPushButton(tr("Scan"))
        self._scan.setObjectName("scanButton")
        self._scan.setProperty("primary", True)
        decorate_action(self._scan, "scan", primary=True)
        self._scan.clicked.connect(self._start_scan)
        controls.addWidget(self._subnet, 1)
        controls.addWidget(self._scan)
        self._status = QLabel(tr("Ready"))
        self._status.setObjectName("mutedLabel")
        self._table = HoverRowTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in self.HEADERS))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(controls)
        status_row = QHBoxLayout()
        status_row.addWidget(self._status)
        status_row.addWidget(ReportExportBar(self._table, tr("Network discovery report")), 1)
        layout.addLayout(status_row)
        layout.addWidget(self._table)
        self.host_found.connect(self._append_host)

    def showEvent(self, event: QShowEvent) -> None:
        """Refresh the suggested subnet until the user edits it manually."""
        if not self._subnet_was_edited:
            self._subnet.setText(detect_default_subnet())
        super().showEvent(event)

    def _start_scan(self) -> None:
        try:
            network = parse_scan_network(self._subnet.text())
        except ValueError as error:
            QMessageBox.warning(self, tr("Invalid subnet"), str(error))
            return
        self._scan.setEnabled(False)
        self._scan_host_count = max(0, network.num_addresses - 2)
        self._displayed_addresses.clear()
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        self._status.setText(tr("Scanning {count} possible host(s)…", count=self._scan_host_count))
        self._task = BackgroundTask(
            lambda: self._service.scan(network, progress=self.host_found.emit)
        )
        self._task.signals.completed.connect(self._show_results)
        self._task.signals.failed.connect(self._show_error)
        QThreadPool.globalInstance().start(self._task)

    def _show_results(self, value: object) -> None:
        hosts = value if isinstance(value, list) else []
        for host in hosts:
            self._append_host(host)
        self._table.setSortingEnabled(True)
        self._table.sortItems(0, Qt.SortOrder.AscendingOrder)
        self._table.resizeColumnsToContents()
        self._status.setText(tr("Found {count} responsive host(s)", count=len(hosts)))
        self._finish()

    def _append_host(self, value: object) -> None:
        if not isinstance(value, DiscoveredHost) or value.ip_address in self._displayed_addresses:
            return
        row = self._table.rowCount()
        self._table.insertRow(row)
        for column, item in enumerate(self._host_items(value)):
            self._table.setItem(row, column, item)
        self._displayed_addresses.add(value.ip_address)
        found = len(self._displayed_addresses)
        self._status.setText(
            tr(
                "Found {found} responsive host(s); scanning {total} possible host(s)…",
                found=found,
                total=self._scan_host_count,
            )
        )
        if found == 1 or found % 10 == 0:
            self._table.resizeColumnsToContents()

    @staticmethod
    def _host_items(host: DiscoveredHost) -> tuple[QTableWidgetItem, ...]:
        return (
            IpAddressItem(host.ip_address),
            QTableWidgetItem(host.mac_address),
            NumericItem(f"{host.latency_ms:.2f} ms", host.latency_ms),
            QTableWidgetItem(host.hostname),
            QTableWidgetItem(host.netbios_info),
            QTableWidgetItem(host.vendor),
        )

    def _show_error(self, message: str) -> None:
        self._status.setText(tr("Scan failed: {message}", message=message))
        self._finish()

    def _finish(self) -> None:
        self._table.setSortingEnabled(True)
        self._table.sortItems(0, Qt.SortOrder.AscendingOrder)
        self._task = None
        self._scan.setEnabled(True)
