"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Capture Windows LLDP/CDP traffic through TShark and Npcap.
"""

from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from core.command_runner import CommandResult, run_command
from core.neighbor_models import NetworkNeighbor
from core.neighbor_parser import parse_cdp, parse_lldp
from core.privileged_runner import run_privileged

Runner = Callable[[tuple[str, ...], float], CommandResult]


class NeighborService:
    """Capture one LLDP and CDP advertisement on a selected interface."""

    def __init__(
        self,
        runner: Runner = run_command,
        privileged_runner: Runner = run_privileged,
    ) -> None:
        self._run = runner
        self._run_privileged = privileged_runner

    def discover(self, interface: str, timeout: float = 15.0) -> list[NetworkNeighbor]:
        """Return passive link-layer neighbors without transmitting probes."""
        if not interface.strip():
            raise ValueError("Select an interface for neighbor discovery.")
        if sys.platform == "win32":
            return self._discover_windows(interface, timeout)
        if self._run(("which", "tcpdump"), 2.0).return_code != 0:
            raise RuntimeError("tcpdump is required for LLDP/CDP discovery.")
        with tempfile.NamedTemporaryFile(
            prefix="netcheck-neighbors-", suffix=".txt", delete=False
        ) as output:
            output_path = Path(output.name)
        try:
            command = self._worker_command(interface, timeout, str(output_path))
            result = self._run_privileged(command, timeout + 60.0)
            if result.return_code != 0:
                detail = result.stderr or result.stdout or "Neighbor capture authorization failed."
                raise RuntimeError(detail)
            capture = output_path.read_text(encoding="utf-8", errors="replace")
        finally:
            output_path.unlink(missing_ok=True)
        neighbors: list[NetworkNeighbor] = []
        for parser in (parse_lldp, parse_cdp):
            neighbor = parser(capture)
            if neighbor is not None:
                neighbors.append(neighbor)
        return neighbors

    def _discover_windows(self, interface: str, timeout: float) -> list[NetworkNeighbor]:
        """Capture directly connected advertisements with Windows packet capture."""
        tshark = shutil.which("tshark")
        if not tshark:
            raise RuntimeError(
                "Install Wireshark with TShark and Npcap to capture LLDP/CDP on Windows."
            )
        interfaces = self._run((tshark, "-D"), 10.0)
        capture_id = parse_tshark_interface_id(interfaces.stdout, interface)
        if not capture_id:
            raise RuntimeError(f"TShark cannot match the Windows interface: {interface}")
        result = self._run(
            (
                tshark,
                "-i",
                capture_id,
                "-a",
                f"duration:{max(2, min(30, int(timeout)))}",
                "-f",
                "ether proto 0x88cc or ether dst 01:00:0c:cc:cc:cc",
                "-V",
            ),
            timeout + 10.0,
        )
        if result.return_code not in (0, 124):
            raise RuntimeError(result.stderr or result.stdout or "Windows packet capture failed.")
        return [
            neighbor
            for parser in (parse_lldp, parse_cdp)
            if (neighbor := parser(result.stdout)) is not None
        ]

    @staticmethod
    def _worker_command(interface: str, timeout: float, output_path: str) -> tuple[str, ...]:
        arguments = ("--neighbor-worker", interface, str(timeout), output_path)
        if getattr(sys, "frozen", False):
            return (sys.executable, *arguments)
        main_script = Path(__file__).resolve().parents[1] / "main.py"
        return (sys.executable, str(main_script), *arguments)


def run_neighbor_worker(arguments: list[str]) -> int:
    """Capture LLDP and CDP frames as root and write their combined text output."""
    if len(arguments) != 3:
        return 64
    interface, timeout_text, output_text = arguments
    output_path = Path(output_text)
    try:
        output_status = output_path.lstat()
        timeout = min(30.0, max(2.0, float(timeout_text)))
    except (OSError, ValueError):
        return 64
    if not stat.S_ISREG(output_status.st_mode) or output_path.is_symlink():
        return 64
    if sys.platform == "darwin" and os.geteuid() != 0:
        return 77
    if not re.fullmatch(r"(?:en|vlan)\d+", interface):
        return 64

    command = (
        "/usr/sbin/tcpdump",
        "-l",
        "-nn",
        "-vv",
        "-e",
        "-s",
        "0",
        "-i",
        interface,
        "(",
        "ether",
        "proto",
        "0x88cc",
        ")",
        "or",
        "(",
        "ether",
        "dst",
        "01:00:0c:cc:cc:cc",
        ")",
    )
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
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=2.0)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
    output_path.write_text("\n".join(part for part in (stdout, stderr) if part), encoding="utf-8")
    return 0


def parse_tshark_interface_id(output: str, interface: str) -> str:
    """Match a TShark capture interface number by its Windows display name."""
    wanted = interface.strip().casefold()
    for line in output.splitlines():
        match = re.match(r"\s*(\d+)\.\s+.*(?:\((.+)\))\s*$", line)
        if match and wanted in match.group(2).casefold():
            return match.group(1)
    return ""
