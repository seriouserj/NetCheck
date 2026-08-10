"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Present live MTR-style route loss and latency statistics.
"""

from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from core.route_monitor import RouteHopStats, monitor_route
from ui.hover_table import HoverRowTableWidget
from ui.sortable_items import NumericItem


class _MonitorSignals(QObject):
    updated = Signal(object)
    completed = Signal(object)
    failed = Signal(str)


class _MonitorTask(QRunnable):
    def __init__(self, operation: Callable[[Callable[[tuple[RouteHopStats, ...]], None]], Any]) -> None:
        super().__init__()
        self._operation = operation
        self.signals = _MonitorSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._operation(self.signals.updated.emit)
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.completed.emit(result)


class RouteMonitorPanel(QWidget):
    """Run and display a repeated route-quality measurement."""

    HEADERS = ("Hop", "Address", "Loss", "Sent", "Received", "Last", "Average", "Best", "Worst")

    def __init__(self) -> None:
        super().__init__()
        self._task: _MonitorTask | None = None
        self._stop_event: Event | None = None
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._target = QLineEdit()
        self._target.setPlaceholderText(tr("hostname or IP address"))
        self._cycles = QSpinBox()
        self._cycles.setRange(1, 1000)
        self._cycles.setValue(10)
        self._interval = QDoubleSpinBox()
        self._interval.setRange(0.1, 60.0)
        self._interval.setValue(1.0)
        self._interval.setSuffix(tr(" seconds"))
        self._continuous = QCheckBox(tr("Continuous monitoring"))
        form.addRow(tr("Target"), self._target)
        form.addRow(tr("Cycles"), self._cycles)
        form.addRow(tr("Interval"), self._interval)
        form.addRow("", self._continuous)
        controls = QHBoxLayout()
        self._status = QLabel(tr("Ready"))
        self._status.setObjectName("mutedLabel")
        self._start = QPushButton(tr("Start"))
        self._start.setProperty("primary", True)
        self._start.clicked.connect(self._run)
        self._stop = QPushButton(tr("Stop"))
        self._stop.setEnabled(False)
        self._stop.clicked.connect(self._cancel)
        controls.addWidget(self._status)
        controls.addStretch()
        controls.addWidget(self._stop)
        controls.addWidget(self._start)
        self._table = HoverRowTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(tuple(tr(header) for header in self.HEADERS))
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(form)
        layout.addLayout(controls)
        layout.addWidget(self._table)

    def _run(self) -> None:
        target = self._target.text()
        self._start.setEnabled(False)
        self._stop.setEnabled(True)
        self._stop_event = Event()
        self._table.setRowCount(0)
        self._status.setText(tr("Monitoring route…"))
        cycles = self._cycles.value()
        interval = self._interval.value()
        continuous = self._continuous.isChecked()
        self._task = _MonitorTask(
            lambda update: monitor_route(
                target,
                cycles=cycles,
                interval_seconds=interval,
                continuous=continuous,
                update_callback=update,
                cancel_event=self._stop_event,
            )
        )
        self._task.signals.updated.connect(self._show)
        self._task.signals.completed.connect(lambda value: self._finish(tr("Route monitoring completed.")))
        self._task.signals.failed.connect(lambda error: self._finish(f"Error: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def _show(self, value: object) -> None:
        rows = value if isinstance(value, tuple) else ()
        self._table.setRowCount(len(rows))
        for row, hop in enumerate(rows):
            if not isinstance(hop, RouteHopStats):
                continue
            values = (
                NumericItem(str(hop.hop), hop.hop),
                QTableWidgetItem(hop.address),
                NumericItem(f"{hop.loss_percent:.1f}%", hop.loss_percent),
                NumericItem(str(hop.sent), hop.sent),
                NumericItem(str(hop.received), hop.received),
                _latency_item(hop.last_ms),
                _latency_item(hop.average_ms),
                _latency_item(hop.best_ms),
                _latency_item(hop.worst_ms),
            )
            for column, item in enumerate(values):
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()

    def _cancel(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
            self._stop.setEnabled(False)
            self._status.setText(tr("Stopping route monitor…"))

    def _finish(self, status: str) -> None:
        self._status.setText(status)
        self._start.setEnabled(True)
        self._stop.setEnabled(False)
        self._stop_event = None
        self._task = None


def _latency_item(value: float | None) -> NumericItem:
    """Create a sortable latency cell."""
    return NumericItem("—" if value is None else f"{value:.2f} ms", value or -1.0)
