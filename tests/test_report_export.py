"""
Version: 1.8.3
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify full-width content inside balanced standard A4 margins.
"""

from pathlib import Path

from PySide6.QtCore import QSize
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
    rendered = document.render(0, QSize(1000, 707))
    occupied_x = [
        x
        for y in range(rendered.height())
        for x in range(rendered.width())
        if rendered.pixelColor(x, y).alpha() > 0
        and rendered.pixelColor(x, y).value() < 235
    ]
    assert max(occupied_x) - min(occupied_x) > 840
    assert 35 < min(occupied_x) < 70
    assert 930 < max(occupied_x) < 965
