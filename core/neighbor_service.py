"""
Version: 0.10.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add authorized passive LLDP and CDP packet capture.
"""

from __future__ import annotations

from core.command_runner import run_command
from core.neighbor_models import NetworkNeighbor
from core.neighbor_parser import parse_cdp, parse_lldp
from core.privileged_runner import run_privileged


class NeighborService:
    """Capture one LLDP and CDP advertisement on a selected interface."""

    def discover(self, interface: str, timeout: float = 15.0) -> list[NetworkNeighbor]:
        """Return passive link-layer neighbors without transmitting probes."""
        if not interface.strip():
            raise ValueError("Select an interface for neighbor discovery.")
        if run_command(("which", "tcpdump"), 2.0).return_code != 0:
            raise RuntimeError("tcpdump is required for LLDP/CDP discovery.")
        captures = (
            (("ether", "proto", "0x88cc"), parse_lldp),
            (("ether", "dst", "01:00:0c:cc:cc:cc"), parse_cdp),
        )
        neighbors: list[NetworkNeighbor] = []
        per_protocol = max(3.0, timeout / 2)
        for packet_filter, parser in captures:
            command = ("/usr/sbin/tcpdump", "-nn", "-vv", "-e", "-s", "0", "-c", "1", "-i", interface, *packet_filter)
            result = run_privileged(command, per_protocol + 15)
            neighbor = parser("\n".join((result.stdout, result.stderr)))
            if neighbor is not None:
                neighbors.append(neighbor)
        return neighbors
