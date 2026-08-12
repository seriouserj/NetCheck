"""
Version: 1.8.1
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Validate the layered aurora activity indicator and product wordmark.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStyle,
    QStyleOptionSpinBox,
    QTableWidgetItem,
    QTabWidget,
)

from core.application import configure_application
from core.i18n import tr
from ui.activity import activity_tracker
from ui.brand_header import ActivityStrip, BrandHeader
from ui.form_layout import CONTROL_HEIGHT, centered_form
from ui.hover_table import HoverRowTableWidget
from ui.main_window import MainWindow
from ui.settings_tab import SettingsTab
from ui.tools_tab import ToolsTab

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
    activity_strip = window.findChild(ActivityStrip)
    if activity_strip is None or activity_strip.height() != 3:
        raise RuntimeError("Brand header must contain a three-pixel activity divider.")
    QThreadPool.globalInstance().waitForDone(15_000)
    application.processEvents()
    tracker = activity_tracker()
    was_busy = tracker.busy
    if not was_busy:
        tracker.begin()
        application.processEvents()
        if not activity_strip.animating:
            raise RuntimeError("Brand divider must animate during background activity.")
        tracker.end()
        application.processEvents()
        if activity_strip.animating:
            raise RuntimeError("Brand divider must stop animating when activity settles.")
    central_layout = window.centralWidget().layout() if window.centralWidget() else None
    if central_layout is None or central_layout.spacing() != 15:
        raise RuntimeError("Primary navigation must have 15 pixels of top spacing.")
    actual_tabs = tuple(tabs.tabText(index) for index in range(tabs.count()))
    expected_tabs = tuple(tr(item) if item != "VLAN" else item for item in EXPECTED_TABS)
    if actual_tabs != expected_tabs:
        raise RuntimeError(f"Unexpected application tabs: {actual_tabs}")
    for tab_widget in window.findChildren(QTabWidget):
        if tab_widget.objectName() not in {"mainTabs", "innerTabs"}:
            continue
        alignment = (
            tab_widget.tabBar()
            .style()
            .styleHint(
                QStyle.StyleHint.SH_TabBar_Alignment,
                None,
                tab_widget.tabBar(),
                None,
            )
        )
        if alignment != Qt.AlignmentFlag.AlignCenter.value:
            raise RuntimeError("Every navigation tab group must be centered.")
        if tab_widget.documentMode() or tab_widget.tabBar().drawBase():
            raise RuntimeError("Navigation must not draw a native grey tab-row base.")
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
    probe = QLabel("Field")
    form.addRow("Probe", probe)
    label_item = form.itemAt(0, QFormLayout.ItemRole.LabelRole)
    label = label_item.widget() if label_item is not None else None
    if not isinstance(label, QLabel):
        raise RuntimeError("Form rows must use explicit QLabel widgets.")
    if label.minimumHeight() != CONTROL_HEIGHT or label.maximumHeight() != CONTROL_HEIGHT:
        raise RuntimeError("Form labels must match the themed control height.")
    if not label.alignment() & Qt.AlignmentFlag.AlignVCenter:
        raise RuntimeError("Every explicit form label must be vertically centered.")
    wide_form = centered_form(grow_fields=True)
    spin_box = QSpinBox()
    wide_form.addRow("Value", spin_box)
    if spin_box.sizePolicy().horizontalPolicy() != QSizePolicy.Policy.Expanding:
        raise RuntimeError("Spin boxes in wide forms must align with line edits.")
    spin_box.resize(300, 42)
    spin_box.ensurePolished()
    spin_option = QStyleOptionSpinBox()
    spin_box.initStyleOption(spin_option)
    stepper = spin_box.style().subControlRect(
        QStyle.ComplexControl.CC_SpinBox,
        spin_option,
        QStyle.SubControl.SC_SpinBoxUp,
        spin_box,
    )
    if stepper.width() < 24:
        raise RuntimeError("Numeric stepper buttons must be at least 24 pixels wide.")
    for panel_type in (ToolsTab, SettingsTab):
        panel = window.findChild(panel_type)
        if panel is None or panel.layout().contentsMargins().top() != 18:
            raise RuntimeError("Secondary navigation must have an 18-pixel top gap.")
    if "QTabWidget#innerTabs::pane" not in application.styleSheet() or "top: 15px" not in application.styleSheet():
        raise RuntimeError("Secondary navigation must have 15 pixels below its tabs.")
    style_sheet = application.styleSheet()
    if "QLabel#brandProduct { color: white; font-size: 26px" not in style_sheet:
        raise RuntimeError("NetCheck wordmark must match the two-line author block height.")
    if "QPushButton { color: white" not in style_sheet or "background: #05285a" not in style_sheet:
        raise RuntimeError("Action buttons must use the navy brand surface by default.")
    if "QPushButton:hover { color: white; background: #009fe3" not in style_sheet:
        raise RuntimeError("Action buttons must use the cyan brand surface on hover.")
    if "QPushButton:disabled { color: #b8e8fa; background: #173c67" not in style_sheet:
        raise RuntimeError("Disabled action buttons must remain legible and navy rather than grey.")
    if "QTabBar#mainTabBar::tab:selected { color: white; background: #009fe3" not in style_sheet:
        raise RuntimeError("Active primary navigation must match its cyan hover state.")
    if "QTabBar#innerTabBar::tab { color: white; background: #009fe3" not in style_sheet:
        raise RuntimeError("Secondary navigation must use the reversed cyan default state.")
    if "QTabBar#innerTabBar::tab:hover:!selected { color: white; background: #05285a" not in style_sheet:
        raise RuntimeError("Secondary navigation must use the reversed navy hover state.")
    if "QTabBar#innerTabBar::tab:selected { color: white; background: #05285a" not in style_sheet:
        raise RuntimeError("Active secondary navigation must match its navy hover state.")
    if "QComboBox::drop-down {" not in style_sheet or "QComboBox::down-arrow { image:" not in style_sheet:
        raise RuntimeError("Combo boxes must use a branded drop-down button and white arrow.")
    if "QComboBox QAbstractItemView {" not in style_sheet:
        raise RuntimeError("Combo-box popup lists must use the application palette.")
    for object_name in (
        "scanButton",
        "copyReportButton",
        "exportTXTButton",
        "exportPDFButton",
        "exportSVGButton",
        "wakeButton",
    ):
        action = window.findChild(QPushButton, object_name)
        if action is None or action.icon().isNull():
            raise RuntimeError(f"Action button must have an icon: {object_name}")
    QThreadPool.globalInstance().waitForDone(15_000)
    application.processEvents()
    window.close()
    return 0
