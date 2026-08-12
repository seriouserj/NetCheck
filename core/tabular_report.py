"""
Version: 1.7.9
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Fit wide report tables cleanly on landscape PDF pages.
"""

from __future__ import annotations

from html import escape


def report_as_tsv(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    """Serialize a report as UTF-8 friendly tab-separated text."""
    normalized = (_normalize_row(headers, headers), *(_normalize_row(row, headers) for row in rows))
    return "\n".join("\t".join(cell.replace("\t", " ").replace("\n", " ") for cell in row) for row in normalized)


def report_as_html(title: str, headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    """Create standalone, escaped HTML suitable for PDF or SVG rendering."""
    column_classes = tuple(_column_class(header) for header in headers)
    heading = "".join(
        f"<th{_class_attribute(column_classes[index])}>{escape(cell)}</th>" for index, cell in enumerate(headers)
    )
    body = "".join(
        "<tr>"
        + "".join(
            f"<td{_class_attribute(column_classes[index])}>{escape(cell)}</td>"
            for index, cell in enumerate(_normalize_row(row, headers))
        )
        + "</tr>"
        for row in rows
    )
    return (
        "<html><head><meta charset='utf-8'><style>"
        "body{font-family:-apple-system,Helvetica,Arial,sans-serif;color:#172b4d;margin:0;}"
        "h1{font-size:16pt;color:#05285a;margin:0 0 10px 0;}"
        "table{border-collapse:collapse;width:100%;table-layout:auto;font-size:8.5pt;}"
        "th,td{border:1px solid #708090;padding:4px;text-align:left;vertical-align:top;"
        "overflow-wrap:break-word;}"
        ".network-identifier{white-space:nowrap;width:1%;}"
        "th{background:#05285a;color:white;}tr:nth-child(even){background:#eef6fa;}"
        "</style></head><body>"
        f"<h1>{escape(title)}</h1><table><thead><tr>{heading}</tr></thead><tbody>{body}</tbody></table>"
        "</body></html>"
    )


def _normalize_row(row: tuple[str, ...], headers: tuple[str, ...]) -> tuple[str, ...]:
    """Pad or trim a row to the declared column count."""
    return tuple(str(cell) for cell in row[: len(headers)]) + ("",) * max(0, len(headers) - len(row))


def _column_class(header: str) -> str:
    """Keep compact network identifiers intact in exported reports."""
    normalized = header.strip().casefold().replace("-", " ").replace("_", " ")
    return "network-identifier" if normalized in {"ip", "ip address", "mac", "mac address"} else ""


def _class_attribute(class_name: str) -> str:
    """Render an optional escaped HTML class attribute."""
    return f" class='{class_name}'" if class_name else ""
