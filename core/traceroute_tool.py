"""
Version: 0.6.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add bounded route tracing.
"""

from __future__ import annotations

from core.command_runner import run_command


def traceroute(target: str, maximum_hops: int = 30, timeout: float = 45.0) -> str:
    """Trace the route to a hostname or IP address."""
    target = target.strip()
    if not target:
        raise ValueError("Enter a traceroute target.")
    result = run_command(("traceroute", "-n", "-m", str(maximum_hops), target), timeout)
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if not output:
        raise RuntimeError("Traceroute produced no output.")
    return output
