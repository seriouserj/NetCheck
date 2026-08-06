"""
Version: 0.2.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Extend system-aware styling for dashboard controls.
"""

from __future__ import annotations

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


def apply_system_theme(application: QApplication) -> None:
    """Apply restrained styling while retaining the active native palette."""
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
