"""
Version: 1.7.0
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Publish streaming task lifetime to the global activity indicator.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from ui.activity import activity_tracker


class StreamingTaskSignals(QObject):
    """Signals emitted while and after a streaming background task runs."""

    started = Signal()
    output = Signal(str)
    completed = Signal(object)
    failed = Signal(str)
    settled = Signal()


class StreamingTask(QRunnable):
    """Execute an operation that publishes incremental text output."""

    def __init__(self, operation: Callable[[Callable[[str], None]], Any]) -> None:
        super().__init__()
        self._operation = operation
        self.signals = StreamingTaskSignals()
        tracker = activity_tracker()
        self.signals.started.connect(tracker.begin)
        self.signals.settled.connect(tracker.end)

    @Slot()
    def run(self) -> None:
        self.signals.started.emit()
        try:
            result = self._operation(self.signals.output.emit)
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.completed.emit(result)
        finally:
            self.signals.settled.emit()
