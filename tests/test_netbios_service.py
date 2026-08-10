"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify NBSTAT request generation and node-name parsing.
"""

import struct

from core.netbios_service import build_node_status_query, parse_node_status_response


def test_builds_wildcard_nbstat_query() -> None:
    query = build_node_status_query(0x1234)

    assert query[:2] == b"\x12\x34"
    assert query[-4:] == struct.pack("!HH", 0x21, 1)
    assert len(query) == 50


def test_parses_hostname_and_workgroup() -> None:
    def name_record(name: str, suffix: int, flags: int) -> bytes:
        return name.encode("ascii").ljust(15, b" ") + bytes((suffix,)) + struct.pack("!H", flags)

    node_data = (
        b"\x02"
        + name_record("MAC-7B68B", 0x00, 0)
        + name_record("WORKGROUP", 0x00, 0x8000)
    )
    header = struct.pack("!HHHHHH", 0x1234, 0x8500, 0, 1, 0, 0)
    answer = b"\xc0\x0c" + struct.pack("!HHIH", 0x21, 1, 0, len(node_data)) + node_data

    result = parse_node_status_response(header + answer, 0x1234)

    assert result.hostname == "MAC-7B68B"
    assert result.workgroup == "WORKGROUP"
    assert result.display_name == "WORKGROUP\\MAC-7B68B"
