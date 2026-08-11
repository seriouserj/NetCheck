"""
Version: 1.6.8
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Use the shared borderless primary navigation presentation.
"""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from core.i18n import tr
from core.metadata import APP_NAME
from ui.about_dialog import AboutDialog
from ui.brand_header import BrandHeader
from ui.dashboard_tab import DashboardTab
from ui.discovery_tab import DiscoveryTab
from ui.ports_tab import PortsTab
from ui.settings_tab import SettingsTab
from ui.tab_navigation import center_tab_group
from ui.tools_tab import ToolsTab
from ui.vlan_tab import VlanTab


class MainWindow(QMainWindow):
    """Top-level NetCheck application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 600)
        self.resize(1180, 760)
        help_menu = self.menuBar().addMenu(tr("Help"))
        about_action = help_menu.addAction(tr("About NetCheck"))
        about_action.triggered.connect(self._show_about)
        self._build_tabs()

    def _show_about(self) -> None:
        AboutDialog(self).exec()

    def _build_tabs(self) -> None:
        """Create all translated tabs from the current language."""
        tabs = QTabWidget()
        tabs.setObjectName("mainTabs")
        tabs.tabBar().setObjectName("mainTabBar")
        center_tab_group(tabs)
        tabs.addTab(DashboardTab(), tr("Dashboard"))
        tabs.addTab(VlanTab(), "VLAN")
        tabs.addTab(DiscoveryTab(), tr("Discovery"))
        tabs.addTab(PortsTab(), tr("Ports"))
        tabs.addTab(ToolsTab(), tr("Tools"))
        settings = SettingsTab()
        settings.settings_saved.connect(lambda _: QTimer.singleShot(0, self._build_tabs))
        tabs.addTab(settings, tr("Settings"))
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(BrandHeader())
        layout.addWidget(tabs)
        self.setCentralWidget(container)
