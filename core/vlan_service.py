"""
Version: 0.3.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add temporary macOS VLAN lifecycle and diagnostic checks.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable

from core.command_runner import CommandResult, run_command
from core.network_parsers import parse_default_gateway
from core.privileged_runner import run_privileged
from core.vlan_models import CheckState, VlanTestResult

Runner = Callable[[tuple[str, ...], float], CommandResult]


class VlanService:
    """Create, test, and always remove temporary macOS VLAN interfaces."""

    def __init__(self, runner: Runner = run_command, privileged_runner: Runner = run_privileged) -> None:
        self._run = runner
        self._run_privileged = privileged_runner

    def test(self, parent: str, vlan_id: int, timeout: float = 5.0) -> VlanTestResult:
        """Test one VLAN and remove its temporary interface on every exit path."""
        name = f"NetCheck VLAN {vlan_id}"
        created = self._run_privileged(
            ("/usr/sbin/networksetup", "-createVLAN", name, parent, str(vlan_id)), 60.0
        )
        if created.return_code != 0:
            return self._failed(vlan_id, created.stderr or created.stdout or "VLAN creation failed")
        try:
            device = self._find_device(parent, vlan_id, timeout)
            if not device:
                return self._failed(vlan_id, "macOS did not expose the temporary VLAN device")
            return self._run_checks(parent, device, vlan_id, timeout)
        finally:
            self._run_privileged(
                ("/usr/sbin/networksetup", "-deleteVLAN", name, parent, str(vlan_id)), 60.0
            )

    def _find_device(self, parent: str, vlan_id: int, timeout: float) -> str:
        devices = self._run(("ifconfig", "-l"), timeout)
        for device in devices.stdout.split():
            if not device.startswith("vlan"):
                continue
            details = self._run(("ifconfig", device), timeout)
            vlan_match = re.search(r"vlan:\s*(\d+).*parent interface:\s*(\S+)", details.stdout)
            if vlan_match and int(vlan_match.group(1)) == vlan_id and vlan_match.group(2) == parent:
                return device
        return ""

    def _run_checks(self, parent: str, device: str, vlan_id: int, timeout: float) -> VlanTestResult:
        parent_state = self._run(("ifconfig", parent), timeout)
        link = CheckState.PASS if re.search(r"status:\s*active", parent_state.stdout) else CheckState.FAIL
        self._run_privileged(("/usr/sbin/ipconfig", "set", device, "DHCP"), 60.0)
        address = self._wait_for_address(device, timeout)
        dhcp = CheckState.PASS if address else CheckState.FAIL

        route = self._run(("route", "-n", "get", "default", "-ifscope", device), timeout)
        gateway_address, _ = parse_default_gateway(route.stdout)
        gateway = self._check_ping(gateway_address, address, timeout) if gateway_address else CheckState.FAIL
        ping = self._check_ping("1.1.1.1", address, timeout) if address else CheckState.FAIL
        dns_result = self._run(("dscacheutil", "-q", "host", "-a", "name", "example.com"), timeout)
        dns = CheckState.PASS if dns_result.return_code == 0 and "ip_address:" in dns_result.stdout else CheckState.FAIL
        curl = self._run(("curl", "--interface", device, "--silent", "--fail", "--max-time", str(timeout), "https://connectivitycheck.gstatic.com/generate_204"), timeout + 1)
        internet = CheckState.PASS if curl.return_code == 0 else CheckState.FAIL
        lldp = self._check_lldp(device, min(timeout, 3.0))
        failures = sum(state is CheckState.FAIL for state in (link, dhcp, gateway, dns, internet, ping))
        return VlanTestResult(
            vlan_id, link, dhcp, gateway, dns, internet, ping, lldp, address, gateway_address,
            "All core checks passed" if failures == 0 else f"{failures} core check(s) failed",
        )

    def _wait_for_address(self, device: str, timeout: float) -> str:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = self._run(("ipconfig", "getifaddr", device), 2.0)
            if result.return_code == 0 and result.stdout:
                return result.stdout.splitlines()[0].strip()
            time.sleep(0.25)
        return ""

    def _check_ping(self, target: str, source_address: str, timeout: float) -> CheckState:
        if not target:
            return CheckState.FAIL
        result = self._run(("ping", "-c", "1", "-W", str(int(timeout * 1000)), "-S", source_address, target), timeout + 1)
        return CheckState.PASS if result.return_code == 0 else CheckState.FAIL

    def _check_lldp(self, device: str, timeout: float) -> CheckState:
        if self._run(("which", "tcpdump"), 2.0).return_code != 0:
            return CheckState.UNAVAILABLE
        result = self._run_privileged(
            ("/usr/sbin/tcpdump", "-i", device, "-c", "1", "-G", str(max(1, int(timeout))), "ether", "proto", "0x88cc"),
            timeout + 15,
        )
        return CheckState.PASS if result.return_code == 0 else CheckState.WARNING

    @staticmethod
    def _failed(vlan_id: int, detail: str) -> VlanTestResult:
        return VlanTestResult(vlan_id, *(CheckState.FAIL for _ in range(6)), CheckState.UNAVAILABLE, detail=detail)
