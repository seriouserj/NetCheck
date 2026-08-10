"""
Version: 1.5.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Bridge streaming command output safely into the Qt event loop.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class StreamingTaskSignals(QObject):
    """Signals emitted while and after a streaming background task runs."""

    output = Signal(str)
    completed = Signal(object)
    failed = Signal(str)


class StreamingTask(QRunnable):
    """Execute an operation that publishes incremental text output."""

    def __init__(self, operation: Callable[[Callable[[str], None]], Any]) -> None:
        super().__init__()
        self._operation = operation
        self.signals = StreamingTaskSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._operation(self.signals.output.emit)
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.completed.emit(result)
