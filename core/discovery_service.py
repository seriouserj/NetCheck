"""
Version: 0.4.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add bounded concurrent IPv4 host discovery.
"""

from __future__ import annotations

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor

from core.command_runner import run_command
from core.discovery_models import DiscoveredHost
from core.discovery_parser import parse_arp_mac, parse_ping_latency
from core.vendor_lookup import VendorLookup


class DiscoveryService:
    """Discover responsive hosts using local ICMP, ARP, and reverse DNS."""

    def __init__(self, vendor_lookup: VendorLookup | None = None) -> None:
        self._vendors = vendor_lookup or VendorLookup()

    def scan(self, network: ipaddress.IPv4Network, timeout: float = 1.0) -> list[DiscoveredHost]:
        """Scan a validated IPv4 network and return hosts in address order."""
        workers = min(64, max(1, network.num_addresses - 2))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netcheck-discovery") as executor:
            results = executor.map(lambda address: self._probe(str(address), timeout), network.hosts())
        hosts = [host for host in results if host is not None]
        return sorted(hosts, key=lambda host: ipaddress.ip_address(host.ip_address))

    def _probe(self, address: str, timeout: float) -> DiscoveredHost | None:
        timeout_ms = max(100, int(timeout * 1000))
        ping = run_command(("ping", "-n", "-c", "1", "-W", str(timeout_ms), address), timeout + 1.0)
        latency = parse_ping_latency(ping.stdout)
        if ping.return_code != 0 or latency is None:
            return None
        arp = run_command(("arp", "-n", address), 2.0)
        mac_address = parse_arp_mac(arp.stdout)
        return DiscoveredHost(
            hostname=self._resolve_hostname(address),
            ip_address=address,
            mac_address=mac_address or "—",
            vendor=self._vendors.resolve(mac_address),
            latency_ms=latency,
        )

    @staticmethod
    def _resolve_hostname(address: str) -> str:
        try:
            return socket.gethostbyaddr(address)[0]
        except (socket.herror, socket.gaierror, OSError):
            return "—"
