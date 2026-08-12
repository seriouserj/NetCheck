"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Build native diagnostic commands for macOS and Windows.
"""

from __future__ import annotations

import sys


def is_windows() -> bool:
    """Return whether NetCheck is running on Windows."""
    return sys.platform == "win32"


def ping_once_command(address: str, timeout_seconds: float) -> tuple[str, ...]:
    """Build one bounded numeric ICMP probe for the current platform."""
    timeout_ms = max(100, int(timeout_seconds * 1000))
    if is_windows():
        return ("ping", "-n", "1", "-w", str(timeout_ms), address)
    return ("ping", "-n", "-c", "1", "-W", str(timeout_ms), address)


def ping_command(target: str, count: int, packet_size: int | None = None) -> tuple[str, ...]:
    """Build a finite numeric ping command for the current platform."""
    if is_windows():
        command = ["ping", "-n", str(count)]
        if packet_size is not None:
            command.extend(("-l", str(packet_size)))
    else:
        command = ["ping", "-n", "-c", str(count)]
        if packet_size is not None:
            command.extend(("-s", str(packet_size)))
    command.append(target)
    return tuple(command)


def traceroute_command(target: str, maximum_hops: int = 30) -> tuple[str, ...]:
    """Build a numeric single-probe route trace for the current platform."""
    if is_windows():
        return ("tracert", "-d", "-h", str(maximum_hops), "-w", "1000", target)
    return ("traceroute", "-n", "-m", str(maximum_hops), "-q", "1", "-w", "1", target)


def arp_lookup_command(address: str) -> tuple[str, ...]:
    """Build a command that reads the neighbor cache for one address."""
    if is_windows():
        return ("arp", "-a", address)
    return ("arp", "-n", address)
