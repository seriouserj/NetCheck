"""
Version: 1.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Report one inactive-link warning instead of errors for unused adapters.
"""

from __future__ import annotations

import re

from core.diagnostic_models import DiagnosticFinding, DiagnosticSeverity
from core.interface_models import InterfaceDiagnostics
from core.vlan_models import CheckState, VlanTestResult


class DiagnosticEngine:
    """Infer common network faults from completed test results."""

    def analyze_interfaces(self, interfaces: list[InterfaceDiagnostics]) -> list[DiagnosticFinding]:
        """Analyze physical link, negotiation, addressing, and upstream reachability."""
        findings: list[DiagnosticFinding] = []
        if not interfaces:
            return [self._finding(DiagnosticSeverity.ERROR, "No Ethernet adapter detected", "No supported wired interface is visible to macOS.", "Reconnect the USB adapter and verify it appears in Network settings.", "Dashboard")]
        connected_interfaces = [interface for interface in interfaces if interface.status == "Connected"]
        if not connected_interfaces:
            return [self._finding(DiagnosticSeverity.WARNING, "No active Ethernet link", "The detected Ethernet adapters currently have no active carrier.", "Connect a cable or select the adapter you want to test.", "Dashboard")]
        for interface in connected_interfaces:
            source = f"Interface {interface.name}"
            speed = self._speed_mbps(interface.speed)
            if speed is not None and speed <= 100:
                findings.append(self._finding(DiagnosticSeverity.WARNING, f"Link negotiated at {interface.speed}", "Cable pair damage, a 100 Mbps switch port, or negotiation mismatch may be limiting speed.", "Test a known-good Cat5e-or-better cable and confirm both endpoints use auto-negotiation.", source))
            if not interface.ipv4:
                findings.append(self._finding(DiagnosticSeverity.ERROR, "No IPv4 address", "DHCP did not provide a lease or the interface has no static configuration.", "Check DHCP availability, VLAN membership, and the selected network service.", source))
            elif interface.gateway == "—":
                findings.append(self._finding(DiagnosticSeverity.ERROR, "Default gateway missing", "The DHCP lease or static configuration has no usable default route.", "Verify gateway options on DHCP and the local subnet configuration.", source))
            elif interface.internet == "Unavailable":
                findings.append(self._finding(DiagnosticSeverity.ERROR, "Internet connectivity unavailable", "The local link is configured, but upstream routing or firewall policy blocks external TCP connectivity.", "Ping the gateway, inspect upstream routes, and verify firewall or captive-portal policy.", source))
            if not interface.dns_servers:
                findings.append(self._finding(DiagnosticSeverity.WARNING, "No DNS servers detected", "No resolver was supplied by DHCP or configured locally.", "Configure a reachable DNS server or correct DHCP option 6.", source))
        return findings

    def analyze_vlans(self, results: list[VlanTestResult]) -> list[DiagnosticFinding]:
        """Infer VLAN trunk, DHCP, gateway, DNS, and policy faults."""
        findings: list[DiagnosticFinding] = []
        for result in results:
            source = f"VLAN {result.vlan_id}"
            if result.link is CheckState.FAIL:
                findings.append(self._finding(DiagnosticSeverity.ERROR, f"VLAN {result.vlan_id} unavailable", "The VLAN may be missing from the switch trunk or the parent link is down.", "Verify that the VLAN is allowed and tagged on the connected switch port.", source))
                continue
            if result.dhcp is CheckState.FAIL:
                findings.append(self._finding(DiagnosticSeverity.ERROR, "No DHCP lease", "The VLAN is present but no DHCP offer reached the temporary interface.", "Check the VLAN DHCP scope, relay configuration, and trunk membership.", source))
            if result.gateway is CheckState.FAIL and result.dhcp is CheckState.PASS:
                findings.append(self._finding(DiagnosticSeverity.ERROR, "Gateway unreachable", "Addressing succeeded, but the configured gateway does not answer from this VLAN.", "Verify the gateway SVI, subnet mask, ACLs, and first-hop availability.", source))
            if result.dns is CheckState.FAIL:
                findings.append(self._finding(DiagnosticSeverity.WARNING, "DNS resolution failed", "The resolver is missing, unreachable, or refusing queries from this VLAN.", "Test the configured DNS server directly and verify DHCP option 6 and firewall rules.", source))
            if result.internet is CheckState.FAIL and result.ping is CheckState.PASS:
                findings.append(self._finding(DiagnosticSeverity.WARNING, "Internet application traffic blocked", "External ICMP works, but HTTPS connectivity is filtered or intercepted.", "Check firewall policy, proxy requirements, and captive-portal status.", source))
            elif result.internet is CheckState.FAIL and result.gateway is CheckState.PASS:
                findings.append(self._finding(DiagnosticSeverity.ERROR, "No upstream connectivity", "The local gateway responds, but the VLAN has no working external route.", "Check NAT, upstream routing, and egress ACLs for this VLAN.", source))
        return findings

    @staticmethod
    def _speed_mbps(value: str) -> float | None:
        match = re.fullmatch(r"([0-9.]+)\s+(Mbps|Gbps)", value)
        if not match:
            return None
        speed = float(match.group(1))
        return speed * 1000 if match.group(2) == "Gbps" else speed

    @staticmethod
    def _finding(severity: DiagnosticSeverity, title: str, reason: str, recommendation: str, source: str) -> DiagnosticFinding:
        return DiagnosticFinding(severity, title, reason, recommendation, source)
