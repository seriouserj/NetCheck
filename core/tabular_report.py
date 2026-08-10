"""
Version: 1.6.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Build safe text and HTML representations of tabular reports.
"""

from __future__ import annotations

from html import escape


def report_as_tsv(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    """Serialize a report as UTF-8 friendly tab-separated text."""
    normalized = (_normalize_row(headers, headers), *(_normalize_row(row, headers) for row in rows))
    return "\n".join("\t".join(cell.replace("\t", " ").replace("\n", " ") for cell in row) for row in normalized)


def report_as_html(title: str, headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    """Create standalone, escaped HTML suitable for PDF or SVG rendering."""
    heading = "".join(f"<th>{escape(cell)}</th>" for cell in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in _normalize_row(row, headers)) + "</tr>"
        for row in rows
    )
    return (
        "<html><head><meta charset='utf-8'><style>"
        "body{font-family:-apple-system,Helvetica,Arial,sans-serif;color:#172b4d;}"
        "h1{font-size:20pt;color:#05285a;}table{border-collapse:collapse;width:100%;}"
        "th,td{border:1px solid #708090;padding:6px;text-align:left;}"
        "th{background:#05285a;color:white;}tr:nth-child(even){background:#eef6fa;}"
        "</style></head><body>"
        f"<h1>{escape(title)}</h1><table><thead><tr>{heading}</tr></thead><tbody>{body}</tbody></table>"
        "</body></html>"
    )


def _normalize_row(row: tuple[str, ...], headers: tuple[str, ...]) -> tuple[str, ...]:
    """Pad or trim a row to the declared column count."""
    return tuple(str(cell) for cell in row[: len(headers)]) + ("",) * max(0, len(headers) - len(row))
