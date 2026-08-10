"""
Version: 1.6.3
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Center SNMP form labels relative to fixed-height inputs.
"""

from __future__ import annotations

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from core.snmp_service import SnmpService, SnmpValue
from ui.async_task import BackgroundTask
from ui.form_layout import centered_form
from ui.hover_table import HoverRowTableWidget


class SnmpPanel(QWidget):
    """Run bounded SNMP v2c read operations without exposing credentials."""

    def __init__(self) -> None:
        super().__init__()
        self._service = SnmpService()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        form = centered_form()
        self._target = QLineEdit()
        self._community = QLineEdit()
        self._community.setEchoMode(QLineEdit.EchoMode.Password)
        self._oid = QLineEdit("1.3.6.1.2.1.1.1.0")
        form.addRow(tr("Target"), self._target)
        form.addRow(tr("Community"), self._community)
        form.addRow(tr("Numeric OID"), self._oid)
        buttons = QHBoxLayout()
        self._get = QPushButton("GET")
        self._get.clicked.connect(lambda: self._run(False))
        self._walk = QPushButton("WALK")
        self._walk.clicked.connect(lambda: self._run(True))
        self._status = QLabel(tr("SNMP v2c read-only; the community string is never saved."))
        self._status.setObjectName("mutedLabel")
        buttons.addWidget(self._status)
        buttons.addStretch()
        buttons.addWidget(self._get)
        buttons.addWidget(self._walk)
        self._table = HoverRowTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(("OID", tr("Value")))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._table)

    def _run(self, walk: bool) -> None:
        self._get.setEnabled(False)
        self._walk.setEnabled(False)
        self._status.setText(tr("Querying SNMP agent…"))
        target, community, oid = self._target.text(), self._community.text(), self._oid.text()
        operation = (lambda: self._service.walk(target, community, oid)) if walk else (lambda: self._service.get(target, community, oid))
        self._task = BackgroundTask(operation)
        self._task.signals.completed.connect(self._show)
        self._task.signals.failed.connect(lambda error: self._finish(f"SNMP error: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def _show(self, value: object) -> None:
        values = value if isinstance(value, list) else []
        self._table.setRowCount(len(values))
        for row, result in enumerate(values):
            if isinstance(result, SnmpValue):
                self._table.setItem(row, 0, QTableWidgetItem(result.oid))
                self._table.setItem(row, 1, QTableWidgetItem(result.value))
        self._finish(tr("Received {count} SNMP value(s).", count=len(values)))

    def _finish(self, status: str) -> None:
        self._status.setText(status)
        self._get.setEnabled(True)
        self._walk.setEnabled(True)
        self._task = None
