"""
Version: 1.9.3
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Display active physical interfaces and configured macOS VPN tunnels.
"""

from __future__ import annotations

import ipaddress
import json
import re
import socket
import sys
from collections.abc import Callable

import psutil

from core.command_runner import CommandResult, run_command
from core.interface_models import InterfaceDiagnostics
from core.network_parsers import (
    is_ethernet_port,
    parse_default_gateway,
    parse_dns_servers,
    parse_hardware_ports,
    parse_ifconfig_addresses,
    parse_media,
)

CommandRunner = Callable[[tuple[str, ...], float], CommandResult]


class InterfaceService:
    """Collect wired interface diagnostics from macOS system APIs."""

    def __init__(self, command_runner: CommandRunner = run_command) -> None:
        self._run = command_runner

    def collect(self, timeout: float = 3.0) -> list[InterfaceDiagnostics]:
        """Collect a consistent snapshot for every detected Ethernet adapter."""
        if sys.platform == "win32":
            return self._collect_windows(timeout)
        hardware = self._run(("networksetup", "-listallhardwareports"), timeout)
        port_labels = parse_hardware_ports(hardware.stdout)
        addresses = psutil.net_if_addrs()
        statistics = psutil.net_if_stats()
        route = self._run(("/sbin/route", "-n", "get", "default"), timeout)
        gateway, gateway_interface = parse_default_gateway(route.stdout)
        dns = self._run(("scutil", "--dns"), timeout)
        dns_servers = parse_dns_servers(dns.stdout)
        internet = self._probe_internet(timeout)

        devices = _select_macos_devices(port_labels, addresses)

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

    def _collect_windows(self, timeout: float) -> list[InterfaceDiagnostics]:
        """Collect physical adapters and route data through Windows PowerShell."""
        addresses = psutil.net_if_addrs()
        statistics = psutil.net_if_stats()
        snapshot = self._run(
            (
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                _WINDOWS_NETWORK_SNAPSHOT,
            ),
            max(5.0, timeout * 2.0),
        )
        adapters, configurations = _parse_windows_snapshot(snapshot.stdout)
        if not adapters:
            adapters = tuple(
                {"Name": name}
                for name in addresses
                if _is_windows_ethernet_name(name)
            )
        internet = self._probe_internet(timeout)
        diagnostics: list[InterfaceDiagnostics] = []
        for adapter in adapters:
            name = str(adapter.get("Name") or "").strip()
            if not name:
                continue
            stats = statistics.get(name)
            config = configurations.get(name, {})
            interface_addresses = addresses.get(name, [])
            mac = str(adapter.get("MacAddress") or "").replace("-", ":").lower()
            if not mac:
                mac = next(
                    (item.address for item in interface_addresses if item.family == psutil.AF_LINK),
                    "",
                )
            ipv4 = tuple(
                item.address for item in interface_addresses if item.family == socket.AF_INET
            )
            ipv6 = tuple(
                item.address.split("%", 1)[0]
                for item in interface_addresses
                if item.family == socket.AF_INET6
            )
            status_text = str(adapter.get("Status") or "").casefold()
            is_up = status_text == "up" or bool(stats and stats.isup)
            speed = str(adapter.get("LinkSpeed") or "").strip()
            if not speed and stats and stats.speed > 0:
                speed = f"{stats.speed:g} Mbps"
            full_duplex = adapter.get("FullDuplex")
            duplex = "Full" if full_duplex is True else "Half" if full_duplex is False else "Unknown"
            gateway = str(config.get("Gateway") or "").strip()
            dns_servers = _string_tuple(config.get("DNS"))
            diagnostics.append(
                InterfaceDiagnostics(
                    name=name,
                    status="Connected" if is_up else "Disconnected",
                    speed=speed or "Unknown",
                    duplex=duplex,
                    mac=mac or "—",
                    ipv4=ipv4,
                    ipv6=ipv6,
                    gateway=gateway or "—",
                    dns_servers=dns_servers,
                    internet=internet if gateway else "Not routed",
                )
            )
        return sorted(diagnostics, key=lambda item: item.name.casefold())

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
        ifconfig = self._run(("/sbin/ifconfig", name), timeout)
        speed, duplex, media_active = parse_media(ifconfig.stdout)
        fallback_mac, fallback_ipv4, fallback_ipv6 = parse_ifconfig_addresses(ifconfig.stdout)
        mac = next((item.address for item in addresses if item.family == psutil.AF_LINK), "") or fallback_mac
        ipv4 = _merge_addresses(
            (item.address for item in addresses if item.family == socket.AF_INET),
            fallback_ipv4,
        )
        ipv6 = _merge_addresses(
            (
                item.address.split("%", 1)[0]
                for item in addresses
                if item.family == socket.AF_INET6
            ),
            fallback_ipv6,
        )
        if not gateway and ipv4:
            scoped_route = self._run(
                ("/sbin/route", "-n", "get", "default", "-ifscope", name),
                timeout,
            )
            gateway, _ = parse_default_gateway(scoped_route.stdout)
        is_tunnel = name.startswith(("utun", "wg"))
        is_up = stats.isup if stats is not None else media_active
        return InterfaceDiagnostics(
            name=name,
            status="Connected" if is_up and (media_active or is_tunnel) else "Disconnected",
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


_WINDOWS_NETWORK_SNAPSHOT = """
$adapters = @(Get-NetAdapter -Physical -ErrorAction SilentlyContinue |
    Select-Object Name, Status, LinkSpeed, MacAddress, FullDuplex)
$configs = @(Get-NetIPConfiguration -ErrorAction SilentlyContinue | ForEach-Object {
    [PSCustomObject]@{
        Name = $_.InterfaceAlias
        Gateway = @($_.IPv4DefaultGateway.NextHop)[0]
        DNS = @($_.DNSServer.ServerAddresses)
    }
})
[PSCustomObject]@{Adapters=$adapters; Configs=$configs} |
    ConvertTo-Json -Depth 5 -Compress
""".strip()


def _parse_windows_snapshot(
    output: str,
) -> tuple[tuple[dict[str, object], ...], dict[str, dict[str, object]]]:
    """Decode the stable PowerShell network snapshot payload."""
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        return (), {}
    if not isinstance(payload, dict):
        return (), {}
    raw_adapters = payload.get("Adapters", [])
    raw_configs = payload.get("Configs", [])
    adapters = tuple(item for item in _as_items(raw_adapters) if isinstance(item, dict))
    configurations = {
        str(item.get("Name")): item
        for item in _as_items(raw_configs)
        if isinstance(item, dict) and item.get("Name")
    }
    return adapters, configurations


def _as_items(value: object) -> tuple[object, ...]:
    if isinstance(value, list):
        return tuple(value)
    return () if value is None else (value,)


def _string_tuple(value: object) -> tuple[str, ...]:
    return tuple(str(item) for item in _as_items(value) if str(item).strip())


def _is_windows_ethernet_name(name: str) -> bool:
    normalized = name.casefold()
    excluded = ("wi-fi", "wifi", "wireless", "wlan", "bluetooth", "loopback", "tunnel", "vethernet")
    return not any(marker in normalized for marker in excluded)


def _merge_addresses(primary: object, fallback: tuple[str, ...]) -> tuple[str, ...]:
    """Merge address sources while preserving stable display order."""
    return tuple(dict.fromkeys((*primary, *fallback)))


def _select_macos_devices(
    port_labels: dict[str, str],
    addresses: dict[str, list[psutil._common.snicaddr]],
) -> list[str]:
    """Select physical network ports and configured third-party VPN tunnels."""
    devices = {
        name
        for name, label in port_labels.items()
        if is_ethernet_port(label)
    }
    for name, interface_addresses in addresses.items():
        has_configured_ip = any(
            _is_configured_ip(item.address)
            for item in interface_addresses
            if item.family in (socket.AF_INET, socket.AF_INET6)
        )
        if has_configured_ip and name.startswith(("en", "utun", "wg")):
            devices.add(name)
    return sorted(devices, key=_interface_sort_key)


def _is_configured_ip(address: str) -> bool:
    try:
        parsed = ipaddress.ip_address(address.split("%", 1)[0])
    except ValueError:
        return False
    return not (parsed.is_link_local or parsed.is_loopback or parsed.is_unspecified)


def _interface_sort_key(name: str) -> tuple[int, int, str]:
    match = re.fullmatch(r"([A-Za-z]+)(\d+)", name)
    prefix, number = (match.group(1), int(match.group(2))) if match else (name, 0)
    category = 0 if prefix == "en" else 1
    return category, number, name.casefold()
