"""
Version: 0.2.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add macOS Ethernet adapter and connectivity diagnostics.
"""

from __future__ import annotations

import socket
from collections.abc import Callable

import psutil

from core.command_runner import CommandResult, run_command
from core.interface_models import InterfaceDiagnostics
from core.network_parsers import (
    is_ethernet_port,
    parse_default_gateway,
    parse_dns_servers,
    parse_hardware_ports,
    parse_media,
)

CommandRunner = Callable[[tuple[str, ...], float], CommandResult]


class InterfaceService:
    """Collect wired interface diagnostics from macOS system APIs."""

    def __init__(self, command_runner: CommandRunner = run_command) -> None:
        self._run = command_runner

    def collect(self, timeout: float = 3.0) -> list[InterfaceDiagnostics]:
        """Collect a consistent snapshot for every detected Ethernet adapter."""
        hardware = self._run(("networksetup", "-listallhardwareports"), timeout)
        port_labels = parse_hardware_ports(hardware.stdout)
        addresses = psutil.net_if_addrs()
        statistics = psutil.net_if_stats()
        route = self._run(("route", "-n", "get", "default"), timeout)
        gateway, gateway_interface = parse_default_gateway(route.stdout)
        dns = self._run(("scutil", "--dns"), timeout)
        dns_servers = parse_dns_servers(dns.stdout)
        internet = self._probe_internet(timeout)

        devices = [name for name, label in port_labels.items() if is_ethernet_port(label)]
        if not devices:
            devices = [name for name in addresses if name.startswith("en") and name != "en0"]

        return [
            self._diagnose_device(
                device,
                addresses.get(device, []),
                statistics.get(device),
                gateway if gateway_interface == device else "",
                dns_servers,
                internet,
                timeout,
            )
            for device in sorted(set(devices))
        ]

    def _diagnose_device(
        self,
        name: str,
        addresses: list[psutil._common.snicaddr],
        stats: psutil._common.snicstats | None,
        gateway: str,
        dns_servers: tuple[str, ...],
        internet: str,
        timeout: float,
    ) -> InterfaceDiagnostics:
        ifconfig = self._run(("ifconfig", name), timeout)
        speed, duplex, media_active = parse_media(ifconfig.stdout)
        mac = next((item.address for item in addresses if item.family == psutil.AF_LINK), "")
        ipv4 = tuple(item.address for item in addresses if item.family == socket.AF_INET)
        ipv6 = tuple(item.address.split("%", 1)[0] for item in addresses if item.family == socket.AF_INET6)
        is_up = stats.isup if stats is not None else media_active
        return InterfaceDiagnostics(
            name=name,
            status="Connected" if is_up and media_active else "Disconnected",
            speed=speed,
            duplex=duplex,
            mac=mac or "—",
            ipv4=ipv4,
            ipv6=ipv6,
            gateway=gateway or "—",
            dns_servers=dns_servers,
            internet=internet if gateway else "Not routed",
        )

    @staticmethod
    def _probe_internet(timeout: float) -> str:
        try:
            with socket.create_connection(("1.1.1.1", 443), timeout=timeout):
                return "Reachable"
        except OSError:
            return "Unavailable"
