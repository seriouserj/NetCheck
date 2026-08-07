"""
Version: 0.10.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add LLDP/CDP neighbor discovery interface.
"""

from __future__ import annotations

import psutil
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.neighbor_models import NetworkNeighbor
from core.neighbor_service import NeighborService
from ui.async_task import BackgroundTask


class NeighborsPanel(QWidget):
    """Capture and present directly connected LLDP/CDP neighbors."""

    def __init__(self) -> None:
        super().__init__()
        self._service = NeighborService()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Interface"))
        self._interface = QComboBox()
        self._interface.addItems(sorted(name for name in psutil.net_if_addrs() if name.startswith(("en", "vlan"))))
        self._start = QPushButton("Listen for neighbors")
        self._start.clicked.connect(self._discover)
        controls.addWidget(self._interface, 1)
        controls.addWidget(self._start)
        self._status = QLabel("Passive capture may request macOS administrator authorization.")
        self._status.setObjectName("mutedLabel")
        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels(("Protocol", "System", "Port", "Platform", "Management IP", "Native VLAN", "Capabilities"))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(controls)
        layout.addWidget(self._status)
        layout.addWidget(self._table)

    def _discover(self) -> None:
        self._start.setEnabled(False)
        self._status.setText("Listening for LLDP and CDP advertisements…")
        interface = self._interface.currentText()
        self._task = BackgroundTask(lambda: self._service.discover(interface))
        self._task.signals.completed.connect(self._show)
        self._task.signals.failed.connect(lambda error: self._finish(f"Discovery failed: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def _show(self, value: object) -> None:
        neighbors = value if isinstance(value, list) else []
        self._table.setRowCount(len(neighbors))
        for row, neighbor in enumerate(neighbors):
            if not isinstance(neighbor, NetworkNeighbor):
                continue
            values = (neighbor.protocol, neighbor.system_name, neighbor.port_id, neighbor.platform, neighbor.management_address, neighbor.native_vlan, neighbor.capabilities)
            for column, item_value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(item_value))
        self._finish(f"Found {len(neighbors)} neighbor advertisement(s).")

    def _finish(self, status: str) -> None:
        self._status.setText(status)
        self._start.setEnabled(True)
        self._task = None
