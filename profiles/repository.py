"""
Version: 0.8.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add atomic JSON persistence for network profiles.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from profiles.models import NetworkProfile


class ProfileRepository:
    """Store validated profiles in the user's application data directory."""

    SCHEMA_VERSION = 1

    def __init__(self, path: Path | None = None) -> None:
        base = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
        self.path = path or base / "profiles.json"

    def list(self) -> list[NetworkProfile]:
        """Return profiles sorted by name; reject corrupt storage explicitly."""
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != self.SCHEMA_VERSION:
                raise ValueError("Unsupported profile storage version.")
            profiles = [NetworkProfile.from_dict(item) for item in payload.get("profiles", [])]
        except (OSError, json.JSONDecodeError, AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Profiles could not be loaded: {error}") from error
        return sorted(profiles, key=lambda profile: profile.name.casefold())

    def save(self, profile: NetworkProfile) -> None:
        """Insert or replace one profile by case-insensitive name."""
        profile.validate()
        profiles = [item for item in self.list() if item.name.casefold() != profile.name.casefold()]
        profiles.append(profile)
        self._write(profiles)

    def delete(self, name: str) -> None:
        """Delete one named profile if present."""
        profiles = [item for item in self.list() if item.name.casefold() != name.casefold()]
        self._write(profiles)

    def _write(self, profiles: list[NetworkProfile]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": self.SCHEMA_VERSION, "profiles": [item.to_dict() for item in profiles]}
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as temporary:
                json.dump(payload, temporary, indent=2, sort_keys=True)
                temporary.write("\n")
                temporary.flush()
                temporary_path = Path(temporary.name)
            temporary_path.replace(self.path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
