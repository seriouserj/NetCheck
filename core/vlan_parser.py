"""
Version: 0.3.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add strict VLAN range and networksetup output parsing.
"""

from __future__ import annotations

import re


def parse_vlan_ids(expression: str) -> tuple[int, ...]:
    """Parse comma-separated VLAN IDs and inclusive ranges."""
    if not expression.strip():
        raise ValueError("Enter at least one VLAN ID.")
    values: set[int] = set()
    for token in expression.split(","):
        token = token.strip()
        match = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", token)
        if not match:
            raise ValueError(f"Invalid VLAN token: {token or 'empty value'}")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start > end:
            raise ValueError(f"VLAN range starts after it ends: {token}")
        if start < 1 or end > 4094:
            raise ValueError("VLAN IDs must be between 1 and 4094.")
        values.update(range(start, end + 1))
    return tuple(sorted(values))


def parse_vlan_devices(output: str) -> dict[tuple[str, int], str]:
    """Return parent/tag-to-device mappings from networksetup VLAN output."""
    mappings: dict[tuple[str, int], str] = {}
    blocks = re.split(r"\n\s*\n", output.strip())
    for block in blocks:
        device = re.search(r"(?:VLAN )?Device:\s*(\S+)", block, re.IGNORECASE)
        parent = re.search(r"Parent Device:\s*(\S+)", block, re.IGNORECASE)
        tag = re.search(r"Tag:\s*(\d+)", block, re.IGNORECASE)
        if device and parent and tag:
            mappings[(parent.group(1), int(tag.group(1)))] = device.group(1)
    return mappings
