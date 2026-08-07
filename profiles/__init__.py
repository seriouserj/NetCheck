"""
Version: 0.8.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Export the typed network profile API.
"""

from profiles.models import NetworkProfile
from profiles.repository import ProfileRepository

__all__ = ["NetworkProfile", "ProfileRepository"]
