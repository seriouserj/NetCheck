"""
Version: 1.0.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: First stable application entry point.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 13):
    raise SystemExit("NetCheck requires Python 3.13 or newer.")

from PySide6.QtWidgets import QApplication

from core.application import configure_application
from ui.main_window import MainWindow


def main() -> int:
    """Start the NetCheck desktop application."""
    application = QApplication(sys.argv)
    configure_application(application)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
