"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Publish pytest failure details as GitHub Actions annotations.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.etree import ElementTree


def main() -> int:
    """Print concise annotations for failed test cases in a JUnit report."""
    report = Path(sys.argv[1] if len(sys.argv) > 1 else "test-results.xml")
    root = ElementTree.parse(report).getroot()
    failures = 0
    for case in root.iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is None:
            continue
        failures += 1
        name = f"{case.get('classname', 'pytest')}.{case.get('name', 'test')}"
        detail = (problem.text or problem.get("message") or "Test failed").strip()
        detail = detail.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error title={name}::{detail}")
    return 0 if failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
