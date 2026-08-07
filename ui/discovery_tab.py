"""
Version: 1.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Localize network discovery controls and results.
"""

from __future__ import annotations

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.discovery_models import DiscoveredHost
from core.discovery_parser import parse_scan_network
from core.discovery_service import DiscoveryService
from core.i18n import tr
from ui.async_task import BackgroundTask


class DiscoveryTab(QWidget):
    """Scan and display responsive hosts on a selected IPv4 subnet."""

    HEADERS = ("Hostname", "IP", "MAC", "Vendor", "Latency")

    def __init__(self) -> None:
        super().__init__()
        self._service = DiscoveryService()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        controls = QHBoxLayout()
        controls.addWidget(QLabel(tr("Subnet")))
        self._subnet = QLineEdit("192.168.1.0/24")
        self._subnet.setPlaceholderText("192.168.1.0/24")
        self._scan = QPushButton(tr("Scan"))
        self._scan.clicked.connect(self._start_scan)
        controls.addWidget(self._subnet, 1)
        controls.addWidget(self._scan)
        self._status = QLabel(tr("Ready"))
        self._status.setObjectName("mutedLabel")
        self._table = QTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in self.HEADERS))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(controls)
        layout.addWidget(self._status)
        layout.addWidget(self._table)

    def _start_scan(self) -> None:
        try:
            network = parse_scan_network(self._subnet.text())
        except ValueError as error:
            QMessageBox.warning(self, tr("Invalid subnet"), str(error))
            return
        self._scan.setEnabled(False)
        self._status.setText(tr("Scanning {count} possible host(s)…", count=network.num_addresses - 2))
        self._task = BackgroundTask(lambda: self._service.scan(network))
        self._task.signals.completed.connect(self._show_results)
        self._task.signals.failed.connect(self._show_error)
        QThreadPool.globalInstance().start(self._task)

    def _show_results(self, value: object) -> None:
        hosts = value if isinstance(value, list) else []
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(hosts))
        for row, host in enumerate(hosts):
            if not isinstance(host, DiscoveredHost):
                continue
            values = (host.hostname, host.ip_address, host.mac_address, host.vendor, f"{host.latency_ms:.2f} ms")
            for column, item_value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(item_value))
        self._table.setSortingEnabled(True)
        self._status.setText(tr("Found {count} responsive host(s)", count=len(hosts)))
        self._finish()

    def _show_error(self, message: str) -> None:
        self._status.setText(tr("Scan failed: {message}", message=message))
        self._finish()

    def _finish(self) -> None:
        self._task = None
        self._scan.setEnabled(True)
