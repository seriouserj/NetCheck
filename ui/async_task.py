"""
Version: 1.7.0
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Publish task lifetime to the global activity indicator.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from ui.activity import activity_tracker


class TaskSignals(QObject):
    """Signals emitted by a background task."""

    started = Signal()
    completed = Signal(object)
    failed = Signal(str)
    settled = Signal()


class BackgroundTask(QRunnable):
    """Execute a callable safely in the global Qt thread pool."""

    def __init__(self, operation: Callable[[], Any]) -> None:
        super().__init__()
        self._operation = operation
        self.signals = TaskSignals()
        tracker = activity_tracker()
        self.signals.started.connect(tracker.begin)
        self.signals.settled.connect(tracker.end)

    @Slot()
    def run(self) -> None:
        self.signals.started.emit()
        try:
            result = self._operation()
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.completed.emit(result)
        finally:
            self.signals.settled.emit()
