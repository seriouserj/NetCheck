"""
Version: 1.9.0
Date: 2026-08-13
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify platform-native DNS lookup command selection.
"""

from core.command_runner import CommandResult
from core import dns_tool


def test_windows_dns_lookup_uses_nslookup(monkeypatch) -> None:
    captured: list[tuple[str, ...]] = []

    def fake_run(command: tuple[str, ...], timeout: float) -> CommandResult:
        captured.append(command)
        return CommandResult(0, "Name: example.com", "")

    monkeypatch.setattr(dns_tool, "is_windows", lambda: True)
    monkeypatch.setattr(dns_tool, "run_command", fake_run)

    assert dns_tool.dns_lookup("example.com", "AAAA", "1.1.1.1") == "Name: example.com"
    assert captured == [("nslookup", "-type=AAAA", "example.com", "1.1.1.1")]


def test_macos_dns_lookup_keeps_dig(monkeypatch) -> None:
    captured: list[tuple[str, ...]] = []

    def fake_run(command: tuple[str, ...], timeout: float) -> CommandResult:
        captured.append(command)
        return CommandResult(0, "example.com. 60 IN A 192.0.2.1", "")

    monkeypatch.setattr(dns_tool, "is_windows", lambda: False)
    monkeypatch.setattr(dns_tool, "run_command", fake_run)

    dns_tool.dns_lookup("example.com", "A")
    assert captured[0][0] == "dig"
