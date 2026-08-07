"""
Version: 1.0.0
Date: 2026-08-07
Author: NetCheck Contributors
Changelog: Reuse the application bundle smoke validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.smoke import run_smoke_test  # noqa: E402


def main() -> int:
    """Run the shared smoke test against the source checkout."""
    application = QApplication([])
    return run_smoke_test(application)


if __name__ == "__main__":
    raise SystemExit(main())
