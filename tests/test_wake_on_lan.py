"""
Version: 0.6.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify Wake-on-LAN MAC address validation.
"""

import pytest

from core.wake_on_lan import normalize_mac_address


def test_normalize_mac_address() -> None:
    assert normalize_mac_address("AA:BB:cc:01:02:03") == "aabbcc010203"
    assert normalize_mac_address("AA-BB-CC-01-02-03") == "aabbcc010203"


def test_reject_invalid_mac_address() -> None:
    with pytest.raises(ValueError):
        normalize_mac_address("invalid")
