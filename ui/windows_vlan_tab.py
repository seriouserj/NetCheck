"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Provide an active Windows VLAN driver capability inspector.
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
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from core.windows_vlan_capability import VlanDriverProperty, WindowsVlanCapabilityService
from ui.async_task import BackgroundTask
from ui.hover_table import HoverRowTableWidget


class WindowsVlanTab(QWidget):
    """Explain and detect the VLAN abilities of a Windows adapter driver."""

    def __init__(self) -> None:
        super().__init__()
        self._service = WindowsVlanCapabilityService()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        controls = QHBoxLayout()
        controls.addWidget(QLabel(tr("Interface")))
        self._interface = QComboBox()
        self._refresh_interfaces()
        self._refresh = QPushButton(tr("Refresh"))
        self._refresh.clicked.connect(self._refresh_interfaces)
        self._inspect = QPushButton(tr("Check VLAN support"))
        self._inspect.setProperty("primary", True)
        self._inspect.clicked.connect(self._start)
        controls.addWidget(self._interface, 1)
        controls.addWidget(self._refresh)
        controls.addWidget(self._inspect)
        self._status = QLabel(
            tr("Windows VLAN testing depends on VLAN controls exposed by the Ethernet adapter driver.")
        )
        self._status.setObjectName("mutedLabel")
        self._table = HoverRowTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(
            (tr("Driver property"), tr("Current value"), tr("Registry keyword"))
        )
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(controls)
        layout.addWidget(self._status)
        layout.addWidget(self._table)

    def _refresh_interfaces(self) -> None:
        selected = self._interface.currentText() if hasattr(self, "_interface") else ""
        names = sorted(name for name in psutil.net_if_addrs() if _is_ethernet_candidate(name))
        if not hasattr(self, "_interface"):
            return
        self._interface.clear()
        self._interface.addItems(names)
        index = self._interface.findText(selected)
        if index >= 0:
            self._interface.setCurrentIndex(index)

    def _start(self) -> None:
        self._inspect.setEnabled(False)
        self._status.setText(tr("Inspecting Windows adapter driver…"))
        adapter = self._interface.currentText()
        self._task = BackgroundTask(lambda: self._service.inspect(adapter))
        self._task.signals.completed.connect(self._show)
        self._task.signals.failed.connect(lambda error: self._finish(f"Error: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def _show(self, value: object) -> None:
        properties = value if isinstance(value, list) else []
        self._table.setRowCount(len(properties))
        for row, item in enumerate(properties):
            if not isinstance(item, VlanDriverProperty):
                continue
            for column, text in enumerate(
                (item.display_name, item.display_value, item.registry_keyword)
            ):
                self._table.setItem(row, column, QTableWidgetItem(text))
        status = (
            tr("The adapter driver exposes {count} VLAN control(s).", count=len(properties))
            if properties
            else tr("This adapter driver does not expose a configurable VLAN ID to Windows.")
        )
        self._finish(status)

    def _finish(self, status: str) -> None:
        self._status.setText(status)
        self._inspect.setEnabled(True)
        self._task = None


def _is_ethernet_candidate(name: str) -> bool:
    normalized = name.casefold()
    return not any(
        marker in normalized
        for marker in ("loopback", "wi-fi", "wifi", "wireless", "wlan", "bluetooth", "tunnel", "vethernet")
    )
