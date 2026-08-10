"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify safe TXT and vector-document report content.
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
