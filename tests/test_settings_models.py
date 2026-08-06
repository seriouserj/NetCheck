"""
Version: 0.7.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify application settings validation.
"""

import pytest

from core.settings_models import AppSettings


def test_valid_settings() -> None:
    assert AppSettings(timeout_seconds=2.5, preferred_dns="1.1.1.1").validate().timeout_seconds == 2.5


@pytest.mark.parametrize("timeout", [0.0, 120.1])
def test_invalid_timeout(timeout: float) -> None:
    with pytest.raises(ValueError):
        AppSettings(timeout_seconds=timeout).validate()


def test_invalid_dns() -> None:
    with pytest.raises(ValueError):
        AppSettings(preferred_dns="not-an-address").validate()
