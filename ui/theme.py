"""
Version: 1.10.0
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Use explicit accessible surfaces for every themed Qt component.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from core.resources import resource_path

BRAND_ACCENT = "#009fe3"
BRAND_LIGHT_CYAN = "#27b9ee"
BRAND_BLUE = "#0077c8"
BRAND_NAVY = "#05285a"


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
    accent = BRAND_ACCENT
    navy = BRAND_NAVY
    muted = "#9eb5c9" if dark else "#5d6f7f"
    window = palette.color(QPalette.ColorRole.Window).name()
    base = palette.color(QPalette.ColorRole.Base).name()
    alternate = palette.color(QPalette.ColorRole.AlternateBase).name()
    text = palette.color(QPalette.ColorRole.Text).name()
    panel = "#0d2944" if dark else "#eef0f2"
    header = "#12375b" if dark else "#e7eaed"
    border = "#416784" if dark else "#8b96a1"
    hover = "#16496f" if dark else "#d9f3fc"
    hover_text = "#ffffff" if dark else navy
    scroll_handle = "#416784" if dark else "#9ca6af"
    step_up = resource_path("icons/step-up-white.svg").as_posix()
    step_down = resource_path("icons/step-down-white.svg").as_posix()
    application.setStyleSheet(
        f"""
        QMainWindow, QWidget#appContainer {{ color: {text}; background: {window}; }}
        QLabel#pageTitle {{ color: {accent}; font-size: 34px; font-weight: 700; }}
        QLabel#pageSubtitle {{ color: {muted}; font-size: 16px; }}
        QLabel#sectionTitle {{ font-size: 24px; font-weight: 650; }}
        QLabel#mutedLabel {{ color: {muted}; }}
        QPushButton {{ color: white; padding: 7px 16px; min-height: 26px; border: 1px solid {navy}; border-radius: 5px; background: {navy}; }}
        QPushButton:hover {{ color: white; background: {accent}; border-color: {accent}; }}
        QPushButton:pressed {{ color: white; background: #0077c8; border-color: #0077c8; }}
        QPushButton:focus {{ border-color: {accent}; }}
        QPushButton:disabled {{ color: #b8e8fa; background: #173c67; border-color: #5d6f7f; }}
        QPushButton[primary="true"] {{ font-weight: 650; }}
        QFrame#brandHeader {{ background: {navy}; border-bottom: 3px solid {accent}; }}
        QLabel#brandLogo {{ background: white; border-radius: 7px; }}
        QLabel#brandProduct {{ color: white; font-size: 26px; font-weight: 700; }}
        QLabel#brandAuthor {{ color: #b8e8fa; font-size: 12px; }}
        QTabWidget#mainTabs, QTabWidget#mainTabs::pane, QTabBar#mainTabBar, QTabBar#mainTabBar::base {{ color: {text}; background: {window}; border: 0; }}
        QTabWidget#mainTabs::tab-bar {{ alignment: center; }}
        QTabBar#mainTabBar::tab {{ color: white; background: {navy}; padding: 10px 18px; margin: 0 5px 0 0; border: 1px solid {navy}; border-radius: 4px; min-width: 132px; min-height: 30px; font-size: 16px; font-weight: 600; }}
        QTabBar#mainTabBar::tab:selected {{ color: white; background: {accent}; border-color: {accent}; }}
        QTabBar#mainTabBar::tab:hover:!selected {{ color: white; background: {accent}; border-color: {accent}; }}
        QTabBar#mainTabBar::tab:disabled {{ color: #e2e7eb; background: #7d8994; border-color: #7d8994; }}
        QTabWidget#innerTabs, QTabBar#innerTabBar, QTabBar#innerTabBar::base {{ color: {text}; background: {window}; border: 0; }}
        QTabWidget#innerTabs::tab-bar {{ alignment: center; }}
        QTabWidget#innerTabs::pane {{ background: {window}; border: 1px solid {border}; border-radius: 0; top: 15px; }}
        QTabBar#innerTabBar::tab {{ color: white; background: {accent}; padding: 8px 12px; margin: 0 5px 0 0; border: 1px solid {accent}; border-radius: 4px; min-width: 131px; min-height: 26px; font-size: 14px; font-weight: 600; }}
        QTabBar#innerTabBar::tab:selected {{ color: white; background: {navy}; border-color: {accent}; }}
        QTabBar#innerTabBar::tab:hover:!selected {{ color: white; background: {navy}; border-color: {navy}; }}
        QTabBar#innerTabBar::tab:disabled {{ color: #e2e7eb; background: #7d8994; border-color: #7d8994; }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ color: {text}; background: {base}; border: 1px solid {border}; border-radius: 0; }}
        QLineEdit {{ min-height: 42px; max-height: 42px; padding: 0 10px; }}
        QComboBox {{ min-height: 42px; max-height: 42px; padding: 0 32px 0 10px; }}
        QComboBox::drop-down {{ subcontrol-origin: border; subcontrol-position: top right; width: 32px; background: {navy}; border: 0; border-left: 1px solid #8a949e; }}
        QComboBox::drop-down:hover, QComboBox::drop-down:on {{ background: {accent}; }}
        QComboBox::down-arrow {{ image: url({step_down}); width: 12px; height: 8px; }}
        QComboBox QAbstractItemView {{ color: {text}; background: {base}; alternate-background-color: {alternate}; border: 1px solid {border}; outline: 0; padding: 4px; selection-color: white; selection-background-color: {accent}; }}
        QComboBox QAbstractItemView::item {{ min-height: 28px; padding: 4px 8px; }}
        QSpinBox, QDoubleSpinBox {{ min-height: 42px; max-height: 42px; padding: 0 34px 0 10px; }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{ subcontrol-origin: border; subcontrol-position: top right; width: 24px; height: 20px; background: {navy}; border: 0; border-left: 1px solid #8a949e; border-bottom: 1px solid #8a949e; }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{ subcontrol-origin: border; subcontrol-position: bottom right; width: 24px; height: 20px; background: {navy}; border: 0; border-left: 1px solid #8a949e; }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover, QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{ background: {accent}; }}
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{ image: url({step_up}); width: 12px; height: 8px; }}
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{ image: url({step_down}); width: 12px; height: 8px; }}
        QPlainTextEdit {{ color: {text}; background: {base}; border: 1px solid {border}; padding: 8px; }}
        QTableWidget {{ color: {text}; background: {base}; alternate-background-color: {alternate}; border: 1px solid {border}; border-radius: 0; gridline-color: {border}; selection-background-color: {navy}; selection-color: white; }}
        QTableWidget::item {{ border: 0; padding: 5px 8px; }}
        QTableWidget::item:hover {{ background: {hover}; color: {hover_text}; }}
        QHeaderView {{ color: {text}; background: {header}; }}
        QHeaderView::section, QTableCornerButton::section {{ color: {text}; background: {header}; font-weight: 600; padding: 7px; border: 0; border-right: 1px solid {border}; border-bottom: 1px solid {border}; }}
        QScrollBar:horizontal, QScrollBar:vertical {{ background: {panel}; border: 0; margin: 0; }}
        QScrollBar::handle:horizontal, QScrollBar::handle:vertical {{ background: {scroll_handle}; border-radius: 4px; min-width: 28px; min-height: 28px; }}
        QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; background: none; border: 0; }}
        QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ border: 1px solid {accent}; }}
        QGroupBox {{ color: {text}; background: {window}; font-weight: 600; border-color: {border}; }}
        QGroupBox::title {{ color: {text}; background: {window}; }}
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
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#12375b"))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#71899d"))
    palette.setColor(QPalette.ColorRole.Light, QColor("#315876"))
    palette.setColor(QPalette.ColorRole.Dark, QColor("#04101b"))
    palette.setColor(QPalette.ColorRole.Shadow, QColor("#02080d"))
    palette.setColor(QPalette.ColorRole.Mid, QColor("#285071"))
    palette.setColor(QPalette.ColorRole.Midlight, QColor("#1b405f"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#71899d"))
    return palette
