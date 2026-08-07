"""
Version: 1.1.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify a VLAN batch performs exactly one privileged invocation.
"""

from core.command_runner import CommandResult
from core.vlan_models import CheckState, VlanTestResult
from core.vlan_service import VlanService


def test_batch_uses_one_privileged_worker() -> None:
    calls: list[tuple[tuple[str, ...], float]] = []
    expected = [
        VlanTestResult(162, CheckState.PASS, CheckState.PASS, CheckState.PASS, CheckState.PASS, CheckState.PASS, CheckState.PASS, CheckState.WARNING, "10.10.162.11"),
        VlanTestResult(172, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.FAIL, CheckState.UNAVAILABLE),
    ]

    def privileged(command: tuple[str, ...], timeout: float) -> CommandResult:
        calls.append((command, timeout))
        from pathlib import Path

        Path(command[-1]).write_text(json_payload(expected), encoding="utf-8")
        return CommandResult(0, "", "")

    results = VlanService(privileged_runner=privileged).test_many("en7", [162, 172], 3.0)

    assert results == expected
    assert len(calls) == 1
    assert "--vlan-worker" in calls[0][0]


def test_batch_maps_authorization_cancel_to_all_results() -> None:
    def canceled(command: tuple[str, ...], timeout: float) -> CommandResult:
        return CommandResult(1, "", "execution error: User canceled. (-128)")

    results = VlanService(privileged_runner=canceled).test_many("en7", [20, 30])

    assert len(results) == 2
    assert all("authorization was canceled" in item.detail for item in results)


def json_payload(results: list[VlanTestResult]) -> str:
    import json

    return json.dumps([item.to_payload() for item in results])
