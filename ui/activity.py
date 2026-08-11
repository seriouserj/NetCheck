"""
Version: 1.7.0
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Track concurrent background operations for global busy feedback.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot


class ActivityTracker(QObject):
    """Publish whether one or more long-running application tasks are active."""

    busy_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._active_count = 0

    @property
    def busy(self) -> bool:
        """Return whether at least one tracked operation is running."""
        return self._active_count > 0

    @Slot()
    def begin(self) -> None:
        """Register one newly started operation."""
        was_busy = self.busy
        self._active_count += 1
        if not was_busy:
            self.busy_changed.emit(True)

    @Slot()
    def end(self) -> None:
        """Register one completed operation without allowing underflow."""
        if self._active_count == 0:
            return
        self._active_count -= 1
        if not self.busy:
            self.busy_changed.emit(False)


_TRACKER = ActivityTracker()


def activity_tracker() -> ActivityTracker:
    """Return the process-wide application activity tracker."""
    return _TRACKER
