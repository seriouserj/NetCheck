"""
Version: 1.9.3
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Show a countdown while listening through a full CDP interval.
"""

from __future__ import annotations

import sys

import psutil
from PySide6.QtCore import QThreadPool, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from core.neighbor_models import NetworkNeighbor
from core.neighbor_service import DEFAULT_NEIGHBOR_TIMEOUT, NeighborService
from ui.async_task import BackgroundTask
from ui.hover_table import HoverRowTableWidget


class NeighborsPanel(QWidget):
    """Capture and present directly connected LLDP/CDP neighbors."""

    def __init__(self) -> None:
        super().__init__()
        self._service = NeighborService()
        self._task: BackgroundTask | None = None
        self._remaining_seconds = 0
        self._countdown = QTimer(self)
        self._countdown.setInterval(1_000)
        self._countdown.timeout.connect(self._update_countdown)
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        controls.addWidget(QLabel(tr("Interface")))
        self._interface = QComboBox()
        names = (
            [name for name in psutil.net_if_addrs() if name.startswith(("en", "vlan"))]
            if sys.platform != "win32"
            else [name for name in psutil.net_if_addrs() if "loopback" not in name.casefold()]
        )
        self._interface.addItems(sorted(names))
        self._start = QPushButton(tr("Listen for neighbors"))
        self._start.clicked.connect(self._discover)
        controls.addWidget(self._interface, 1)
        controls.addWidget(self._start)
        status = (
            "Windows capture uses Wireshark TShark and Npcap."
            if sys.platform == "win32"
            else tr("One macOS authorization captures LLDP and CDP together.")
        )
        self._status = QLabel(status)
        self._status.setObjectName("mutedLabel")
        self._table = HoverRowTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in ("Protocol", "System", "Port", "Platform", "Management IP", "Native VLAN", "Capabilities")))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(controls)
        layout.addWidget(self._status)
        layout.addWidget(self._table)

    def _discover(self) -> None:
        self._start.setEnabled(False)
        self._remaining_seconds = int(DEFAULT_NEIGHBOR_TIMEOUT)
        self._update_countdown()
        self._countdown.start()
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
        if neighbors:
            status = tr("Found {count} neighbor advertisement(s).", count=len(neighbors))
        else:
            status = tr("No LLDP/CDP advertisements received from the directly connected port.")
        self._finish(status)

    def _finish(self, status: str) -> None:
        self._countdown.stop()
        self._status.setText(status)
        self._start.setEnabled(True)
        self._task = None

    def _update_countdown(self) -> None:
        self._status.setText(
            tr(
                "Listening for LLDP and CDP advertisements: {seconds} s remaining…",
                seconds=max(0, self._remaining_seconds),
            )
        )
        self._remaining_seconds -= 1
