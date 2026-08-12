"""
Version: 1.7.2
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Widen the visible activity gradient for a smoother header animation.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPaintEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from core.metadata import APP_NAME, AUTHOR_EMAIL, AUTHOR_NAME
from core.resources import resource_path
from ui.activity import activity_tracker
from ui.theme import BRAND_ACCENT, BRAND_NAVY


class ActivityStrip(QWidget):
    """Render a static cyan divider or an animated moving brand gradient."""

    ACCENT_COLOR = QColor(BRAND_ACCENT)
    NAVY_COLOR = QColor(BRAND_NAVY)
    GRADIENT_SPAN_RATIO = 0.40

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._busy = False
        self._position = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(24)
        self._timer.timeout.connect(self._advance)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_busy(self, busy: bool) -> None:
        """Start or stop the moving gradient without changing strip geometry."""
        if self._busy == busy:
            return
        self._busy = busy
        if busy:
            self._position = -0.25
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    @property
    def animating(self) -> bool:
        """Return whether the moving gradient timer is active."""
        return self._timer.isActive()

    def _advance(self) -> None:
        self._position += 0.012
        if self._position > 1.25:
            self._position = -0.25
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the divider and, while busy, its moving navy highlight."""
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.ACCENT_COLOR)
        if not self._busy or self.width() <= 0:
            return
        center = self._position * self.width()
        span = max(180.0, self.width() * self.GRADIENT_SPAN_RATIO)
        gradient = QLinearGradient(center - span / 2, 0, center + span / 2, 0)
        transparent = QColor(self.ACCENT_COLOR)
        transparent.setAlpha(0)
        gradient.setColorAt(0.0, transparent)
        gradient.setColorAt(0.25, self.ACCENT_COLOR)
        gradient.setColorAt(0.5, self.NAVY_COLOR)
        trailing_accent = QColor(self.ACCENT_COLOR)
        trailing_accent.setAlpha(194)
        gradient.setColorAt(0.75, trailing_accent)
        gradient.setColorAt(1.0, transparent)
        painter.fillRect(self.rect(), gradient)


class BrandHeader(QFrame):
    """Display product, organization, and author identity on every tab."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("brandHeader")
        self.setFixedHeight(72)
        self._activity_strip = ActivityStrip(self)
        tracker = activity_tracker()
        tracker.busy_changed.connect(self._activity_strip.set_busy)
        self._activity_strip.set_busy(tracker.busy)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(18)

        logo = QLabel()
        logo.setObjectName("brandLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(250, 52)
        pixmap = QPixmap(str(resource_path("icons/ditis-logo.png")))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    220,
                    42,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        layout.addWidget(logo)

        layout.addStretch()
        product = QLabel(APP_NAME)
        product.setObjectName("brandProduct")
        product.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(product)

        author = QLabel(f"{AUTHOR_NAME}\n{AUTHOR_EMAIL}")
        author.setObjectName("brandAuthor")
        author.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(author)
        self._place_activity_strip()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Keep the activity strip exactly on the header's lower edge."""
        super().resizeEvent(event)
        self._place_activity_strip()

    def _place_activity_strip(self) -> None:
        """Place the unmanaged overlay without affecting header content spacing."""
        strip_height = 3
        self._activity_strip.setGeometry(0, self.height() - strip_height, self.width(), strip_height)
        self._activity_strip.raise_()
