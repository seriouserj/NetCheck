"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Provide one headless Qt application for cross-platform UI tests.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def qt_application() -> Iterator[QApplication]:
    """Keep one QApplication alive while tests exercise Qt documents and widgets."""
    application = QApplication.instance() or QApplication([])
    yield application
    application.processEvents()
