"""
Version: 1.1.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Apply the DITIS navy and cyan brand palette to native Qt themes.
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
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#0077c8"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#0077c8"))
        application.setPalette(palette)
    else:
        application.setPalette(QPalette())
        palette = application.palette()
    dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
    accent = "#27b9ee" if dark else "#0077c8"
    accent_hover = "#42c8f5" if dark else "#009fe3"
    muted = "#9eb5c9" if dark else "#5d6f7f"
    application.setStyleSheet(
        f"""
        QMainWindow {{ background: palette(window); }}
        QLabel#pageTitle {{ color: {accent}; font-size: 34px; font-weight: 700; }}
        QLabel#pageSubtitle {{ color: {muted}; font-size: 16px; }}
        QLabel#sectionTitle {{ font-size: 24px; font-weight: 650; }}
        QLabel#mutedLabel {{ color: {muted}; }}
        QPushButton {{ padding: 6px 14px; min-height: 24px; border-radius: 6px; }}
        QPushButton:hover {{ color: {accent_hover}; }}
        QTabBar::tab:selected {{ color: {accent}; font-weight: 650; border-bottom: 2px solid {accent}; }}
        QTableWidget {{ border: 1px solid palette(mid); border-radius: 6px; gridline-color: palette(midlight); }}
        QHeaderView::section {{ font-weight: 600; padding: 6px; }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ border: 1px solid {accent}; }}
        QGroupBox {{ font-weight: 600; }}
        a {{ color: {accent}; }}
        QToolTip {{ padding: 6px; }}
        """
    )


def _dark_palette() -> QPalette:
    """Build an accessible Qt dark palette using macOS-like neutral colors."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#071727"))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor("#0b2239"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#102f4e"))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor("#12375b"))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#0077c8"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Link, QColor("#27b9ee"))
    palette.setColor(QPalette.ColorRole.Mid, QColor("#285071"))
    palette.setColor(QPalette.ColorRole.Midlight, QColor("#1b405f"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#71899d"))
    return palette
