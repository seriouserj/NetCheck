"""
Version: 1.9.4
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Distinguish LAN and Wi-Fi while preserving raw VLAN interface names.
"""

from __future__ import annotations

import re

import psutil
from PySide6.QtCore import QThreadPool, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.diagnostic_engine import DiagnosticEngine
from core.i18n import tr
from core.vlan_discovery_service import VlanDiscoveryService
from core.vlan_models import CheckState, VlanTestResult
from core.vlan_parser import parse_vlan_ids
from core.vlan_service import VlanService
from ui.async_task import BackgroundTask
from ui.diagnostics_widget import DiagnosticsWidget
from ui.form_layout import centered_form
from ui.hover_table import HoverRowTableWidget
from ui.interface_selector import populate_interface_selector, selected_interface_name


class VlanTab(QWidget):
    """Run temporary VLAN tests without blocking the GUI."""

    result_ready = Signal(object)

    HEADERS = ("VLAN", "Link", "DHCP", "Gateway", "DNS", "Internet", "Ping", "LLDP", "Address", "Detail")
    COLORS = {CheckState.PASS: QColor("#34c759"), CheckState.WARNING: QColor("#ffcc00"), CheckState.FAIL: QColor("#ff3b30"), CheckState.UNAVAILABLE: QColor("#8e8e93")}

    def __init__(self) -> None:
        super().__init__()
        self._service = VlanService()
        self._discovery_service = VlanDiscoveryService()
        self._diagnostic_engine = DiagnosticEngine()
        self._task: BackgroundTask | None = None
        self._results: dict[int, VlanTestResult] = {}
        self._row_for_vlan: dict[int, int] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        form = centered_form()
        self._parent = QComboBox()
        self._refresh_interfaces()
        self._interface_refresh = QPushButton(tr("Refresh"))
        self._interface_refresh.clicked.connect(self._refresh_interfaces)
        interface_row = QHBoxLayout()
        interface_row.addWidget(self._parent)
        interface_row.addWidget(self._interface_refresh)
        self._vlans = QLineEdit()
        self._vlans.setPlaceholderText(tr("Examples: 20, 30-35, 100"))
        self._vlans.returnPressed.connect(self._start_tests)
        form.addRow(tr("Interface"), interface_row)
        form.addRow(tr("VLAN IDs"), self._vlans)
        controls = QHBoxLayout()
        self._status = QLabel(tr("Ready"))
        self._start = QPushButton(tr("Start tests"))
        self._start.setProperty("primary", True)
        self._start.clicked.connect(self._start_tests)
        self._discover = QPushButton(tr("Discover VLANs"))
        self._discover.setToolTip(tr("Observe tagged traffic for 8 seconds; silent VLANs cannot be detected passively."))
        self._discover.clicked.connect(self._start_discovery)
        controls.addWidget(self._status)
        controls.addStretch()
        controls.addWidget(self._discover)
        controls.addWidget(self._start)
        self._table = HoverRowTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(tuple(tr(item) for item in self.HEADERS))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(form)
        layout.addLayout(controls)
        layout.addWidget(self._table)
        self._diagnostics = DiagnosticsWidget()
        layout.addWidget(self._diagnostics)
        self.result_ready.connect(self._show_progress)
        self._interface_timer = QTimer(self)
        self._interface_timer.setInterval(2000)
        self._interface_timer.timeout.connect(self._refresh_interfaces)
        self._interface_timer.start()

    def _refresh_interfaces(self) -> None:
        """Keep the selector synchronized with adapters connected after launch."""
        selected = selected_interface_name(self._parent) if hasattr(self, "_parent") else ""
        names = sorted(name for name in psutil.net_if_addrs() if name.startswith("en"))
        if hasattr(self, "_parent"):
            existing = [str(self._parent.itemData(index)) for index in range(self._parent.count())]
            if set(existing) == set(names):
                return
            populate_interface_selector(self._parent, names, selected)

    def _start_tests(self) -> None:
        try:
            vlan_ids = parse_vlan_ids(self._vlans.text())
        except ValueError as error:
            QMessageBox.warning(self, tr("Invalid VLAN IDs"), str(error))
            return
        parent = selected_interface_name(self._parent)
        if not parent:
            QMessageBox.warning(self, tr("No interface"), tr("Connect or select an Ethernet interface."))
            return
        self._start.setEnabled(False)
        self._interface_refresh.setEnabled(False)
        self._status.setText(tr("Testing {count} VLAN(s)…", count=len(vlan_ids)))
        self._results.clear()
        self._row_for_vlan = {vlan_id: row for row, vlan_id in enumerate(vlan_ids)}
        self._table.setRowCount(len(vlan_ids))
        for row, vlan_id in enumerate(vlan_ids):
            self._table.setItem(row, 0, QTableWidgetItem(str(vlan_id)))
            self._table.setItem(row, 9, QTableWidgetItem(tr("Waiting…")))
        self._diagnostics.set_findings([])
        self._task = BackgroundTask(
            lambda: self._service.test_many(parent, vlan_ids, progress=self.result_ready.emit)
        )
        self._task.signals.completed.connect(self._show_results)
        self._task.signals.failed.connect(self._show_error)
        QThreadPool.globalInstance().start(self._task)

    def _start_discovery(self) -> None:
        parent = selected_interface_name(self._parent)
        if not parent:
            QMessageBox.warning(self, tr("No interface"), tr("Connect or select an Ethernet interface."))
            return
        self._start.setEnabled(False)
        self._discover.setEnabled(False)
        self._interface_refresh.setEnabled(False)
        self._status.setText(tr("Listening for tagged VLAN traffic for 8 seconds…"))
        self._task = BackgroundTask(lambda: self._discovery_service.discover(parent, 8.0))
        self._task.signals.completed.connect(self._show_discovered)
        self._task.signals.failed.connect(self._show_error)
        QThreadPool.globalInstance().start(self._task)

    def _show_discovered(self, value: object) -> None:
        vlan_ids = [item for item in value if isinstance(item, int)] if isinstance(value, list) else []
        if vlan_ids:
            self._vlans.setText(",".join(str(item) for item in vlan_ids))
            self._status.setText(tr("Observed {count} active VLAN(s)", count=len(vlan_ids)))
        else:
            self._status.setText(tr("No tagged traffic observed; silent VLANs may still be available."))
        self._finish()

    def _show_progress(self, value: object) -> None:
        if not isinstance(value, VlanTestResult) or value.vlan_id not in self._row_for_vlan:
            return
        self._results[value.vlan_id] = value
        self._populate(self._row_for_vlan[value.vlan_id], value)
        completed = len(self._results)
        total = len(self._row_for_vlan)
        self._status.setText(tr("Completed {completed} of {total} VLAN tests", completed=completed, total=total))
        self._diagnostics.set_findings(
            self._diagnostic_engine.analyze_vlans(list(self._results.values()))
        )

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
        values = (
            str(result.vlan_id),
            *(tr(state.value.title()) for state in states),
            result.address or "—",
            self._translated_detail(result.detail),
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if 1 <= column <= 7:
                item.setForeground(self.COLORS[states[column - 1]])
            self._table.setItem(row, column, item)

    @staticmethod
    def _translated_detail(detail: str) -> str:
        failure_count = re.fullmatch(r"(\d+) core check\(s\) failed", detail)
        if failure_count:
            return tr("{count} core check(s) failed", count=failure_count.group(1))
        return tr(detail)

    def _show_error(self, message: str) -> None:
        self._status.setText(tr("Test failed: {message}", message=message))
        self._finish()

    def _finish(self) -> None:
        self._task = None
        self._start.setEnabled(True)
        self._discover.setEnabled(True)
        self._interface_refresh.setEnabled(True)
        self._refresh_interfaces()
