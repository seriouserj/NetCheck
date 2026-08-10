"""
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify subnet selection from en0, active fallback, and static fallback.
"""

import socket
from types import SimpleNamespace

from pytest import MonkeyPatch

from core.network_defaults import FALLBACK_SUBNET, detect_default_subnet


def _address(value: str, netmask: str = "255.255.255.0") -> SimpleNamespace:
    return SimpleNamespace(family=socket.AF_INET, address=value, netmask=netmask)


def test_prefers_en0_address(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "core.network_defaults.psutil.net_if_addrs",
        lambda: {"en7": [_address("10.20.30.4")], "en0": [_address("192.168.50.20")]},
    )
    monkeypatch.setattr(
        "core.network_defaults.psutil.net_if_stats",
        lambda: {"en7": SimpleNamespace(isup=True), "en0": SimpleNamespace(isup=False)},
    )

    assert detect_default_subnet() == "192.168.50.0/24"


def test_uses_active_ethernet_when_en0_has_no_address(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "core.network_defaults.psutil.net_if_addrs",
        lambda: {"en0": [], "en7": [_address("10.10.162.11", "255.255.255.0")]},
    )
    monkeypatch.setattr(
        "core.network_defaults.psutil.net_if_stats",
        lambda: {"en7": SimpleNamespace(isup=True)},
    )

    assert detect_default_subnet() == "10.10.162.0/24"


def test_falls_back_without_usable_ipv4(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("core.network_defaults.psutil.net_if_addrs", lambda: {})
    monkeypatch.setattr("core.network_defaults.psutil.net_if_stats", lambda: {})

    assert detect_default_subnet() == FALLBACK_SUBNET
