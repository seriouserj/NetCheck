"""
Version: 1.9.5
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Reuse the app-session VLAN authorization when BPF access is denied.
"""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

from core.command_runner import CommandResult
from core.packet_capture import capture_requires_privileges
from core.privileged_session import run_session_privileged
from core.streaming_command import run_streaming_command

Runner = Callable[[tuple[str, ...], float], CommandResult]
CaptureRunner = Callable[[Sequence[str], float, object | None, object | None], CommandResult]


class VlanDiscoveryService:
    """Observe tagged frames without actively configuring every VLAN ID."""

    def __init__(
        self,
        privileged_runner: Runner = run_session_privileged,
        capture_runner: CaptureRunner = run_streaming_command,
    ) -> None:
        self._run_privileged = privileged_runner
        self._capture = capture_runner

    def discover(self, interface: str, duration: float = 8.0) -> list[int]:
        """Return VLAN IDs observed on an Ethernet interface during a short capture."""
        capture = self._capture(
            ("/usr/sbin/tcpdump", "-l", "-nn", "-e", "-i", interface, "vlan"),
            duration,
            None,
            None,
        )
        if not capture_requires_privileges(capture):
            if capture.return_code not in (0, 124):
                raise RuntimeError(capture.stderr or capture.stdout or "VLAN discovery capture failed")
            return parse_observed_vlan_ids(capture.stdout)
        with tempfile.NamedTemporaryFile(prefix="netcheck-vlan-discovery-", suffix=".json", delete=False) as output:
            output_path = Path(output.name)
        try:
            command = self._worker_command(interface, duration, str(output_path))
            completed = self._run_privileged(command, duration + 60.0)
            if completed.return_code != 0:
                detail = completed.stderr or completed.stdout or "VLAN discovery authorization failed"
                raise RuntimeError(detail)
            try:
                payload = json.loads(output_path.read_text(encoding="utf-8"))
                return sorted({int(item) for item in payload if 1 <= int(item) <= 4094})
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
                raise RuntimeError(f"Invalid VLAN discovery response: {error}") from error
        finally:
            output_path.unlink(missing_ok=True)

    @staticmethod
    def _worker_command(interface: str, duration: float, output_path: str) -> tuple[str, ...]:
        arguments = ("--vlan-discovery-worker", interface, str(duration), output_path)
        if getattr(sys, "frozen", False):
            return (sys.executable, *arguments)
        main_script = Path(__file__).resolve().parents[1] / "main.py"
        return (sys.executable, str(main_script), *arguments)


def parse_observed_vlan_ids(capture: str) -> list[int]:
    """Extract unique valid VLAN identifiers from tcpdump text output."""
    return sorted(
        {
            int(candidate)
            for candidate in re.findall(r"\bvlan\s+(\d{1,4})\b", capture, re.IGNORECASE)
            if 1 <= int(candidate) <= 4094
        }
    )


def run_vlan_discovery_worker(arguments: list[str]) -> int:
    """Capture tagged frames as root and write observed identifiers to JSON."""
    if len(arguments) != 3:
        return 64
    interface, duration_text, output_text = arguments
    output_path = Path(output_text)
    try:
        output_status = output_path.lstat()
        duration = min(30.0, max(2.0, float(duration_text)))
    except (OSError, ValueError):
        return 64
    if not stat.S_ISREG(output_status.st_mode) or output_path.is_symlink():
        return 64
    if sys.platform == "darwin" and os.geteuid() != 0:
        return 77
    if not re.fullmatch(r"en\d+", interface):
        return 64

    command = ["/usr/sbin/tcpdump", "-l", "-nn", "-e", "-i", interface, "vlan"]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (FileNotFoundError, PermissionError, OSError):
        return 69
    try:
        stdout, _ = process.communicate(timeout=duration)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            stdout, _ = process.communicate(timeout=2.0)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, _ = process.communicate()
    output_path.write_text(json.dumps(parse_observed_vlan_ids(stdout)), encoding="utf-8")
    return 0
