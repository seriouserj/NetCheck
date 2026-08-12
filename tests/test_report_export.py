"""
Version: 1.7.9
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify landscape PDF report generation.
"""

from pathlib import Path

from PySide6.QtPdf import QPdfDocument

from ui.report_export import _write_pdf


def test_pdf_report_uses_landscape_pages(tmp_path: Path) -> None:
    destination = tmp_path / "report.pdf"
    headers = ("Hostname", "IP", "MAC", "Vendor", "NetBIOS", "Latency")
    rows = (("workstation.example", "192.168.10.25", "00:11:22:33:44:55", "Example", "HOST", "1 ms"),)

    _write_pdf(destination, "Network discovery report", headers, rows)

    document = QPdfDocument()
    document.load(str(destination))
    page_size = document.pagePointSize(0)
    assert destination.stat().st_size > 0
    assert document.pageCount() == 1
    assert page_size.width() > page_size.height()
