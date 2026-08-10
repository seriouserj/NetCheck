"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Center fixed-height fields and unify navigation sizing and backgrounds.
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
    accent = "#009fe3"
    navy = "#05285a"
    muted = "#9eb5c9" if dark else "#5d6f7f"
    application.setStyleSheet(
        f"""
        QMainWindow {{ background: palette(window); }}
        QLabel#pageTitle {{ color: {accent}; font-size: 34px; font-weight: 700; }}
        QLabel#pageSubtitle {{ color: {muted}; font-size: 16px; }}
        QLabel#sectionTitle {{ font-size: 24px; font-weight: 650; }}
        QLabel#mutedLabel {{ color: {muted}; }}
        QPushButton {{ color: {navy}; padding: 7px 16px; min-height: 26px; border: 1px solid {navy}; border-radius: 5px; background: palette(button); }}
        QPushButton:hover {{ color: white; background: {navy}; border-color: {navy}; }}
        QPushButton[primary="true"] {{ color: white; background: {accent}; border-color: {accent}; font-weight: 650; }}
        QPushButton[primary="true"]:hover {{ color: white; background: {navy}; border-color: {navy}; }}
        QPushButton:pressed {{ color: white; background: {accent}; border-color: {accent}; }}
        QFrame#brandHeader {{ background: {navy}; border-bottom: 3px solid {accent}; }}
        QLabel#brandLogo {{ background: white; border-radius: 7px; }}
        QLabel#brandProduct {{ color: white; font-size: 20px; font-weight: 700; }}
        QLabel#brandAuthor {{ color: #b8e8fa; font-size: 12px; }}
        QTabWidget#mainTabs, QTabWidget#mainTabs::pane, QTabBar#mainTabBar, QTabBar#mainTabBar::base {{ background: palette(window); border: 0; }}
        QTabWidget#mainTabs::tab-bar {{ alignment: center; }}
        QTabBar#mainTabBar::tab {{ color: palette(text); background: palette(button); padding: 10px 18px; margin: 0 5px 0 0; border: 1px solid #8a949e; border-radius: 4px; min-width: 132px; min-height: 30px; font-size: 16px; font-weight: 600; }}
        QTabBar#mainTabBar::tab:selected {{ color: white; background: {navy}; }}
        QTabBar#mainTabBar::tab:hover:!selected {{ color: {navy}; background: #d9f3fc; }}
        QTabWidget#innerTabs, QTabBar#innerTabBar, QTabBar#innerTabBar::base {{ background: palette(window); }}
        QTabWidget#innerTabs::tab-bar {{ alignment: center; }}
        QTabWidget#innerTabs::pane {{ background: palette(window); border: 1px solid #8a949e; border-radius: 0; top: 5px; }}
        QTabBar#innerTabBar::tab {{ color: {navy}; background: palette(button); padding: 9px 14px; margin: 0 5px 0 0; border: 1px solid #8a949e; border-radius: 4px; min-width: 142px; min-height: 28px; font-size: 14px; font-weight: 600; }}
        QTabBar#innerTabBar::tab:selected {{ color: white; background: {navy}; border-color: {navy}; }}
        QTabBar#innerTabBar::tab:hover:!selected {{ color: {navy}; background: #d9f3fc; }}
        QLineEdit {{ min-height: 42px; max-height: 42px; padding: 0 10px; }}
        QComboBox {{ min-height: 42px; max-height: 42px; padding: 0 32px 0 10px; }}
        QSpinBox, QDoubleSpinBox {{ min-height: 42px; max-height: 42px; padding-left: 10px; }}
        QPlainTextEdit {{ padding: 8px; }}
        QTableWidget {{ border: 1px solid #707b86; border-radius: 0; gridline-color: #8b96a1; selection-background-color: {navy}; selection-color: white; }}
        QTableWidget::item {{ border: 0; padding: 5px 8px; }}
        QTableWidget::item:hover {{ background: #d9f3fc; color: {navy}; }}
        QHeaderView::section {{ font-weight: 600; padding: 7px; border: 0; border-right: 1px solid #8b96a1; border-bottom: 1px solid #707b86; }}
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
