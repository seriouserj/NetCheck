"""
Version: 0.5.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify TCP port expression validation.
"""

import pytest

from core.port_parser import parse_ports


def test_parse_ports_sorts_and_deduplicates() -> None:
    assert parse_ports("443, 20-22, 22, 80") == (20, 21, 22, 80, 443)


@pytest.mark.parametrize("expression", ["", "0", "65536", "22-20", "1,,2", "ssh"])
def test_parse_ports_rejects_invalid_values(expression: str) -> None:
    with pytest.raises(ValueError):
        parse_ports(expression)
