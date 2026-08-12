"""
Version: 1.7.6
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify the layered aurora and pearl-highlight palette.
"""

from ui.activity import ActivityTracker
from ui.brand_header import ActivityStrip
from ui.theme import BRAND_ACCENT, BRAND_BLUE, BRAND_LIGHT_CYAN, BRAND_NAVY


def test_activity_strip_uses_canonical_brand_colors() -> None:
    assert ActivityStrip.ACCENT_COLOR.name() == BRAND_ACCENT
    assert ActivityStrip.LIGHT_CYAN_COLOR.name() == BRAND_LIGHT_CYAN
    assert ActivityStrip.BLUE_COLOR.name() == BRAND_BLUE
    assert ActivityStrip.NAVY_COLOR.name() == BRAND_NAVY
    assert ActivityStrip.INDIGO_COLOR.name() == "#312e81"
    assert ActivityStrip.VIOLET_COLOR.name() == "#6f4cff"
    assert ActivityStrip.MAGENTA_COLOR.name() == "#d946ef"
    assert ActivityStrip.CORAL_COLOR.name() == "#ff5f6d"
    assert ActivityStrip.AMBER_COLOR.name() == "#ffcc00"
    assert ActivityStrip.LIME_COLOR.name() == "#7cff6b"
    assert ActivityStrip.TEAL_COLOR.name() == "#00cfa6"
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
