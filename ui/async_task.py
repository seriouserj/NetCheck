"""
Version: 0.2.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add reusable Qt thread-pool task adapter.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class TaskSignals(QObject):
    """Signals emitted by a background task."""

    completed = Signal(object)
    failed = Signal(str)


class BackgroundTask(QRunnable):
    """Execute a callable safely in the global Qt thread pool."""

    def __init__(self, operation: Callable[[], Any]) -> None:
        super().__init__()
        self._operation = operation
        self.signals = TaskSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._operation()
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.completed.emit(result)
