"""
Version: 0.8.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Integrate General settings and Profiles panels.
"""

from __future__ import annotations

import psutil
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.settings_models import AppSettings, ThemePreference
from core.settings_store import SettingsStore
from ui.profiles_panel import ProfilesPanel
from ui.theme import apply_theme


class SettingsTab(QWidget):
    """Edit validated diagnostic defaults and application appearance."""

    settings_saved = Signal(object)

    def __init__(self, store: SettingsStore | None = None) -> None:
        super().__init__()
        self._store = store or SettingsStore()
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        tabs = QTabWidget()
        general = QWidget()
        layout = QVBoxLayout(general)
        layout.setContentsMargins(24, 24, 24, 24)
        form = QFormLayout()
        self._timeout = QDoubleSpinBox()
        self._timeout.setRange(0.1, 120.0)
        self._timeout.setDecimals(1)
        self._timeout.setSuffix(" seconds")
        self._dns = QLineEdit()
        self._dns.setPlaceholderText("Optional IPv4 or IPv6 address")
        self._interface = QComboBox()
        self._interface.addItem("Automatic", "")
        for name in sorted(psutil.net_if_addrs()):
            self._interface.addItem(name, name)
        self._theme = QComboBox()
        self._theme.addItem("System", ThemePreference.SYSTEM.value)
        self._theme.addItem("Light", ThemePreference.LIGHT.value)
        self._theme.addItem("Dark", ThemePreference.DARK.value)
        form.addRow("Default timeout", self._timeout)
        form.addRow("Preferred DNS", self._dns)
        form.addRow("Default interface", self._interface)
        form.addRow("Theme", self._theme)
        self._status = QLabel("")
        self._status.setObjectName("mutedLabel")
        save = QPushButton("Save settings")
        save.clicked.connect(self._save)
        layout.addLayout(form)
        layout.addWidget(save)
        layout.addWidget(self._status)
        layout.addStretch()
        tabs.addTab(general, "General")
        tabs.addTab(ProfilesPanel(), "Profiles")
        root_layout.addWidget(tabs)
        self._load()

    def _load(self) -> None:
        settings = self._store.load()
        self._timeout.setValue(settings.timeout_seconds)
        self._dns.setText(settings.preferred_dns)
        interface_index = self._interface.findData(settings.default_interface)
        self._interface.setCurrentIndex(max(0, interface_index))
        theme_index = self._theme.findData(settings.theme.value)
        self._theme.setCurrentIndex(max(0, theme_index))

    def _save(self) -> None:
        settings = AppSettings(
            timeout_seconds=self._timeout.value(),
            preferred_dns=self._dns.text().strip(),
            default_interface=str(self._interface.currentData()),
            theme=ThemePreference(str(self._theme.currentData())),
        )
        try:
            self._store.save(settings)
        except (ValueError, OSError) as error:
            self._status.setText(f"Error: {error}")
            return
        application = QApplication.instance()
        if isinstance(application, QApplication):
            apply_theme(application, settings.theme.value)
        self._status.setText("Settings saved.")
        self.settings_saved.emit(settings)
