"""
Version: 0.5.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add strict TCP port list and range parsing.
"""

from __future__ import annotations

import re


def parse_ports(expression: str, maximum_ports: int = 4096) -> tuple[int, ...]:
    """Parse comma-separated ports and inclusive ranges safely."""
    if not expression.strip():
        raise ValueError("Enter at least one TCP port.")
    ports: set[int] = set()
    for token in expression.split(","):
        token = token.strip()
        match = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", token)
        if not match:
            raise ValueError(f"Invalid port token: {token or 'empty value'}")
        start, end = int(match.group(1)), int(match.group(2) or match.group(1))
        if start > end:
            raise ValueError(f"Port range starts after it ends: {token}")
        if start < 1 or end > 65535:
            raise ValueError("Ports must be between 1 and 65535.")
        ports.update(range(start, end + 1))
        if len(ports) > maximum_ports:
            raise ValueError(f"One scan is limited to {maximum_ports} ports.")
    return tuple(sorted(ports))
