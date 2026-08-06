"""
Version: 0.8.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Verify profile normalization and atomic repository behavior.
"""

from profiles.models import NetworkProfile
from profiles.repository import ProfileRepository


def test_profile_round_trip(tmp_path) -> None:
    repository = ProfileRepository(tmp_path / "profiles.json")
    profile = NetworkProfile.from_fields("Office A", "20, 30-31", "1.1.1.1", "192.168.10.25/24")
    repository.save(profile)
    assert repository.list() == [NetworkProfile("Office A", (20, 30, 31), "1.1.1.1", "192.168.10.0/24")]


def test_profile_replacement_is_case_insensitive(tmp_path) -> None:
    repository = ProfileRepository(tmp_path / "profiles.json")
    repository.save(NetworkProfile("Home"))
    repository.save(NetworkProfile("home", (10,)))
    assert repository.list() == [NetworkProfile("home", (10,))]
