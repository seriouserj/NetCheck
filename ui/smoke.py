"""
Version: 1.6.4
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Validate centered primary and nested tab navigation.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import QApplication, QStyle, QTableWidgetItem, QTabWidget

from core.application import configure_application
from core.i18n import tr
from ui.brand_header import BrandHeader
from ui.form_layout import centered_form
from ui.hover_table import HoverRowTableWidget
from ui.main_window import MainWindow

EXPECTED_TABS = ("Dashboard", "VLAN", "Discovery", "Ports", "Tools", "Settings")


def run_smoke_test(application: QApplication) -> int:
    """Construct the complete UI and validate its top-level navigation."""
    configure_application(application)
    window = MainWindow()
    tabs = window.findChild(QTabWidget)
    if tabs is None:
        raise RuntimeError("MainWindow must contain a QTabWidget.")
    if window.findChild(BrandHeader) is None:
        raise RuntimeError("MainWindow must contain the DITIS brand header.")
    actual_tabs = tuple(tabs.tabText(index) for index in range(tabs.count()))
    expected_tabs = tuple(tr(item) if item != "VLAN" else item for item in EXPECTED_TABS)
    if actual_tabs != expected_tabs:
        raise RuntimeError(f"Unexpected application tabs: {actual_tabs}")
    for tab_widget in window.findChildren(QTabWidget):
        if tab_widget.objectName() not in {"mainTabs", "innerTabs"}:
            continue
        alignment = tab_widget.tabBar().style().styleHint(
            QStyle.StyleHint.SH_TabBar_Alignment,
            None,
            tab_widget.tabBar(),
            None,
        )
        if alignment != Qt.AlignmentFlag.AlignCenter.value:
            raise RuntimeError("Every navigation tab group must be centered.")
    copy_table = HoverRowTableWidget(1, 1)
    copy_table.setItem(0, 0, QTableWidgetItem("192.0.2.1"))
    copy_table.cellClicked.emit(0, 0)
    if application.clipboard().text() != "192.0.2.1":
        raise RuntimeError("Clicking a result cell must copy its exact value.")
    copy_table.close()
    form = centered_form()
    if not form.formAlignment() & Qt.AlignmentFlag.AlignVCenter:
        raise RuntimeError("Diagnostic forms must be vertically centered.")
    if not form.labelAlignment() & Qt.AlignmentFlag.AlignVCenter:
        raise RuntimeError("Form labels must be centered beside their fields.")
    QThreadPool.globalInstance().waitForDone(15_000)
    application.processEvents()
    window.close()
    return 0
