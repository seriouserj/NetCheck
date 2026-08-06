"""
Version: 0.11.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add read-only SNMP v2c diagnostics panel.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QTabWidget, QVBoxLayout, QWidget

from core.dns_tool import RECORD_TYPES, dns_lookup
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
        controls.addWidget(QLabel(label))
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.button = QPushButton("Run")
        self.button.clicked.connect(self.run)
        controls.addWidget(self.input, 1)
        controls.addWidget(self.button)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addLayout(controls)
        layout.addWidget(self.output)

    def run(self) -> None:
        self.button.setEnabled(False)
        self.output.setPlainText("Running…")
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
        self.server.setPlaceholderText("Optional, e.g. 1.1.1.1")
        form.addRow("Name", self.name)
        form.addRow("Record type", self.kind)
        form.addRow("DNS server", self.server)
        self.command = CommandPanel("", "", lambda _: dns_lookup(self.name.text(), self.kind.currentText(), self.server.text()))
        self.command.input.setVisible(False)
        layout.addLayout(form)
        layout.addWidget(self.command)


class WolPanel(QWidget):
    """Send Wake-on-LAN packets with explicit broadcast selection."""

    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.mac = QLineEdit()
        self.broadcast = QLineEdit("255.255.255.255")
        self.status = QLabel("Ready")
        button = QPushButton("Send magic packet")
        button.clicked.connect(self._send)
        layout.addRow("MAC address", self.mac)
        layout.addRow("Broadcast", self.broadcast)
        layout.addRow(button)
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
        tabs.addTab(CommandPanel("Target", "hostname or IP address", ping), "Ping")
        tabs.addTab(CommandPanel("Target", "hostname or IP address", traceroute), "Traceroute")
        tabs.addTab(DnsPanel(), "DNS Lookup")
        tabs.addTab(WolPanel(), "Wake-on-LAN")
        tabs.addTab(NeighborsPanel(), "LLDP/CDP")
        tabs.addTab(SnmpPanel(), "SNMP")
        layout.addWidget(tabs)
