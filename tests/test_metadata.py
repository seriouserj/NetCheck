"""
Version: 1.1.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify semantic version and visible author metadata.
"""

import re

from core.metadata import APP_NAME, APP_VERSION, AUTHOR_EMAIL, AUTHOR_NAME


def test_application_metadata() -> None:
    assert APP_NAME == "NetCheck"
    assert re.fullmatch(r"\d+\.\d+\.\d+", APP_VERSION)
    assert AUTHOR_NAME == "Serhii Dralo"
    assert AUTHOR_EMAIL == "dralo@ditis.group"
