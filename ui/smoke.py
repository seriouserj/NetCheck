"""
Version: 1.6.2
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Validate click-to-copy behavior in result tables.
"""

from __future__ import annotations

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QTabWidget

from core.application import configure_application
from core.i18n import tr
from ui.brand_header import BrandHeader
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
    copy_table = HoverRowTableWidget(1, 1)
    copy_table.setItem(0, 0, QTableWidgetItem("192.0.2.1"))
    copy_table.cellClicked.emit(0, 0)
    if application.clipboard().text() != "192.0.2.1":
        raise RuntimeError("Clicking a result cell must copy its exact value.")
    copy_table.close()
    QThreadPool.globalInstance().waitForDone(15_000)
    application.processEvents()
    window.close()
    return 0
