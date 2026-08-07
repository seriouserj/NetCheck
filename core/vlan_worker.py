"""
Version: 1.1.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add a single-process privileged worker for complete VLAN batches.
"""

from __future__ import annotations

import json
import os
import re
import stat
import sys
from pathlib import Path

from core.command_runner import run_command
from core.vlan_parser import parse_vlan_ids
from core.vlan_service import VlanService


def run_vlan_worker(arguments: list[str]) -> int:
    """Validate worker arguments, execute the batch as root, and emit JSON."""
    if len(arguments) != 4:
        return 64
    parent, vlan_text, timeout_text, output_text = arguments
    output_path = Path(output_text)
    try:
        output_status = output_path.lstat()
    except OSError:
        return 64
    if not stat.S_ISREG(output_status.st_mode) or output_path.is_symlink():
        return 64
    if sys.platform == "darwin" and os.geteuid() != 0:
        return 77
    if not re.fullmatch(r"en\d+", parent):
        return 64
    try:
        vlan_ids = parse_vlan_ids(vlan_text)
        timeout = min(120.0, max(0.5, float(timeout_text)))
    except ValueError as error:
        output_path.write_text(json.dumps({"error": str(error)}), encoding="utf-8")
        return 64

    service = VlanService(runner=run_command, privileged_runner=run_command)
    results = [service.test(parent, vlan_id, timeout) for vlan_id in vlan_ids]
    output_path.write_text(
        json.dumps([result.to_payload() for result in results], separators=(",", ":")),
        encoding="utf-8",
    )
    return 0
