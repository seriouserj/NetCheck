"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify numeric IP and latency ordering in discovery tables.
"""

from ui.sortable_items import IpAddressItem, NumericItem


def test_ip_addresses_sort_numerically() -> None:
    values = [IpAddressItem("192.168.1.100"), IpAddressItem("192.168.1.2"), IpAddressItem("192.168.1.10")]

    assert [item.text() for item in sorted(values)] == [
        "192.168.1.2",
        "192.168.1.10",
        "192.168.1.100",
    ]


def test_formatted_numbers_sort_by_raw_value() -> None:
    values = [NumericItem("100.00 ms", 100.0), NumericItem("9.00 ms", 9.0)]

    assert [item.text() for item in sorted(values)] == ["9.00 ms", "100.00 ms"]
