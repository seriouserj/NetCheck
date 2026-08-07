"""
Version: 0.6.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add bounded ICMP ping execution.
"""

from __future__ import annotations

from core.command_runner import run_command


def ping(target: str, count: int = 4, timeout: float = 8.0) -> str:
    """Ping a target and return the complete diagnostic output."""
    target = target.strip()
    if not target:
        raise ValueError("Enter a ping target.")
    result = run_command(("ping", "-n", "-c", str(count), target), timeout)
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if not output:
        raise RuntimeError("Ping produced no output.")
    return output
