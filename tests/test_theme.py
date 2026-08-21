"""
Version: 1.10.0
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify explicit accessible Dark Mode surfaces and table headers.
"""

from __future__ import annotations

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from ui.theme import apply_theme


def test_dark_theme_uses_explicit_accessible_surfaces(qt_application: QApplication) -> None:
    try:
        apply_theme(qt_application, "dark")
        style_sheet = qt_application.styleSheet()
        palette = qt_application.palette()

        assert palette.color(QPalette.ColorRole.Window).name() == "#071727"
        assert palette.color(QPalette.ColorRole.Base).name() == "#0b2239"
        assert "QMainWindow, QWidget#appContainer { color: #ffffff; background: #071727; }" in style_sheet
        assert "QHeaderView::section, QTableCornerButton::section { color: #ffffff; background: #12375b;" in style_sheet
        assert "QTableWidget { color: #ffffff; background: #0b2239; alternate-background-color: #102f4e;" in style_sheet
        assert "QGroupBox { color: #ffffff; background: #071727;" in style_sheet
        assert "QScrollBar:horizontal, QScrollBar:vertical { background: #0d2944;" in style_sheet
    finally:
        apply_theme(qt_application, "system")
