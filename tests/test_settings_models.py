"""
Version: 1.1.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify application language settings and validation.
"""

import pytest

from core.i18n import AppLanguage
from core.settings_models import AppSettings


def test_valid_settings() -> None:
    settings = AppSettings(timeout_seconds=2.5, preferred_dns="1.1.1.1", language=AppLanguage.UKRAINIAN).validate()
    assert settings.timeout_seconds == 2.5
    assert settings.language is AppLanguage.UKRAINIAN


@pytest.mark.parametrize("timeout", [0.0, 120.1])
def test_invalid_timeout(timeout: float) -> None:
    with pytest.raises(ValueError):
        AppSettings(timeout_seconds=timeout).validate()


def test_invalid_dns() -> None:
    with pytest.raises(ValueError):
        AppSettings(preferred_dns="not-an-address").validate()
