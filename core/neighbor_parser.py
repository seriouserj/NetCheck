"""
Version: 1.9.2
Date: 2026-08-18
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Parse every captured neighbor and exclude CDP TLV length metadata.
"""

from __future__ import annotations

import re

from core.neighbor_models import NetworkNeighbor


def parse_lldp(output: str) -> NetworkNeighbor | None:
    """Parse verbose tcpdump LLDP TLV output."""
    normalized = output.upper()
    if "LLDP" not in normalized and "LINK LAYER DISCOVERY PROTOCOL" not in normalized:
        return None
    return NetworkNeighbor(
        protocol="LLDP",
        system_name=_tlv_value(output, r"System Name(?: TLV)?"),
        port_id=_tlv_value(output, r"Port ID(?: TLV)?", use_last_colon=True),
        platform=_tlv_value(output, r"System Description(?: TLV)?"),
        management_address=_match(
            output, r"Management Address TLV[^\n]*\n(?:.*\n)*?\s*(?:IPv4|Address)\s*:\s*([0-9a-fA-F:.]+)"
        ),
        native_vlan=_match(output, r"(?:Port VLAN ID|PVID)[^:]*:\s*(\d+)"),
        capabilities=_tlv_value(output, r"System Capabilities(?: TLV)?"),
    )


def parse_cdp(output: str) -> NetworkNeighbor | None:
    """Parse verbose tcpdump Cisco Discovery Protocol output."""
    if "CDP" not in output.upper():
        return None
    return NetworkNeighbor(
        protocol="CDP",
        system_name=_tlv_value(output, r"Device[ -]ID"),
        port_id=_tlv_value(output, r"Port[ -]ID"),
        platform=_tlv_value(output, r"Platform"),
        management_address=_match(output, r"IPv4[^0-9]*([0-9]+(?:\.[0-9]+){3})"),
        native_vlan=_numeric_tlv_value(output, r"Native VLAN"),
        capabilities=_tlv_value(output, r"Capabilities"),
    )


def parse_neighbors(output: str) -> list[NetworkNeighbor]:
    """Parse all LLDP and CDP advertisements present in combined capture output."""
    neighbors: list[NetworkNeighbor] = []
    seen: set[tuple[str, str, str, str]] = set()
    for section in _packet_sections(output):
        normalized = section.upper()
        parser = None
        if "LLDP" in normalized or "LINK LAYER DISCOVERY PROTOCOL" in normalized:
            parser = parse_lldp
        elif "CDP" in normalized or "CISCO DISCOVERY PROTOCOL" in normalized:
            parser = parse_cdp
        if parser is None or (neighbor := parser(section)) is None:
            continue
        identity = (
            neighbor.protocol,
            neighbor.system_name,
            neighbor.port_id,
            neighbor.management_address,
        )
        if identity not in seen:
            seen.add(identity)
            neighbors.append(neighbor)
    return neighbors


def _packet_sections(output: str) -> list[str]:
    """Split tcpdump and TShark verbose output at captured packet boundaries."""
    frame_starts = [match.start() for match in re.finditer(r"(?m)^Frame\s+\d+:", output)]
    if frame_starts:
        return _sections_from_starts(output, frame_starts)
    protocol_starts = [
        match.start()
        for match in re.finditer(
            r"(?im)^(?=\S)(?=[^\n]*(?:\bLLDP\b|\bCDP(?:\s+v?\d+|v?\d+)?\b|Cisco Discovery Protocol))",
            output,
        )
    ]
    return _sections_from_starts(output, protocol_starts) if protocol_starts else [output]


def _sections_from_starts(output: str, starts: list[int]) -> list[str]:
    ends = [*starts[1:], len(output)]
    return [output[start:end] for start, end in zip(starts, ends, strict=True)]


def _tlv_value(output: str, label: str, *, use_last_colon: bool = False) -> str:
    """Read a TLV value while removing tcpdump length and type annotations."""
    match = re.search(rf"^.*?{label}[^\n]*$", output, re.IGNORECASE | re.MULTILINE)
    if not match:
        return "—"
    line = match.group(0).strip()
    quoted = re.search(r"['\"]([^'\"]+)['\"]\s*$", line)
    if quoted:
        return quoted.group(1).strip()
    bytes_value = re.search(r"\bbytes:\s*(.+)$", line, re.IGNORECASE)
    if bytes_value:
        return bytes_value.group(1).strip().strip("'\"") or "—"
    length_value = re.search(r"\blength\s*:?\s*\d+\s*:\s*(.+)$", line, re.IGNORECASE)
    if length_value:
        value = length_value.group(1).strip()
    elif ":" in line:
        value = line.split(":", 1)[1].strip()
    else:
        return "—"
    if use_last_colon and ":" in value:
        value = value.rsplit(":", 1)[1].strip()
    return value.strip("'\"") or "—"


def _numeric_tlv_value(output: str, label: str) -> str:
    value = _tlv_value(output, label)
    match = re.search(r"\b(\d+)\b", value)
    return match.group(1) if match else "—"


def _match(output: str, pattern: str) -> str:
    match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else "—"
