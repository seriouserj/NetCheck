"""
Version: 0.9.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add structured Smart Diagnostics findings.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DiagnosticSeverity(str, Enum):
    """Operational severity of an inferred network problem."""

    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"


@dataclass(frozen=True, slots=True)
class DiagnosticFinding:
    """Probable cause and actionable recommendation for observed evidence."""

    severity: DiagnosticSeverity
    title: str
    probable_reason: str
    recommendation: str
    source: str
