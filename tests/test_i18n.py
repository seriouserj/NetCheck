"""
Version: 1.2.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify translated VLAN progress and diagnostic messages.
"""

import pytest

from core.i18n import AppLanguage, set_language, tr


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (AppLanguage.ENGLISH, "Settings"),
        (AppLanguage.GERMAN, "Einstellungen"),
        (AppLanguage.RUSSIAN, "Настройки"),
        (AppLanguage.UKRAINIAN, "Налаштування"),
    ],
)
def test_translates_settings_tab(language: AppLanguage, expected: str) -> None:
    set_language(language)
    assert tr("Settings") == expected
    set_language(AppLanguage.ENGLISH)


def test_formats_translated_runtime_value() -> None:
    set_language(AppLanguage.RUSSIAN)
    assert tr("Testing {count} VLAN(s)…", count=4) == "Тестирование VLAN: 4…"
    set_language(AppLanguage.ENGLISH)


def test_unknown_text_falls_back_to_english_source() -> None:
    set_language(AppLanguage.GERMAN)
    assert tr("Vendor-specific status") == "Vendor-specific status"
    set_language(AppLanguage.ENGLISH)


def test_translates_vlan_progress_and_diagnostics() -> None:
    set_language(AppLanguage.RUSSIAN)
    assert tr("Completed {completed} of {total} VLAN tests", completed=2, total=4) == "Завершено VLAN-тестов: 2 из 4"
    assert tr("No DHCP lease") == "Нет аренды DHCP"
    set_language(AppLanguage.UKRAINIAN)
    assert tr("All core checks passed") == "Усі основні перевірки пройдено"
    set_language(AppLanguage.GERMAN)
    assert tr("Discover VLANs") == "VLANs erkennen"
    set_language(AppLanguage.ENGLISH)
