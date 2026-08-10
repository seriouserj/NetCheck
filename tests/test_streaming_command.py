"""
Version: 1.5.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify incremental command output and bounded traceroute probes.
"""

from __future__ import annotations

import sys
from threading import Event

from core.command_runner import CommandResult
from core.streaming_command import run_streaming_command
from core.traceroute_tool import traceroute


def test_streaming_command_delivers_each_line() -> None:
    received: list[str] = []

    result = run_streaming_command(
        (sys.executable, "-u", "-c", "print('first'); print('second')"),
        2.0,
        received.append,
    )

    assert result.return_code == 0
    assert received == ["first", "second"]
    assert result.stdout == "first\nsecond"


def test_streaming_command_keeps_partial_output_on_timeout() -> None:
    received: list[str] = []

    result = run_streaming_command(
        (
            sys.executable,
            "-u",
            "-c",
            "import time; print('started'); time.sleep(2)",
        ),
        0.1,
        received.append,
    )

    assert result.return_code == 124
    assert result.stdout == "started"
    assert received[0] == "started"
    assert "timed out" in received[-1]


def test_streaming_command_drains_large_terminal_output() -> None:
    received: list[str] = []

    result = run_streaming_command(
        (sys.executable, "-u", "-c", "[print(index) for index in range(2000)]"),
        5.0,
        received.append,
    )

    assert result.return_code == 0
    assert len(received) == 2000
    assert received[-1] == "1999"


def test_traceroute_uses_one_short_probe_per_hop() -> None:
    calls: list[tuple[tuple[str, ...], float]] = []

    def runner(command: tuple[str, ...], timeout: float, callback: object) -> CommandResult:
        calls.append((command, timeout))
        return CommandResult(0, "1  192.0.2.1  1.0 ms", "")

    output = traceroute("example.com", runner=runner)

    assert output == "1  192.0.2.1  1.0 ms"
    assert calls == [
        (("traceroute", "-n", "-m", "30", "-q", "1", "-w", "1", "example.com"), 45.0)
    ]


def test_streaming_command_honors_cancellation() -> None:
    stop = Event()
    stop.set()

    result = run_streaming_command(
        (sys.executable, "-u", "-c", "import time; time.sleep(10)"),
        20.0,
        cancel_event=stop,
    )

    assert result.return_code != 0
