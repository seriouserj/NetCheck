"""
Version: 1.2.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Stabilize sequential DHCP tests and stream completed VLAN results.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from core.command_runner import CommandResult, run_command
from core.network_parsers import parse_default_gateway
from core.privileged_runner import run_privileged
from core.vlan_models import CheckState, VlanTestResult

Runner = Callable[[tuple[str, ...], float], CommandResult]
ProgressCallback = Callable[[VlanTestResult], None]


class VlanService:
    """Create, test, and always remove temporary macOS VLAN interfaces."""

    def __init__(self, runner: Runner = run_command, privileged_runner: Runner = run_privileged) -> None:
        self._run = runner
        self._run_privileged = privileged_runner

    def test(self, parent: str, vlan_id: int, timeout: float = 5.0) -> VlanTestResult:
        """Test one VLAN and remove its temporary interface on every exit path."""
        name = f"NetCheck-{os.getpid()}-{uuid4().hex[:8]}-{vlan_id}"
        created = self._run_privileged(
            ("/usr/sbin/networksetup", "-createVLAN", name, parent, str(vlan_id)), 60.0
        )
        if created.return_code != 0:
            return self._failed(vlan_id, created.stderr or created.stdout or "VLAN creation failed")
        device = ""
        try:
            device = self._find_device(parent, vlan_id, timeout)
            if not device:
                return self._failed(vlan_id, "macOS did not expose the temporary VLAN device")
            return self._run_checks(parent, device, vlan_id, timeout)
        finally:
            if device:
                self._run_privileged(("/usr/sbin/ipconfig", "set", device, "NONE"), 10.0)
                self._run_privileged(("/sbin/ifconfig", device, "down"), 10.0)
            self._run_privileged(
                ("/usr/sbin/networksetup", "-deleteVLAN", name, parent, str(vlan_id)), 60.0
            )

    def test_many(
        self,
        parent: str,
        vlan_ids: list[int],
        timeout: float = 5.0,
        progress: ProgressCallback | None = None,
    ) -> list[VlanTestResult]:
        """Run a complete VLAN batch in one authorized worker process."""
        if not vlan_ids:
            return []
        with tempfile.NamedTemporaryFile(prefix="netcheck-vlan-", suffix=".json") as output:
            Path(output.name).write_text("[]", encoding="utf-8")
            command = self._worker_command(parent, vlan_ids, timeout, output.name)
            batch_timeout = max(120.0, len(vlan_ids) * (max(10.0, timeout * 2.0) + 20.0))
            reported = 0
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_privileged, command, batch_timeout)
                while not future.done():
                    reported = self._report_progress(output.name, reported, progress)
                    time.sleep(0.1)
                completed = future.result()
            reported = self._report_progress(output.name, reported, progress)
            if completed.return_code != 0:
                detail = completed.stderr or completed.stdout or "Administrator authorization failed"
                if "-128" in detail or "canceled" in detail.casefold() or "abgebrochen" in detail.casefold():
                    detail = "Administrator authorization was canceled; no further VLANs were tested."
                return [self._failed(vlan_id, detail) for vlan_id in vlan_ids]
            response = Path(output.name).read_bytes()
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
    def _report_progress(
        output_path: str, reported: int, progress: ProgressCallback | None
    ) -> int:
        """Emit every complete worker result once while tolerating partial writes."""
        if progress is None:
            return reported
        try:
            payload = json.loads(Path(output_path).read_text(encoding="utf-8"))
            results = [
                VlanTestResult.from_payload(item)
                for item in payload
                if isinstance(item, dict)
            ]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return reported
        for result in results[reported:]:
            progress(result)
        return max(reported, len(results))

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
        with ThreadPoolExecutor(max_workers=4) as executor:
            lldp_future = executor.submit(self._check_lldp, device, min(timeout, 3.0))
            self._run_privileged(("/usr/sbin/ipconfig", "set", device, "NONE"), 10.0)
            self._run_privileged(("/sbin/ifconfig", device, "up"), 10.0)
            time.sleep(0.25)
            self._run_privileged(("/usr/sbin/ipconfig", "set", device, "DHCP"), 60.0)
            dhcp_timeout = min(30.0, max(10.0, timeout * 2.0))
            address = self._wait_for_address(device, dhcp_timeout)
            dhcp = CheckState.PASS if address else CheckState.FAIL

            gateway_address = self._wait_for_gateway(device, min(4.0, timeout)) if address else ""
            gateway_future = executor.submit(self._check_ping, gateway_address, address, timeout)
            ping_future = executor.submit(self._check_ping, "1.1.1.1", address, timeout)
            dns_future = executor.submit(self._check_dns, address, timeout)
            internet_future = executor.submit(self._check_internet, device, address, timeout)
            gateway = gateway_future.result()
            ping = ping_future.result()
            dns = dns_future.result()
            internet = internet_future.result()
            lldp = lldp_future.result()
        failures = sum(state is CheckState.FAIL for state in (link, dhcp, gateway, dns, internet, ping))
        return VlanTestResult(
            vlan_id, link, dhcp, gateway, dns, internet, ping, lldp, address, gateway_address,
            "All core checks passed" if failures == 0 else f"{failures} core check(s) failed",
        )

    def _wait_for_gateway(self, device: str, timeout: float) -> str:
        deadline = time.monotonic() + max(0.5, timeout)
        while time.monotonic() < deadline:
            route = self._run(("route", "-n", "get", "default", "-ifscope", device), 2.0)
            gateway, _ = parse_default_gateway(route.stdout)
            if gateway:
                return gateway
            time.sleep(0.2)
        return ""

    def _wait_for_address(self, device: str, timeout: float) -> str:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = self._run(("ipconfig", "getifaddr", device), 2.0)
            if result.return_code == 0 and result.stdout:
                return result.stdout.splitlines()[0].strip()
            time.sleep(0.25)
        return ""

    def _check_ping(self, target: str, source_address: str, timeout: float) -> CheckState:
        if not target or not source_address:
            return CheckState.FAIL
        result = self._run(("ping", "-c", "1", "-W", str(int(timeout * 1000)), "-S", source_address, target), timeout + 1)
        return CheckState.PASS if result.return_code == 0 else CheckState.FAIL

    def _check_dns(self, source_address: str, timeout: float) -> CheckState:
        if not source_address:
            return CheckState.FAIL
        result = self._run(("dscacheutil", "-q", "host", "-a", "name", "example.com"), timeout)
        return CheckState.PASS if result.return_code == 0 and "ip_address:" in result.stdout else CheckState.FAIL

    def _check_internet(self, device: str, source_address: str, timeout: float) -> CheckState:
        if not source_address:
            return CheckState.FAIL
        result = self._run(
            (
                "curl", "--interface", device, "--silent", "--fail", "--max-time",
                str(timeout), "https://connectivitycheck.gstatic.com/generate_204",
            ),
            timeout + 1,
        )
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
