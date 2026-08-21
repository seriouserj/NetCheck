"""
Version: 1.9.6
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Share one macOS authorization between VLAN and LLDP/CDP operations.
"""

from __future__ import annotations

import atexit
import json
import os
import secrets
import shlex
import socket
import sys
import tempfile
import threading
import time
from collections.abc import Sequence
from pathlib import Path

from core.command_runner import CommandResult, run_command

_MAX_MESSAGE_BYTES = 8 * 1024 * 1024
_BROKER_IDLE_SECONDS = 15 * 60
_ALLOWED_WORKERS = {
    "--vlan-worker",
    "--vlan-discovery-worker",
    "--neighbor-worker",
}


class PrivilegedNetworkSession:
    """Own a short-lived root broker restricted to approved NetCheck workers."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._directory: Path | None = None
        self._socket_path: Path | None = None
        self._token = ""

    def run(self, command: Sequence[str], timeout: float = 60.0) -> CommandResult:
        """Execute an approved network worker, authorizing only the first request."""
        normalized = tuple(str(item) for item in command)
        if sys.platform != "darwin" or os.geteuid() == 0:
            return run_command(normalized, timeout)
        if not _command_is_allowed(normalized):
            return CommandResult(77, "", "The privileged network session rejected this command.")
        with self._lock:
            startup = self._ensure_started()
            if startup is not None:
                return startup
            response = self._request(
                {"token": self._token, "action": "run", "command": normalized, "timeout": timeout},
                timeout + 10.0,
            )
            if response is None:
                self._reset()
                return CommandResult(70, "", "The privileged network session stopped unexpectedly.")
            return _command_result_from_payload(response)

    def close(self) -> None:
        """Ask the root broker to exit and remove the private session directory."""
        with self._lock:
            if self._socket_path and self._socket_path.exists():
                self._request({"token": self._token, "action": "stop"}, 2.0)
            self._reset()

    def _ensure_started(self) -> CommandResult | None:
        if self._socket_path and self._socket_path.exists():
            return None
        self._reset()
        directory = Path(tempfile.mkdtemp(prefix="nc-network-root-", dir="/tmp"))
        directory.chmod(0o700)
        self._directory = directory
        self._socket_path = directory / "broker.sock"
        self._token = secrets.token_hex(32)
        worker = _broker_command(str(self._socket_path), self._token, os.getuid())
        shell_command = f"{shlex.join(worker)} </dev/null >/dev/null 2>&1 &"
        apple_script = (
            f"do shell script {json.dumps(shell_command)} with administrator privileges"
        )
        authorized = run_command(("osascript", "-e", apple_script), 60.0)
        if authorized.return_code != 0:
            self._reset()
            return authorized
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            if self._socket_path.exists():
                return None
            time.sleep(0.05)
        self._reset()
        return CommandResult(70, "", "The privileged network session did not start.")

    def _request(self, payload: dict[str, object], timeout: float) -> dict[str, object] | None:
        if self._socket_path is None:
            return None
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(max(1.0, timeout))
                client.connect(str(self._socket_path))
                client.sendall(json.dumps(payload, separators=(",", ":")).encode() + b"\n")
                response = _receive_line(client)
            decoded = json.loads(response)
            return decoded if isinstance(decoded, dict) else None
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def _reset(self) -> None:
        socket_path = self._socket_path
        directory = self._directory
        self._socket_path = None
        self._directory = None
        self._token = ""
        if socket_path:
            socket_path.unlink(missing_ok=True)
        if directory:
            try:
                directory.rmdir()
            except OSError:
                pass


_SESSION = PrivilegedNetworkSession()
atexit.register(_SESSION.close)


def run_session_privileged(
    command: Sequence[str], timeout: float = 60.0
) -> CommandResult:
    """Run an approved worker through the reusable session authorization."""
    return _SESSION.run(command, timeout)


def run_privileged_session_worker(arguments: list[str]) -> int:
    """Serve approved network worker requests as a time-limited root process."""
    if len(arguments) != 3 or sys.platform != "darwin" or os.geteuid() != 0:
        return 77
    socket_text, token, uid_text = arguments
    try:
        owner_uid = int(uid_text)
    except ValueError:
        return 64
    socket_path = Path(socket_text)
    if not token or socket_path.name != "broker.sock" or not socket_path.parent.is_dir():
        return 64
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        socket_path.unlink(missing_ok=True)
        server.bind(str(socket_path))
        os.chown(socket_path, owner_uid, -1)
        socket_path.chmod(0o600)
        server.listen(4)
        server.settimeout(1.0)
        deadline = time.monotonic() + _BROKER_IDLE_SECONDS
        while time.monotonic() < deadline:
            try:
                connection, _ = server.accept()
            except TimeoutError:
                continue
            with connection:
                request = _decode_request(_receive_line(connection))
                if request.get("token") != token:
                    _send_response(connection, {"return_code": 77, "stdout": "", "stderr": "Unauthorized request."})
                    continue
                if request.get("action") == "stop":
                    _send_response(connection, {"return_code": 0, "stdout": "", "stderr": ""})
                    return 0
                command = tuple(str(item) for item in request.get("command", []))
                if request.get("action") != "run" or not _command_is_allowed(command):
                    _send_response(connection, {"return_code": 77, "stdout": "", "stderr": "Rejected command."})
                    continue
                timeout = min(3600.0, max(1.0, float(request.get("timeout", 60.0))))
                result = run_command(command, timeout)
                _send_response(
                    connection,
                    {"return_code": result.return_code, "stdout": result.stdout, "stderr": result.stderr},
                )
                deadline = time.monotonic() + _BROKER_IDLE_SECONDS
        return 0
    except (OSError, ValueError):
        return 70
    finally:
        server.close()
        socket_path.unlink(missing_ok=True)


def _broker_command(socket_path: str, token: str, owner_uid: int) -> tuple[str, ...]:
    arguments = ("--privileged-session-worker", socket_path, token, str(owner_uid))
    if getattr(sys, "frozen", False):
        return (sys.executable, *arguments)
    main_script = Path(__file__).resolve().parents[1] / "main.py"
    return (sys.executable, str(main_script), *arguments)


def _command_is_allowed(command: Sequence[str]) -> bool:
    if not command or Path(command[0]).resolve() != Path(sys.executable).resolve():
        return False
    if getattr(sys, "frozen", False):
        return len(command) >= 2 and command[1] in _ALLOWED_WORKERS
    expected_main = Path(__file__).resolve().parents[1] / "main.py"
    return (
        len(command) >= 3
        and Path(command[1]).resolve() == expected_main.resolve()
        and command[2] in _ALLOWED_WORKERS
    )


def _receive_line(connection: socket.socket) -> str:
    chunks = bytearray()
    while len(chunks) < _MAX_MESSAGE_BYTES:
        chunk = connection.recv(min(65536, _MAX_MESSAGE_BYTES - len(chunks)))
        if not chunk:
            break
        chunks.extend(chunk)
        if b"\n" in chunk:
            break
    return bytes(chunks).split(b"\n", 1)[0].decode("utf-8", errors="replace")


def _decode_request(value: str) -> dict[str, object]:
    try:
        payload = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _send_response(connection: socket.socket, payload: dict[str, object]) -> None:
    connection.sendall(json.dumps(payload, separators=(",", ":")).encode() + b"\n")


def _command_result_from_payload(payload: dict[str, object]) -> CommandResult:
    try:
        return_code = int(payload.get("return_code", 70))
    except (TypeError, ValueError):
        return_code = 70
    return CommandResult(
        return_code,
        str(payload.get("stdout", "")),
        str(payload.get("stderr", "")),
    )
