"""
Version: 0.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify semantic application metadata.
"""

import re

from core.metadata import APP_NAME, APP_VERSION


def test_application_metadata() -> None:
    assert APP_NAME == "NetCheck"
    assert re.fullmatch(r"\d+\.\d+\.\d+", APP_VERSION)
