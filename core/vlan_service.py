"""
Version: 1.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Run multi-VLAN diagnostics through one administrator authorization.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

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

    def test_many(
        self, parent: str, vlan_ids: list[int], timeout: float = 5.0
    ) -> list[VlanTestResult]:
        """Run a complete VLAN batch in one authorized worker process."""
        if not vlan_ids:
            return []
        with tempfile.NamedTemporaryFile(prefix="netcheck-vlan-", suffix=".json") as output:
            command = self._worker_command(parent, vlan_ids, timeout, output.name)
            batch_timeout = max(120.0, len(vlan_ids) * (timeout * 6.0 + 30.0))
            completed = self._run_privileged(command, batch_timeout)
            if completed.return_code != 0:
                detail = completed.stderr or completed.stdout or "Administrator authorization failed"
                if "-128" in detail or "canceled" in detail.casefold() or "abgebrochen" in detail.casefold():
                    detail = "Administrator authorization was canceled; no further VLANs were tested."
                return [self._failed(vlan_id, detail) for vlan_id in vlan_ids]
            output.seek(0)
            response = output.read()
        try:
            payload = json.loads(response)
            if not isinstance(payload, list):
                raise ValueError("worker response is not a list")
            results = [VlanTestResult.from_payload(item) for item in payload if isinstance(item, dict)]
        except (KeyError, TypeError, ValueError) as error:
            detail = f"Invalid response from the VLAN worker: {error}"
            return [self._failed(vlan_id, detail) for vlan_id in vlan_ids]
        if len(results) != len(vlan_ids):
            detail = "The VLAN worker returned an incomplete result set."
            return [self._failed(vlan_id, detail) for vlan_id in vlan_ids]
        return results

    @staticmethod
    def _worker_command(
        parent: str, vlan_ids: list[int], timeout: float, output_path: str
    ) -> tuple[str, ...]:
        arguments = (
            "--vlan-worker",
            parent,
            ",".join(str(item) for item in vlan_ids),
            str(timeout),
            output_path,
        )
        if getattr(sys, "frozen", False):
            return (sys.executable, *arguments)
        main_script = Path(__file__).resolve().parents[1] / "main.py"
        return (sys.executable, str(main_script), *arguments)

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
