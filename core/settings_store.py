"""
Version: 0.7.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add native persistent settings storage.
"""

from __future__ import annotations

from PySide6.QtCore import QSettings

from core.settings_models import AppSettings, ThemePreference


class SettingsStore:
    """Persist typed application settings through the platform-native backend."""

    def __init__(self, backend: QSettings | None = None) -> None:
        self._backend = backend or QSettings()

    def load(self) -> AppSettings:
        """Load settings and recover safely from invalid legacy values."""
        try:
            theme = ThemePreference(str(self._backend.value("appearance/theme", "system")))
        except ValueError:
            theme = ThemePreference.SYSTEM
        try:
            timeout = float(self._backend.value("network/timeout_seconds", 3.0))
        except (TypeError, ValueError):
            timeout = 3.0
        settings = AppSettings(
            timeout_seconds=min(120.0, max(0.1, timeout)),
            preferred_dns=str(self._backend.value("network/preferred_dns", "")),
            default_interface=str(self._backend.value("network/default_interface", "")),
            theme=theme,
        )
        try:
            return settings.validate()
        except ValueError:
            return AppSettings(timeout_seconds=settings.timeout_seconds, default_interface=settings.default_interface, theme=theme)

    def save(self, settings: AppSettings) -> None:
        """Validate and atomically synchronize current settings."""
        settings.validate()
        self._backend.setValue("network/timeout_seconds", settings.timeout_seconds)
        self._backend.setValue("network/preferred_dns", settings.preferred_dns)
        self._backend.setValue("network/default_interface", settings.default_interface)
        self._backend.setValue("appearance/theme", settings.theme.value)
        self._backend.sync()
        if self._backend.status() != QSettings.Status.NoError:
            raise OSError("The settings backend could not save the configuration.")
