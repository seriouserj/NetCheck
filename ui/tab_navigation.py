"""
Version: 1.6.4
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Center fixed-width Qt tab groups independently of interface language.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QProxyStyle,
    QStyle,
    QStyleHintReturn,
    QStyleOption,
    QTabWidget,
    QWidget,
)


class _CenteredTabStyle(QProxyStyle):
    """Override only the native tab-bar alignment hint."""

    def styleHint(
        self,
        hint: QStyle.StyleHint,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
        return_data: QStyleHintReturn | None = None,
    ) -> int:
        if hint == QStyle.StyleHint.SH_TabBar_Alignment:
            return Qt.AlignmentFlag.AlignCenter.value
        return super().styleHint(hint, option, widget, return_data)


def center_tab_group(tabs: QTabWidget) -> None:
    """Keep a tab group at its natural width and center it in the tab row."""
    bar = tabs.tabBar()
    bar.setExpanding(False)
    style = _CenteredTabStyle()
    style.setParent(bar)
    bar.setStyle(style)
