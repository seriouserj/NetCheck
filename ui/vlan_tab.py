"""
Version: 1.1.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Test each VLAN batch with one macOS administrator authorization.
"""

from __future__ import annotations

import psutil
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
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

from core.diagnostic_engine import DiagnosticEngine
from core.i18n import tr
from core.vlan_models import CheckState, VlanTestResult
from core.vlan_parser import parse_vlan_ids
from core.vlan_service import VlanService
from ui.async_task import BackgroundTask
from ui.diagnostics_widget import DiagnosticsWidget


class VlanTab(QWidget):
    """Run temporary VLAN tests without blocking the GUI."""

    HEADERS = ("VLAN", "Link", "DHCP", "Gateway", "DNS", "Internet", "Ping", "LLDP", "Address", "Detail")
    COLORS = {CheckState.PASS: QColor("#34c759"), CheckState.WARNING: QColor("#ffcc00"), CheckState.FAIL: QColor("#ff3b30"), CheckState.UNAVAILABLE: QColor("#8e8e93")}

    def __init__(self) -> None:
        super().__init__()
        self._service = VlanService()
        self._diagnostic_engine = DiagnosticEngine()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        form = QFormLayout()
        self._parent = QComboBox()
        self._parent.addItems(sorted(name for name in psutil.net_if_addrs() if name.startswith("en")))
        self._vlans = QLineEdit()
        self._vlans.setPlaceholderText(tr("Examples: 20, 30-35, 100"))
        form.addRow(tr("Parent interface"), self._parent)
        form.addRow(tr("VLAN IDs"), self._vlans)
        controls = QHBoxLayout()
        self._status = QLabel(tr("Ready"))
        self._start = QPushButton(tr("Start tests"))
        self._start.clicked.connect(self._start_tests)
        controls.addWidget(self._status)
        controls.addStretch()
        controls.addWidget(self._start)
        self._table = QTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in self.HEADERS))
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(form)
        layout.addLayout(controls)
        layout.addWidget(self._table)
        self._diagnostics = DiagnosticsWidget()
        layout.addWidget(self._diagnostics)

    def _start_tests(self) -> None:
        try:
            vlan_ids = parse_vlan_ids(self._vlans.text())
        except ValueError as error:
            QMessageBox.warning(self, tr("Invalid VLAN IDs"), str(error))
            return
        parent = self._parent.currentText()
        if not parent:
            QMessageBox.warning(self, tr("No interface"), tr("Connect or select an Ethernet interface."))
            return
        self._start.setEnabled(False)
        self._status.setText(tr("Testing {count} VLAN(s)…", count=len(vlan_ids)))
        self._task = BackgroundTask(lambda: self._service.test_many(parent, vlan_ids))
        self._task.signals.completed.connect(self._show_results)
        self._task.signals.failed.connect(self._show_error)
        from PySide6.QtCore import QThreadPool
        QThreadPool.globalInstance().start(self._task)

    def _show_results(self, value: object) -> None:
        results = value if isinstance(value, list) else []
        self._table.setRowCount(len(results))
        for row, result in enumerate(results):
            if isinstance(result, VlanTestResult):
                self._populate(row, result)
        self._status.setText(tr("Completed {count} VLAN test(s)", count=len(results)))
        typed_results = [item for item in results if isinstance(item, VlanTestResult)]
        self._diagnostics.set_findings(self._diagnostic_engine.analyze_vlans(typed_results))
        self._finish()

    def _populate(self, row: int, result: VlanTestResult) -> None:
        states = (result.link, result.dhcp, result.gateway, result.dns, result.internet, result.ping, result.lldp)
        values = (str(result.vlan_id), *(tr(state.value.title()) for state in states), result.address or "—", tr(result.detail))
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if 1 <= column <= 7:
                item.setForeground(self.COLORS[states[column - 1]])
            self._table.setItem(row, column, item)

    def _show_error(self, message: str) -> None:
        self._status.setText(tr("Test failed: {message}", message=message))
        self._finish()

    def _finish(self) -> None:
        self._task = None
        self._start.setEnabled(True)
