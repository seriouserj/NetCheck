"""
Version: 0.2.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add the Ethernet diagnostics Dashboard tab.
"""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from core.metadata import APP_NAME, APP_VERSION
from ui.dashboard_tab import DashboardTab


class MainWindow(QMainWindow):
    """Top-level NetCheck application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(900, 600)
        self.resize(1180, 760)
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(DashboardTab(), "Dashboard")
        self.setCentralWidget(tabs)
