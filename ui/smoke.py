"""
Version: 1.0.0
Date: 2026-08-07
Author: NetCheck Contributors
Changelog: Add reusable application bundle smoke validation.
"""

from __future__ import annotations

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QTabWidget

from core.application import configure_application
from ui.main_window import MainWindow

EXPECTED_TABS = ("Dashboard", "VLAN", "Discovery", "Ports", "Tools", "Settings")


def run_smoke_test(application: QApplication) -> int:
    """Construct the complete UI and validate its top-level navigation."""
    configure_application(application)
    window = MainWindow()
    tabs = window.centralWidget()
    if not isinstance(tabs, QTabWidget):
        raise RuntimeError("MainWindow must expose a QTabWidget as its central widget.")
    actual_tabs = tuple(tabs.tabText(index) for index in range(tabs.count()))
    if actual_tabs != EXPECTED_TABS:
        raise RuntimeError(f"Unexpected application tabs: {actual_tabs}")
    QThreadPool.globalInstance().waitForDone(15_000)
    application.processEvents()
    window.close()
    return 0
