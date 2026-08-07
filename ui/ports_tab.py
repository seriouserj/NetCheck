"""
Version: 1.1.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Localize TCP scanner controls, headings, and states.
"""

from __future__ import annotations

from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
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

from core.i18n import tr
from core.port_models import PortScanResult, PortState
from core.port_parser import parse_ports
from core.port_scanner import PortScanner
from ui.async_task import BackgroundTask


class PortsTab(QWidget):
    """Scan selected TCP ports on one hostname or address."""

    COLORS = {PortState.OPEN: QColor("#34c759"), PortState.CLOSED: QColor("#ff3b30"), PortState.FILTERED: QColor("#ffcc00")}

    def __init__(self) -> None:
        super().__init__()
        self._scanner = PortScanner()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        form = QFormLayout()
        self._target = QLineEdit()
        self._target.setPlaceholderText("hostname or IP address")
        self._ports = QLineEdit("22, 53, 80, 443")
        self._ports.setPlaceholderText("22, 80, 443, 8000-8100")
        form.addRow(tr("Target"), self._target)
        form.addRow(tr("TCP ports"), self._ports)
        controls = QHBoxLayout()
        self._status = QLabel(tr("Ready"))
        self._status.setObjectName("mutedLabel")
        self._start = QPushButton(tr("Scan ports"))
        self._start.clicked.connect(self._start_scan)
        controls.addWidget(self._status)
        controls.addStretch()
        controls.addWidget(self._start)
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in ("Port", "State", "Service", "Latency")))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(form)
        layout.addLayout(controls)
        layout.addWidget(self._table)

    def _start_scan(self) -> None:
        try:
            ports = parse_ports(self._ports.text())
        except ValueError as error:
            QMessageBox.warning(self, tr("Invalid ports"), str(error))
            return
        target = self._target.text().strip()
        if not target:
            QMessageBox.warning(self, tr("Invalid target"), tr("Enter a target hostname or IP address."))
            return
        self._start.setEnabled(False)
        self._status.setText(tr("Scanning {count} TCP port(s)…", count=len(ports)))
        self._task = BackgroundTask(lambda: self._scanner.scan(target, ports))
        self._task.signals.completed.connect(self._show_results)
        self._task.signals.failed.connect(self._show_error)
        QThreadPool.globalInstance().start(self._task)

    def _show_results(self, value: object) -> None:
        if not isinstance(value, tuple) or len(value) != 2:
            self._show_error("Unexpected scanner response")
            return
        address, results = value
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(results))
        for row, result in enumerate(results):
            if not isinstance(result, PortScanResult):
                continue
            latency = f"{result.latency_ms:.2f} ms" if result.latency_ms is not None else "—"
            values = (str(result.port), tr(result.state.value), result.service, latency)
            for column, item_value in enumerate(values):
                item = QTableWidgetItem(item_value)
                if column == 1:
                    item.setForeground(self.COLORS[result.state])
                self._table.setItem(row, column, item)
        self._table.setSortingEnabled(True)
        open_count = sum(result.state is PortState.OPEN for result in results)
        self._status.setText(tr("{address}: {open_count} open of {count} scanned", address=address, open_count=open_count, count=len(results)))
        self._finish()

    def _show_error(self, message: str) -> None:
        self._status.setText(tr("Scan failed: {message}", message=message))
        self._finish()

    def _finish(self) -> None:
        self._task = None
        self._start.setEnabled(True)
