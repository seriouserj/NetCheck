"""
Version: 0.5.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add bounded concurrent TCP connect scanner.
"""

from __future__ import annotations

import errno
import socket
import time
from concurrent.futures import ThreadPoolExecutor

from core.port_models import PortScanResult, PortState


class PortScanner:
    """Perform portable, unprivileged TCP connect scans."""

    FILTERED_ERRORS = {
        errno.ETIMEDOUT,
        errno.EHOSTUNREACH,
        errno.ENETUNREACH,
        errno.EHOSTDOWN,
        errno.EACCES,
    }

    def scan(self, target: str, ports: tuple[int, ...], timeout: float = 1.0) -> tuple[str, list[PortScanResult]]:
        """Resolve a target once and scan its selected ports."""
        target = target.strip()
        if not target:
            raise ValueError("Enter a target hostname or IP address.")
        try:
            resolved = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
        except socket.gaierror as error:
            raise ValueError(f"Target could not be resolved: {target}") from error
        family, _, _, _, sockaddr = resolved[0]
        address = sockaddr[0]
        workers = min(128, max(1, len(ports)))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netcheck-ports") as executor:
            results = executor.map(lambda port: self._probe(family, address, port, timeout), ports)
        return address, list(results)

    def _probe(self, family: int, address: str, port: int, timeout: float) -> PortScanResult:
        started = time.monotonic()
        endpoint = (address, port, 0, 0) if family == socket.AF_INET6 else (address, port)
        try:
            with socket.socket(family, socket.SOCK_STREAM) as connection:
                connection.settimeout(timeout)
                error_code = connection.connect_ex(endpoint)
        except OSError as error:
            error_code = error.errno or errno.ETIMEDOUT
        latency = (time.monotonic() - started) * 1000
        state = PortState.OPEN if error_code == 0 else PortState.FILTERED if error_code in self.FILTERED_ERRORS else PortState.CLOSED
        try:
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "—"
        return PortScanResult(port, state, service, latency if state is PortState.OPEN else None)
