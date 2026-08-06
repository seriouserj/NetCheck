"""
Version: 0.9.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify Smart Diagnostics inference rules.
"""

from core.diagnostic_engine import DiagnosticEngine
from core.interface_models import InterfaceDiagnostics
from core.vlan_models import CheckState, VlanTestResult


def test_detects_slow_link_and_missing_gateway() -> None:
    interface = InterfaceDiagnostics("en7", "Connected", "100 Mbps", "Full", "aa:bb:cc:dd:ee:ff", ("192.168.1.2",), (), "—", ("1.1.1.1",), "Not routed")
    titles = [finding.title for finding in DiagnosticEngine().analyze_interfaces([interface])]
    assert "Link negotiated at 100 Mbps" in titles
    assert "Default gateway missing" in titles


def test_detects_vlan_dhcp_failure() -> None:
    result = VlanTestResult(20, CheckState.PASS, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.UNAVAILABLE)
    titles = [finding.title for finding in DiagnosticEngine().analyze_vlans([result])]
    assert "No DHCP lease" in titles
