"""
Version: 1.3.1
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Apply the compact segmented style to settings navigation.
"""

from __future__ import annotations

import psutil
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.i18n import AppLanguage, set_language, tr
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
        tabs.setObjectName("innerTabs")
        tabs.tabBar().setObjectName("innerTabBar")
        tabs.setDocumentMode(True)
        general = QWidget()
        layout = QVBoxLayout(general)
        layout.setContentsMargins(24, 24, 24, 24)
        form = QFormLayout()
        self._timeout = QDoubleSpinBox()
        self._timeout.setRange(0.1, 120.0)
        self._timeout.setDecimals(1)
        self._timeout.setSuffix(" seconds")
        self._dns = QLineEdit()
        self._dns.setPlaceholderText(tr("Optional IPv4 or IPv6 address"))
        self._interface = QComboBox()
        self._interface.addItem(tr("Automatic"), "")
        for name in sorted(psutil.net_if_addrs()):
            self._interface.addItem(name, name)
        self._theme = QComboBox()
        self._theme.addItem(tr("System"), ThemePreference.SYSTEM.value)
        self._theme.addItem(tr("Light"), ThemePreference.LIGHT.value)
        self._theme.addItem(tr("Dark"), ThemePreference.DARK.value)
        self._language = QComboBox()
        self._language.addItem(tr("English"), AppLanguage.ENGLISH.value)
        self._language.addItem(tr("German"), AppLanguage.GERMAN.value)
        self._language.addItem(tr("Russian"), AppLanguage.RUSSIAN.value)
        self._language.addItem(tr("Ukrainian"), AppLanguage.UKRAINIAN.value)
        form.addRow(tr("Default timeout"), self._timeout)
        form.addRow(tr("Preferred DNS"), self._dns)
        form.addRow(tr("Default interface"), self._interface)
        form.addRow(tr("Theme"), self._theme)
        form.addRow(tr("Language"), self._language)
        self._status = QLabel("")
        self._status.setObjectName("mutedLabel")
        save = QPushButton(tr("Save settings"))
        save.setProperty("primary", True)
        save.setMinimumWidth(240)
        save.setMaximumWidth(360)
        save.clicked.connect(self._save)
        save_row = QHBoxLayout()
        save_row.setContentsMargins(30, 0, 30, 0)
        save_row.addStretch()
        save_row.addWidget(save)
        save_row.addStretch()
        layout.addLayout(form)
        layout.addLayout(save_row)
        layout.addWidget(self._status)
        layout.addStretch()
        tabs.addTab(general, tr("General"))
        tabs.addTab(ProfilesPanel(), tr("Profiles"))
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
        language_index = self._language.findData(settings.language.value)
        self._language.setCurrentIndex(max(0, language_index))

    def _save(self) -> None:
        settings = AppSettings(
            timeout_seconds=self._timeout.value(),
            preferred_dns=self._dns.text().strip(),
            default_interface=str(self._interface.currentData()),
            theme=ThemePreference(str(self._theme.currentData())),
            language=AppLanguage(str(self._language.currentData())),
        )
        try:
            self._store.save(settings)
        except (ValueError, OSError) as error:
            self._status.setText(f"Error: {error}")
            return
        application = QApplication.instance()
        if isinstance(application, QApplication):
            apply_theme(application, settings.theme.value)
        set_language(settings.language)
        self._status.setText(tr("Settings saved."))
        self.settings_saved.emit(settings)
