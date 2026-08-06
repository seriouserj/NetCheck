"""
Version: 0.2.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add bounded subprocess execution for system diagnostics.
"""

from __future__ import annotations

import subprocess
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
            timeout=timeout,
        )
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired) as error:
        return CommandResult(127, "", str(error))
    return CommandResult(completed.returncode, completed.stdout.strip(), completed.stderr.strip())
