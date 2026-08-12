"""
Version: 1.7.2
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify canonical colors and the wider activity gradient.
"""

from ui.activity import ActivityTracker
from ui.brand_header import ActivityStrip
from ui.theme import BRAND_ACCENT, BRAND_NAVY


def test_activity_strip_uses_canonical_brand_colors() -> None:
    assert ActivityStrip.ACCENT_COLOR.name() == BRAND_ACCENT
    assert ActivityStrip.NAVY_COLOR.name() == BRAND_NAVY
    assert ActivityStrip.GRADIENT_SPAN_RATIO == 0.40


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
