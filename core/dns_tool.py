"""
Version: 0.6.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add DNS record lookup through the macOS resolver.
"""

from __future__ import annotations

from core.command_runner import run_command


RECORD_TYPES = ("A", "AAAA", "CNAME", "MX", "NS", "PTR", "SOA", "TXT")


def dns_lookup(name: str, record_type: str = "A", server: str = "", timeout: float = 8.0) -> str:
    """Query a supported DNS record type with optional resolver override."""
    name = name.strip()
    record_type = record_type.upper().strip()
    if not name:
        raise ValueError("Enter a DNS name or address.")
    if record_type not in RECORD_TYPES:
        raise ValueError(f"Unsupported DNS record type: {record_type}")
    command = ["dig", "+noall", "+answer", f"+time={max(1, int(timeout))}"]
    if server.strip():
        command.append(f"@{server.strip()}")
    command.extend((name, record_type))
    result = run_command(tuple(command), timeout + 1)
    if result.return_code == 127:
        raise RuntimeError("The macOS dig utility is unavailable.")
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    return output or "No records returned."
