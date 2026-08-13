"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Suppress Windows console windows and tolerate localized command output.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Captured result of a system command."""

    return_code: int
    stdout: str
    stderr: str


def run_command(command: Sequence[str], timeout: float = 5.0) -> CommandResult:
    """Run a command without a shell and return a normalized result."""
    try:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            check=False,
            text=True,
            errors="replace",
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired) as error:
        return CommandResult(127, "", str(error))
    return CommandResult(completed.returncode, completed.stdout.strip(), completed.stderr.strip())
