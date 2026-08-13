"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Detect VLAN controls exposed by Windows Ethernet adapter drivers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from core.command_runner import run_command


@dataclass(frozen=True, slots=True)
class VlanDriverProperty:
    """One VLAN-related advanced property exposed by a Windows driver."""

    display_name: str
    display_value: str
    registry_keyword: str


class WindowsVlanCapabilityService:
    """Inspect an adapter without changing its driver or network state."""

    def __init__(self, runner=run_command) -> None:
        self._run = runner

    def inspect(self, adapter: str, timeout: float = 15.0) -> list[VlanDriverProperty]:
        """Return VLAN-related driver properties for an adapter."""
        adapter = adapter.strip()
        if not adapter:
            raise ValueError("Select an Ethernet interface.")
        escaped = adapter.replace("'", "''")
        script = (
            f"Get-NetAdapterAdvancedProperty -Name '{escaped}' -AllProperties "
            "-ErrorAction Stop | Select-Object DisplayName,DisplayValue,RegistryKeyword | "
            "ConvertTo-Json -Depth 3 -Compress"
        )
        result = self._run(
            ("powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script),
            timeout,
        )
        if result.return_code != 0:
            raise RuntimeError(result.stderr or result.stdout or "Unable to inspect the adapter driver.")
        return parse_vlan_driver_properties(result.stdout)


def parse_vlan_driver_properties(payload: str) -> list[VlanDriverProperty]:
    """Decode and filter a PowerShell advanced-property response."""
    try:
        decoded = json.loads(payload or "[]")
    except json.JSONDecodeError as error:
        raise RuntimeError("Windows returned an invalid adapter property response.") from error
    items = decoded if isinstance(decoded, list) else [decoded]
    properties: list[VlanDriverProperty] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("DisplayName") or "").strip()
        value = str(item.get("DisplayValue") or "").strip()
        keyword = str(item.get("RegistryKeyword") or "").strip()
        if "vlan" not in f"{name} {keyword}".casefold():
            continue
        properties.append(VlanDriverProperty(name or keyword, value or "—", keyword or "—"))
    return properties
