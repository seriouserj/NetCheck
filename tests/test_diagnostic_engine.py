"""
Version: 1.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify unused disconnected adapters do not produce false errors.
"""

from core.diagnostic_engine import DiagnosticEngine
from core.diagnostic_models import DiagnosticSeverity
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


def test_ignores_disconnected_adapters_when_one_link_is_active() -> None:
    active = InterfaceDiagnostics("en7", "Connected", "1 Gbps", "Full", "aa:bb:cc:dd:ee:ff", ("192.168.1.2",), (), "192.168.1.1", ("1.1.1.1",), "Reachable")
    unused = InterfaceDiagnostics("en4", "Disconnected", "Unknown", "Unknown", "00:11:22:33:44:55", (), (), "—", (), "Not routed")

    assert DiagnosticEngine().analyze_interfaces([active, unused]) == []


def test_reports_one_warning_when_all_adapters_are_disconnected() -> None:
    unused = InterfaceDiagnostics("en4", "Disconnected", "Unknown", "Unknown", "00:11:22:33:44:55", (), (), "—", (), "Not routed")
    findings = DiagnosticEngine().analyze_interfaces([unused])

    assert len(findings) == 1
    assert findings[0].severity is DiagnosticSeverity.WARNING
    assert findings[0].title == "No active Ethernet link"
