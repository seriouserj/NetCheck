"""
Version: 0.11.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add read-only SNMP v2c GET and WALK interface.
"""

from __future__ import annotations

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QAbstractItemView, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from core.snmp_service import SnmpService, SnmpValue
from ui.async_task import BackgroundTask


class SnmpPanel(QWidget):
    """Run bounded SNMP v2c read operations without exposing credentials."""

    def __init__(self) -> None:
        super().__init__()
        self._service = SnmpService()
        self._task: BackgroundTask | None = None
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._target = QLineEdit()
        self._community = QLineEdit()
        self._community.setEchoMode(QLineEdit.EchoMode.Password)
        self._oid = QLineEdit("1.3.6.1.2.1.1.1.0")
        form.addRow("Target", self._target)
        form.addRow("Community", self._community)
        form.addRow("Numeric OID", self._oid)
        buttons = QHBoxLayout()
        self._get = QPushButton("GET")
        self._get.clicked.connect(lambda: self._run(False))
        self._walk = QPushButton("WALK")
        self._walk.clicked.connect(lambda: self._run(True))
        self._status = QLabel("SNMP v2c read-only; the community string is never saved.")
        self._status.setObjectName("mutedLabel")
        buttons.addWidget(self._status)
        buttons.addStretch()
        buttons.addWidget(self._get)
        buttons.addWidget(self._walk)
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(("OID", "Value"))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._table)

    def _run(self, walk: bool) -> None:
        self._get.setEnabled(False)
        self._walk.setEnabled(False)
        self._status.setText("Querying SNMP agent…")
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
        self._finish(f"Received {len(values)} SNMP value(s).")

    def _finish(self, status: str) -> None:
        self._status.setText(status)
        self._get.setEnabled(True)
        self._walk.setEnabled(True)
        self._task = None
