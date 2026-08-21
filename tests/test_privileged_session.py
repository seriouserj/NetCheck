"""
Version: 1.9.6
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify approved VLAN and LLDP/CDP session workers.
"""

import sys
from pathlib import Path

from core.privileged_session import _command_is_allowed


def test_allows_only_network_workers_from_the_current_executable() -> None:
    main_script = str(Path(__file__).resolve().parents[1] / "main.py")

    assert _command_is_allowed((sys.executable, main_script, "--vlan-worker", "en0"))
    assert _command_is_allowed(
        (sys.executable, main_script, "--vlan-discovery-worker", "en0")
    )
    assert _command_is_allowed((sys.executable, main_script, "--neighbor-worker", "en0"))
    assert not _command_is_allowed((sys.executable, main_script, "--version"))
    assert not _command_is_allowed((sys.executable, "/tmp/untrusted.py", "--vlan-worker"))
    assert not _command_is_allowed(("/bin/sh", "-c", "id"))
