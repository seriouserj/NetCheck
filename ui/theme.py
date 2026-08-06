"""
Version: 0.7.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add explicit light, dark, and system theme selection.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_theme(application: QApplication, preference: str = "system") -> None:
    """Apply a native-derived system, light, or dark application theme."""
    if preference == "dark":
        palette = _dark_palette()
        application.setPalette(palette)
    elif preference == "light":
        palette = application.style().standardPalette()
        application.setPalette(palette)
    else:
        application.setPalette(QPalette())
        palette = application.palette()
    dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
    accent = "#5ac8fa" if dark else "#007aff"
    muted = "#a1a1a6" if dark else "#6e6e73"
    application.setStyleSheet(
        f"""
        QMainWindow {{ background: palette(window); }}
        QLabel#pageTitle {{ color: {accent}; font-size: 34px; font-weight: 700; }}
        QLabel#pageSubtitle {{ color: {muted}; font-size: 16px; }}
        QLabel#sectionTitle {{ font-size: 24px; font-weight: 650; }}
        QLabel#mutedLabel {{ color: {muted}; }}
        QPushButton {{ padding: 6px 14px; min-height: 24px; }}
        QTableWidget {{ border: 1px solid palette(mid); border-radius: 6px; gridline-color: palette(midlight); }}
        QToolTip {{ padding: 6px; }}
        """
    )


def _dark_palette() -> QPalette:
    """Build an accessible Qt dark palette using macOS-like neutral colors."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1c1c1e"))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor("#2c2c2e"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#3a3a3c"))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor("#3a3a3c"))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#0a84ff"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#8e8e93"))
    return palette
