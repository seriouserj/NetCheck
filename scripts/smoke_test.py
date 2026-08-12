"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Publish smoke-test exceptions as GitHub Actions annotations.
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
    try:
        return run_smoke_test(application)
    except Exception as error:
        detail = str(error).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error title=NetCheck UI smoke test::{detail}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
