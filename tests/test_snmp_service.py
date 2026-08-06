"""
Version: 0.11.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify SNMP request validation without network access.
"""

import pytest

from core.snmp_service import SnmpService


@pytest.mark.parametrize("oid", ["", "sysDescr.0", "1.3.bad.1"])
def test_rejects_non_numeric_oid(oid: str) -> None:
    with pytest.raises(ValueError):
        SnmpService().get("192.0.2.1", "public", oid)


def test_requires_target_and_community() -> None:
    with pytest.raises(ValueError):
        SnmpService().get("", "public", "1.3.6.1")
    with pytest.raises(ValueError):
        SnmpService().get("192.0.2.1", "", "1.3.6.1")
