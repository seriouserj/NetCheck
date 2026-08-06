"""
Version: 0.3.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add safe macOS administrator command execution.
"""

from __future__ import annotations

import shlex
import json
from collections.abc import Sequence

from core.command_runner import CommandResult, run_command


def run_privileged(command: Sequence[str], timeout: float = 60.0) -> CommandResult:
    """Run an argument-safe command through the macOS authorization dialog."""
    shell_command = shlex.join(command)
    apple_script = f"do shell script {json.dumps(shell_command)} with administrator privileges"
    return run_command(("osascript", "-e", apple_script), timeout)
