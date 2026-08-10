"""
Version: 1.3.1
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Refine inner navigation and center compact tool actions.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.dns_tool import RECORD_TYPES, dns_lookup
from core.i18n import tr
from core.ping_tool import ping
from core.traceroute_tool import traceroute
from core.wake_on_lan import send_magic_packet
from ui.async_task import BackgroundTask
from ui.neighbors_panel import NeighborsPanel
from ui.snmp_panel import SnmpPanel


class CommandPanel(QWidget):
    """Run one text-producing network operation asynchronously."""

    def __init__(self, label: str, placeholder: str, action: Callable[[str], str]) -> None:
        super().__init__()
        self._action = action
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.button = QPushButton(tr("Run"))
        self.button.setProperty("primary", True)
        self.button.setMinimumWidth(120)
        self.button.setMaximumWidth(180)
        self.button.clicked.connect(self.run)
        if label:
            controls.addWidget(QLabel(label))
            controls.addWidget(self.input, 1)
            controls.addWidget(self.button)
        else:
            self.input.setVisible(False)
            controls.addStretch()
            controls.addWidget(self.button)
            controls.addStretch()
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addLayout(controls)
        layout.addWidget(self.output)

    def run(self) -> None:
        self.button.setEnabled(False)
        self.output.setPlainText(tr("Running…"))
        value = self.input.text()
        self._task = BackgroundTask(lambda: self._action(value))
        self._task.signals.completed.connect(lambda result: self._finish(str(result)))
        self._task.signals.failed.connect(lambda error: self._finish(f"Error: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def _finish(self, output: str) -> None:
        self.output.setPlainText(output)
        self.button.setEnabled(True)
        self._task = None


class DnsPanel(QWidget):
    """Collect DNS query parameters and display resolver output."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.kind = QComboBox()
        self.kind.addItems(RECORD_TYPES)
        self.server = QLineEdit()
        self.server.setPlaceholderText(tr("Optional, e.g. 1.1.1.1"))
        form.addRow(tr("Name"), self.name)
        form.addRow(tr("Record type"), self.kind)
        form.addRow(tr("DNS server"), self.server)
        self.command = CommandPanel("", "", lambda _: dns_lookup(self.name.text(), self.kind.currentText(), self.server.text()))
        layout.addLayout(form)
        layout.addWidget(self.command)


class WolPanel(QWidget):
    """Send Wake-on-LAN packets with explicit broadcast selection."""

    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.mac = QLineEdit()
        self.broadcast = QLineEdit("255.255.255.255")
        self.status = QLabel(tr("Ready"))
        button = QPushButton(tr("Send magic packet"))
        button.setProperty("primary", True)
        button.setMinimumWidth(160)
        button.setMaximumWidth(220)
        button.clicked.connect(self._send)
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(button)
        button_row.addStretch()
        layout.addRow(tr("MAC address"), self.mac)
        layout.addRow(tr("Broadcast"), self.broadcast)
        layout.addRow(button_row)
        layout.addRow(self.status)

    def _send(self) -> None:
        try:
            self.status.setText(send_magic_packet(self.mac.text(), self.broadcast.text()))
        except (ValueError, OSError) as error:
            self.status.setText(f"Error: {error}")


class ToolsTab(QWidget):
    """Container for focused day-to-day network tools."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        tabs = QTabWidget()
        tabs.setObjectName("innerTabs")
        tabs.tabBar().setObjectName("innerTabBar")
        tabs.setDocumentMode(True)
        tabs.addTab(CommandPanel(tr("Target"), tr("hostname or IP address"), ping), "Ping")
        tabs.addTab(CommandPanel(tr("Target"), tr("hostname or IP address"), traceroute), tr("Traceroute"))
        tabs.addTab(DnsPanel(), tr("DNS Lookup"))
        tabs.addTab(WolPanel(), tr("Wake-on-LAN"))
        tabs.addTab(NeighborsPanel(), "LLDP/CDP")
        tabs.addTab(SnmpPanel(), "SNMP")
        layout.addWidget(tabs)
