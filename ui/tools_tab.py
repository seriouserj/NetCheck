"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Start tools with Enter and stop streaming tools with Escape.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from threading import Event

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
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
from core.traceroute_tool import traceroute
from core.wake_on_lan import send_magic_packet
from ui.action_icons import decorate_action
from ui.async_task import BackgroundTask
from ui.form_layout import centered_form
from ui.neighbors_panel import NeighborsPanel
from ui.ping_panel import PingPanel
from ui.route_monitor_panel import RouteMonitorPanel
from ui.snmp_panel import SnmpPanel
from ui.streaming_task import StreamingTask
from ui.tab_navigation import center_tab_group


class CommandPanel(QWidget):
    """Run one text-producing network operation asynchronously."""

    def __init__(
        self,
        label: str,
        placeholder: str,
        action: Callable[..., str],
        *,
        streaming: bool = False,
    ) -> None:
        super().__init__()
        self._action = action
        self._streaming = streaming
        self._task: BackgroundTask | StreamingTask | None = None
        self._stop_event: Event | None = None
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.button = QPushButton(tr("Run"))
        self.button.setProperty("primary", True)
        self.button.setMinimumWidth(120)
        self.button.setMaximumWidth(180)
        self.button.clicked.connect(self.run)
        self.input.returnPressed.connect(self.run)
        stop_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        stop_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        stop_shortcut.activated.connect(self.cancel)
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
        if not self.button.isEnabled():
            return
        self.button.setEnabled(False)
        value = self.input.text()
        if self._streaming:
            self.output.clear()
            self._stop_event = Event()
            task = StreamingTask(lambda emit: self._action(value, emit, self._stop_event))
            task.signals.output.connect(self._append_output)
            task.signals.completed.connect(lambda result: self._finish_stream(str(result)))
            task.signals.failed.connect(self._fail_stream)
            self._task = task
            QThreadPool.globalInstance().start(task)
            return
        self.output.setPlainText(tr("Running…"))
        self._task = BackgroundTask(lambda: self._action(value))
        self._task.signals.completed.connect(lambda result: self._finish(str(result)))
        self._task.signals.failed.connect(lambda error: self._finish(f"Error: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def cancel(self) -> None:
        """Request cancellation of the active streaming operation."""
        if self._stop_event is not None:
            self._stop_event.set()

    def _append_output(self, line: str) -> None:
        self.output.appendPlainText(line)

    def _finish_stream(self, output: str) -> None:
        if self.output.document().isEmpty():
            self.output.setPlainText(output)
        self.button.setEnabled(True)
        self._stop_event = None
        self._task = None

    def _fail_stream(self, error: str) -> None:
        self.output.appendPlainText(f"Error: {error}")
        self.button.setEnabled(True)
        self._stop_event = None
        self._task = None

    def _finish(self, output: str) -> None:
        self.output.setPlainText(output)
        self.button.setEnabled(True)
        self._task = None


class DnsPanel(QWidget):
    """Collect DNS query parameters and display resolver output."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        form = centered_form()
        self.name = QLineEdit()
        self.kind = QComboBox()
        self.kind.addItems(RECORD_TYPES)
        self.server = QLineEdit()
        self.server.setPlaceholderText(tr("Optional, e.g. 1.1.1.1"))
        form.addRow(tr("Name"), self.name)
        form.addRow(tr("Record type"), self.kind)
        form.addRow(tr("DNS server"), self.server)
        self.command = CommandPanel("", "", lambda _: dns_lookup(self.name.text(), self.kind.currentText(), self.server.text()))
        self.name.returnPressed.connect(self.command.run)
        self.server.returnPressed.connect(self.command.run)
        layout.addLayout(form)
        layout.addWidget(self.command)


class WolPanel(QWidget):
    """Send Wake-on-LAN packets with explicit broadcast selection."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        form = centered_form()
        self.mac = QLineEdit()
        self.broadcast = QLineEdit("255.255.255.255")
        self.status = QLabel(tr("Ready"))
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button = QPushButton(tr("Send magic packet"))
        button.setObjectName("wakeButton")
        button.setProperty("primary", True)
        decorate_action(button, "wake", primary=True)
        button.setMinimumWidth(160)
        button.setMaximumWidth(220)
        button.clicked.connect(self._send)
        self.mac.returnPressed.connect(self._send)
        self.broadcast.returnPressed.connect(self._send)
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(button)
        button_row.addStretch()
        form.addRow(tr("MAC address"), self.mac)
        form.addRow(tr("Broadcast"), self.broadcast)
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.status)
        layout.addStretch()

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
        layout.setContentsMargins(24, 18, 24, 24)
        tabs = QTabWidget()
        tabs.setObjectName("innerTabs")
        tabs.tabBar().setObjectName("innerTabBar")
        center_tab_group(tabs)
        tabs.addTab(PingPanel(), "Ping")
        tabs.addTab(
            CommandPanel(
                tr("Target"),
                tr("hostname or IP address"),
                lambda target, emit, stop: traceroute(
                    target,
                    output_callback=emit,
                    cancel_event=stop,
                ),
                streaming=True,
            ),
            tr("Traceroute"),
        )
        tabs.addTab(RouteMonitorPanel(), tr("Route Monitor"))
        tabs.addTab(DnsPanel(), tr("DNS Lookup"))
        tabs.addTab(WolPanel(), tr("Wake-on-LAN"))
        neighbor_index = tabs.addTab(NeighborsPanel(), "LLDP/CDP")
        if sys.platform == "win32":
            tabs.setTabEnabled(neighbor_index, False)
            tabs.setTabToolTip(
                neighbor_index,
                tr("LLDP/CDP capture requires macOS packet capture support."),
            )
        tabs.addTab(SnmpPanel(), "SNMP")
        layout.addWidget(tabs)
