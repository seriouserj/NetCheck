"""
Version: 1.9.8
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Deterministically verify progressive discovery publication order.
"""

from __future__ import annotations

import ipaddress
from threading import Event

from core.discovery_models import DiscoveredHost
from core.discovery_service import DiscoveryService


def test_scan_reports_each_host_before_returning_sorted_results(monkeypatch) -> None:
    service = DiscoveryService()
    release_slow_probe = Event()

    def probe(address: str, timeout: float) -> DiscoveredHost:
        del timeout
        if address.endswith(".1"):
            assert release_slow_probe.wait(1.0)
        return DiscoveredHost(
            hostname="host",
            ip_address=address,
            mac_address="00:11:22:33:44:55",
            vendor="Example",
            latency_ms=1.0,
        )

    monkeypatch.setattr(service, "_probe", probe)
    published: list[DiscoveredHost] = []

    def publish(host: DiscoveredHost) -> None:
        published.append(host)
        if host.ip_address.endswith(".2"):
            release_slow_probe.set()

    results = service.scan(
        ipaddress.ip_network("192.0.2.0/30"),
        progress=publish,
    )

    assert [host.ip_address for host in published] == ["192.0.2.2", "192.0.2.1"]
    assert [host.ip_address for host in results] == ["192.0.2.1", "192.0.2.2"]
