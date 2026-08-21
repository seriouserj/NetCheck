"""
Version: 1.9.7
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Publish responsive hosts immediately while a network scan is running.
"""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.command_runner import CommandResult, run_command
from core.discovery_models import DiscoveredHost
from core.discovery_parser import parse_arp_mac, parse_cached_hostname, parse_ping_latency
from core.netbios_service import NetBiosInfo, query_netbios_node_status
from core.platform_commands import arp_lookup_command, is_windows, ping_once_command
from core.vendor_lookup import VendorLookup

CommandRunner = Callable[[tuple[str, ...], float], CommandResult]
NetBiosResolver = Callable[[str, float], NetBiosInfo]
ProgressCallback = Callable[[DiscoveredHost], None]


class DiscoveryService:
    """Discover responsive hosts using local ICMP, ARP, and reverse DNS."""

    def __init__(
        self,
        vendor_lookup: VendorLookup | None = None,
        command_runner: CommandRunner = run_command,
        netbios_resolver: NetBiosResolver = query_netbios_node_status,
    ) -> None:
        self._vendors = vendor_lookup or VendorLookup()
        self._run = command_runner
        self._netbios = netbios_resolver

    def scan(
        self,
        network: ipaddress.IPv4Network,
        timeout: float = 1.0,
        progress: ProgressCallback | None = None,
    ) -> list[DiscoveredHost]:
        """Scan an IPv4 network, reporting each host as soon as its probe finishes."""
        workers = min(64, max(1, network.num_addresses - 2))
        hosts: list[DiscoveredHost] = []
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netcheck-discovery") as executor:
            futures = {
                executor.submit(self._probe, str(address), timeout): address
                for address in network.hosts()
            }
            for future in as_completed(futures):
                host = future.result()
                if host is None:
                    continue
                hosts.append(host)
                if progress is not None:
                    progress(host)
        return sorted(hosts, key=lambda host: ipaddress.ip_address(host.ip_address))

    def _probe(self, address: str, timeout: float) -> DiscoveredHost | None:
        ping = self._run(ping_once_command(address, timeout), timeout + 1.0)
        latency = parse_ping_latency(ping.stdout)
        if ping.return_code != 0 or (latency is None and not is_windows()):
            return None
        arp = self._run(arp_lookup_command(address), 2.0)
        mac_address = parse_arp_mac(arp.stdout)
        netbios = self._netbios(address, min(0.5, max(0.2, timeout)))
        hostname = self._resolve_hostname(address) or netbios.hostname or "—"
        return DiscoveredHost(
            hostname=hostname,
            ip_address=address,
            mac_address=mac_address or "—",
            vendor=self._vendors.resolve(mac_address),
            latency_ms=latency if latency is not None else 0.0,
            netbios_info=netbios.display_name,
        )

    def _resolve_hostname(self, address: str) -> str:
        try:
            return socket.gethostbyaddr(address)[0]
        except (socket.herror, socket.gaierror, OSError):
            if is_windows():
                return ""
            cached = self._run(("dscacheutil", "-q", "host", "-a", "ip_address", address), 1.0)
            return parse_cached_hostname(cached.stdout)
