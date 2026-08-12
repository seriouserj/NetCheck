"""
Version: 1.8.0
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify native diagnostic command construction for macOS and Windows.
"""

import core.platform_commands as platform_commands


def test_builds_macos_commands(monkeypatch) -> None:
    monkeypatch.setattr(platform_commands.sys, "platform", "darwin")

    assert platform_commands.ping_once_command("192.0.2.1", 1.5) == (
        "ping",
        "-n",
        "-c",
        "1",
        "-W",
        "1500",
        "192.0.2.1",
    )
    assert platform_commands.ping_command("router", 4, 1400) == (
        "ping",
        "-n",
        "-c",
        "4",
        "-s",
        "1400",
        "router",
    )
    assert platform_commands.traceroute_command("router") == (
        "traceroute",
        "-n",
        "-m",
        "30",
        "-q",
        "1",
        "-w",
        "1",
        "router",
    )


def test_builds_windows_commands(monkeypatch) -> None:
    monkeypatch.setattr(platform_commands.sys, "platform", "win32")

    assert platform_commands.ping_once_command("192.0.2.1", 1.5) == (
        "ping",
        "-n",
        "1",
        "-w",
        "1500",
        "192.0.2.1",
    )
    assert platform_commands.ping_command("router", 4, 1400) == (
        "ping",
        "-n",
        "4",
        "-l",
        "1400",
        "router",
    )
    assert platform_commands.traceroute_command("router") == (
        "tracert",
        "-d",
        "-h",
        "30",
        "-w",
        "1000",
        "router",
    )
