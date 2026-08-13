"""
Version: 1.8.3
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify Qt-compatible table width and title spacing markup.
"""

from core.tabular_report import report_as_html, report_as_tsv


def test_report_as_tsv_normalizes_rows_and_control_characters() -> None:
    output = report_as_tsv(("IP", "Name"), (("192.0.2.1", "server\nmain"), ("192.0.2.2",)))

    assert output == "IP\tName\n192.0.2.1\tserver main\n192.0.2.2\t"


def test_report_as_html_escapes_untrusted_scan_values() -> None:
    output = report_as_html("Scan <report>", ("Host",), (("<script>alert(1)</script>",),))

    assert "Scan &lt;report&gt;" in output
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in output
    assert "<script>alert(1)</script>" not in output
    assert "border-collapse:collapse" in output
    assert "<table width='100%' cellspacing='0' cellpadding='0'>" in output
    assert "<p class='title-gap'>&nbsp;</p>" in output


def test_report_as_html_keeps_ip_and_mac_columns_compact() -> None:
    output = report_as_html(
        "Discovery",
        ("Hostname", "IP", "MAC", "Vendor"),
        (("workstation.example", "192.168.10.25", "00:11:22:33:44:55", "Example vendor"),),
    )

    assert "table-layout:auto" in output
    assert ".network-identifier{white-space:nowrap;width:1%;}" in output
    assert "<th class='network-identifier'>IP</th>" in output
    assert "<td class='network-identifier'>192.168.10.25</td>" in output
    assert "<td class='network-identifier'>00:11:22:33:44:55</td>" in output
    assert "<td>workstation.example</td>" in output
