"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Use the native Windows DNS lookup utility without changing macOS behavior.
"""

from __future__ import annotations

from core.command_runner import run_command
from core.platform_commands import is_windows

RECORD_TYPES = ("A", "AAAA", "CNAME", "MX", "NS", "PTR", "SOA", "TXT")


def dns_lookup(name: str, record_type: str = "A", server: str = "", timeout: float = 8.0) -> str:
    """Query a supported DNS record type with optional resolver override."""
    name = name.strip()
    record_type = record_type.upper().strip()
    if not name:
        raise ValueError("Enter a DNS name or address.")
    if record_type not in RECORD_TYPES:
        raise ValueError(f"Unsupported DNS record type: {record_type}")
    if is_windows():
        command = ["nslookup", f"-type={record_type}", name]
        if server.strip():
            command.append(server.strip())
        result = run_command(tuple(command), timeout + 1)
        if result.return_code == 127:
            raise RuntimeError("The Windows nslookup utility is unavailable.")
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        return output or "No records returned."

    command = ["dig", "+noall", "+answer", f"+time={max(1, int(timeout))}"]
    if server.strip():
        command.append(f"@{server.strip()}")
    command.extend((name, record_type))
    result = run_command(tuple(command), timeout + 1)
    if result.return_code == 127:
        raise RuntimeError("The macOS dig utility is unavailable.")
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    return output or "No records returned."
