"""
Version: 1.7.9
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify the seamless reverse-moving linear activity gradient.
"""

from PySide6.QtWidgets import QApplication

from ui.activity import ActivityTracker
from ui.brand_header import ActivityStrip
from ui.theme import BRAND_ACCENT, BRAND_BLUE, BRAND_LIGHT_CYAN, BRAND_NAVY


def test_activity_strip_uses_canonical_brand_colors() -> None:
    assert ActivityStrip.ACCENT_COLOR.name() == BRAND_ACCENT
    assert ActivityStrip.LIGHT_CYAN_COLOR.name() == BRAND_LIGHT_CYAN
    assert ActivityStrip.BLUE_COLOR.name() == BRAND_BLUE
    assert ActivityStrip.NAVY_COLOR.name() == BRAND_NAVY
    assert ActivityStrip.INDIGO_COLOR.name() == "#3843a5"
    assert ActivityStrip.VIOLET_COLOR.name() == "#735bc7"
    assert ActivityStrip.MAGENTA_COLOR.name() == "#b64fa3"
    assert ActivityStrip.RUBY_COLOR.name() == "#d94c78"
    assert ActivityStrip.GRADIENT_SPAN_PX == 900.0
    assert ActivityStrip.SPEED_PX == 3.0


def test_activity_strip_moves_in_reverse_and_wraps_seamlessly() -> None:
    application = QApplication.instance() or QApplication([])
    strip = ActivityStrip(None)
    strip._position = 0.0

    strip._advance()

    assert strip._position == -3.0
    strip._position = -899.0
    strip._advance()
    assert strip._position == -2.0
    strip.deleteLater()
    application.processEvents()


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
