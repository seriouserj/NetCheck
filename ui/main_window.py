"""
Version: 0.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Initial resizable native Qt main window.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from core.metadata import APP_NAME, APP_VERSION


class MainWindow(QMainWindow):
    """Top-level NetCheck application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(900, 600)
        self.resize(1180, 760)
        self.setCentralWidget(self._build_welcome_view())

    @staticmethod
    def _build_welcome_view() -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(12)

        title = QLabel("NetCheck")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Professional network diagnostics for macOS")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        return container
