"""
Version: 1.7.7
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify the harmonized cool aurora palette.
"""

from ui.activity import ActivityTracker
from ui.brand_header import ActivityStrip
from ui.theme import BRAND_ACCENT, BRAND_BLUE, BRAND_LIGHT_CYAN, BRAND_NAVY


def test_activity_strip_uses_canonical_brand_colors() -> None:
    assert ActivityStrip.ACCENT_COLOR.name() == BRAND_ACCENT
    assert ActivityStrip.LIGHT_CYAN_COLOR.name() == BRAND_LIGHT_CYAN
    assert ActivityStrip.BLUE_COLOR.name() == BRAND_BLUE
    assert ActivityStrip.NAVY_COLOR.name() == BRAND_NAVY
    assert ActivityStrip.ROYAL_BLUE_COLOR.name() == "#2457d6"
    assert ActivityStrip.INDIGO_COLOR.name() == "#3843a5"
    assert ActivityStrip.VIOLET_COLOR.name() == "#735bc7"
    assert ActivityStrip.PERIWINKLE_COLOR.name() == "#586fe8"
    assert ActivityStrip.AQUA_COLOR.name() == "#20d5d2"
    assert ActivityStrip.TEAL_COLOR.name() == "#00b7b0"
    assert ActivityStrip.GRADIENT_SPAN_PX == 900.0


def test_activity_tracker_stays_busy_until_every_operation_finishes() -> None:
    tracker = ActivityTracker()
    changes: list[bool] = []
    tracker.busy_changed.connect(changes.append)

    tracker.begin()
    tracker.begin()
    tracker.end()

    assert tracker.busy
    assert changes == [True]

    tracker.end()

    assert not tracker.busy
    assert changes == [True, False]


def test_activity_tracker_ignores_unbalanced_completion() -> None:
    tracker = ActivityTracker()
    changes: list[bool] = []
    tracker.busy_changed.connect(changes.append)

    tracker.end()

    assert not tracker.busy
    assert changes == []
