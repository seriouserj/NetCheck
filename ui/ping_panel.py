"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add multi-target, payload-size, and continuous Ping controls.
"""

from __future__ import annotations

from threading import Event

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from core.multi_ping import parse_ping_targets, run_multi_ping
from ui.form_layout import centered_form
from ui.streaming_task import StreamingTask


class PingPanel(QWidget):
    """Run concurrent finite or continuous ICMP tests."""

    def __init__(self) -> None:
        super().__init__()
        self._task: StreamingTask | None = None
        self._stop_event: Event | None = None
        layout = QVBoxLayout(self)
        form = centered_form(grow_fields=True)
        self._targets = QLineEdit()
        self._targets.setPlaceholderText(tr("hostnames or IP addresses, separated by commas"))
        self._packet_size = QSpinBox()
        self._packet_size.setRange(0, 65507)
        self._packet_size.setValue(56)
        self._packet_size.setSuffix(tr(" bytes"))
        self._continuous = QCheckBox(tr("Continuous; show statistics every 100 requests"))
        form.addRow(tr("Targets"), self._targets)
        form.addRow(tr("Packet payload"), self._packet_size)
        form.addRow("", self._continuous)
        buttons = QHBoxLayout()
        self._status = QLabel(tr("Finite mode sends 4 requests to every target."))
        self._status.setObjectName("mutedLabel")
        self._start = QPushButton(tr("Start"))
        self._start.setProperty("primary", True)
        self._start.clicked.connect(self._run)
        self._stop = QPushButton(tr("Stop"))
        self._stop.setEnabled(False)
        self._stop.clicked.connect(self._cancel)
        buttons.addWidget(self._status)
        buttons.addStretch()
        buttons.addWidget(self._stop)
        buttons.addWidget(self._start)
        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._output)

    def _run(self) -> None:
        try:
            targets = parse_ping_targets(self._targets.text())
        except ValueError as error:
            self._status.setText(str(error))
            return
        self._output.clear()
        self._start.setEnabled(False)
        self._stop.setEnabled(True)
        self._stop_event = Event()
        packet_size = self._packet_size.value()
        continuous = self._continuous.isChecked()
        self._status.setText(tr("Pinging {count} target(s)…", count=len(targets)))
        self._task = StreamingTask(
            lambda emit: run_multi_ping(
                targets,
                packet_size=packet_size,
                continuous=continuous,
                output_callback=emit,
                cancel_event=self._stop_event,
            )
        )
        self._task.signals.output.connect(self._output.appendPlainText)
        self._task.signals.completed.connect(lambda _: self._finish(tr("Ping completed.")))
        self._task.signals.failed.connect(lambda error: self._finish(f"Error: {error}"))
        QThreadPool.globalInstance().start(self._task)

    def _cancel(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
            self._stop.setEnabled(False)
            self._status.setText(tr("Stopping ping sessions…"))

    def _finish(self, status: str) -> None:
        self._status.setText(status)
        self._start.setEnabled(True)
        self._stop.setEnabled(False)
        self._stop_event = None
        self._task = None
