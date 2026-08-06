"""
Version: 0.7.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Load and apply the persisted theme preference.
"""

from __future__ import annotations

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from core.metadata import APP_NAME, APP_VERSION, ORGANIZATION_NAME
from core.settings_store import SettingsStore
from ui.theme import apply_theme


def configure_application(application: QApplication) -> None:
    """Apply stable identity and platform-aware defaults to the Qt application."""
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(APP_VERSION)
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    application.setFont(QFont("SF Pro Text", 13))
    apply_theme(application, SettingsStore().load().theme.value)
