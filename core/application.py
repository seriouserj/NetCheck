"""
Version: 1.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Configure the persisted interface language before creating widgets.
"""

from __future__ import annotations

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from core.i18n import set_language
from core.metadata import APP_NAME, APP_VERSION, ORGANIZATION_NAME
from core.settings_store import SettingsStore
from ui.theme import apply_theme


def configure_application(application: QApplication) -> None:
    """Apply stable identity and platform-aware defaults to the Qt application."""
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(APP_VERSION)
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    font = application.font()
    font.setPointSize(13)
    application.setFont(font)
    settings = SettingsStore().load()
    set_language(settings.language)
    apply_theme(application, settings.theme.value)
