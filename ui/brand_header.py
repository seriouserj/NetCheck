"""
Version: 1.7.9
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Use a seamless reverse-moving linear brand gradient without highlights.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QGradient, QLinearGradient, QPainter, QPaintEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from core.metadata import APP_NAME, AUTHOR_EMAIL, AUTHOR_NAME
from core.resources import resource_path
from ui.activity import activity_tracker
from ui.theme import BRAND_ACCENT, BRAND_BLUE, BRAND_LIGHT_CYAN, BRAND_NAVY


class ActivityStrip(QWidget):
    """Render a static cyan divider or an animated moving brand gradient."""

    ACCENT_COLOR = QColor(BRAND_ACCENT)
    LIGHT_CYAN_COLOR = QColor(BRAND_LIGHT_CYAN)
    BLUE_COLOR = QColor(BRAND_BLUE)
    NAVY_COLOR = QColor(BRAND_NAVY)
    INDIGO_COLOR = QColor("#3843a5")
    VIOLET_COLOR = QColor("#735bc7")
    MAGENTA_COLOR = QColor("#b64fa3")
    RUBY_COLOR = QColor("#d94c78")
    GRADIENT_SPAN_PX = 900.0
    SPEED_PX = 3.0

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
            self._position = 0.0
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    @property
    def animating(self) -> bool:
        """Return whether the moving gradient timer is active."""
        return self._timer.isActive()

    def _advance(self) -> None:
        self._position -= self.SPEED_PX
        if self._position <= -self.GRADIENT_SPAN_PX:
            self._position += self.GRADIENT_SPAN_PX
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the divider and, while busy, a seamless repeating linear gradient."""
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.ACCENT_COLOR)
        if not self._busy or self.width() <= 0:
            return
        gradient = QLinearGradient(
            self._position,
            0,
            self._position + self.GRADIENT_SPAN_PX,
            0,
        )
        gradient.setSpread(QGradient.Spread.RepeatSpread)
        gradient.setColorAt(0.00, self.ACCENT_COLOR)
        gradient.setColorAt(0.10, self.LIGHT_CYAN_COLOR)
        gradient.setColorAt(0.24, self.BLUE_COLOR)
        gradient.setColorAt(0.38, self.NAVY_COLOR)
        gradient.setColorAt(0.52, self.INDIGO_COLOR)
        gradient.setColorAt(0.64, self.VIOLET_COLOR)
        gradient.setColorAt(0.76, self.MAGENTA_COLOR)
        gradient.setColorAt(0.86, self.RUBY_COLOR)
        gradient.setColorAt(0.94, self.BLUE_COLOR)
        gradient.setColorAt(1.00, self.ACCENT_COLOR)
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
