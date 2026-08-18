"""
Version: 1.9.2
Date: 2026-08-18
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Detect when passive packet capture specifically requires macOS privileges.
"""

from __future__ import annotations

from core.command_runner import CommandResult

_PERMISSION_ERRORS = (
    "permission denied",
    "operation not permitted",
    "you don't have permission",
    "no suitable device found",
    "/dev/bpf",
    "biocsetif",
)


def capture_requires_privileges(result: CommandResult) -> bool:
    """Return whether tcpdump failed because the capture device is inaccessible."""
    if result.return_code in (0, 124):
        return False
    detail = f"{result.stdout}\n{result.stderr}".casefold()
    return any(message in detail for message in _PERMISSION_ERRORS)
