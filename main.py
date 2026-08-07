"""
Version: 1.0.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add bundle-safe version and smoke-test command-line modes.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 13):
    raise SystemExit("NetCheck requires Python 3.13 or newer.")

from PySide6.QtWidgets import QApplication

from core.application import configure_application
from core.metadata import APP_VERSION
from ui.main_window import MainWindow


def main() -> int:
    """Start the NetCheck desktop application."""
    if "--version" in sys.argv:
        print(APP_VERSION)
        return 0
    application = QApplication(sys.argv)
    if "--smoke-test" in sys.argv:
        from ui.smoke import run_smoke_test

        return run_smoke_test(application)
    configure_application(application)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
