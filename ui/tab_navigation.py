"""
Version: 1.6.8
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Remove the native dark tab-row base while preserving centered groups.
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
    """Center a compact tab group without the native document-mode background."""
    tabs.setDocumentMode(False)
    tabs.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    bar = tabs.tabBar()
    bar.setExpanding(False)
    bar.setDrawBase(False)
    bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    style = _CenteredTabStyle()
    style.setParent(bar)
    bar.setStyle(style)
