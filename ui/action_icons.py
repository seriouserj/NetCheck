"""
Version: 1.6.10
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Keep every action icon legible on the unified navy button surface.
"""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QPushButton

ActionIconName = Literal["copy", "export", "scan", "wake"]
ICON_SIZE = 18


def decorate_action(button: QPushButton, name: ActionIconName, *, primary: bool = False) -> None:
    """Add a compact, accessible icon while retaining the translated button text."""
    button.setIcon(action_icon(name, primary=primary))
    button.setIconSize(QSize(ICON_SIZE, ICON_SIZE))


def action_icon(name: ActionIconName, *, primary: bool = False) -> QIcon:
    """Create a scalable-looking icon with normal, hover, and disabled states."""
    normal = QColor("#ffffff")
    icon = QIcon()
    icon.addPixmap(_draw_icon(name, normal), QIcon.Mode.Normal)
    icon.addPixmap(_draw_icon(name, QColor("#ffffff")), QIcon.Mode.Active)
    icon.addPixmap(_draw_icon(name, QColor("#8a949e")), QIcon.Mode.Disabled)
    return icon


def _draw_icon(name: ActionIconName, color: QColor) -> QPixmap:
    pixmap = QPixmap(ICON_SIZE, ICON_SIZE)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name == "copy":
        painter.drawRoundedRect(QRectF(3.0, 6.0, 9.0, 9.0), 1.0, 1.0)
        painter.drawRoundedRect(QRectF(6.0, 3.0, 9.0, 9.0), 1.0, 1.0)
    elif name == "export":
        painter.drawLine(QPointF(9.0, 2.5), QPointF(9.0, 11.5))
        painter.drawLine(QPointF(5.5, 8.0), QPointF(9.0, 11.5))
        painter.drawLine(QPointF(12.5, 8.0), QPointF(9.0, 11.5))
        painter.drawLine(QPointF(3.0, 14.5), QPointF(15.0, 14.5))
    elif name == "scan":
        painter.drawEllipse(QRectF(2.5, 2.5, 9.5, 9.5))
        painter.drawLine(QPointF(11.0, 11.0), QPointF(15.5, 15.5))
    else:
        path = QPainterPath(QPointF(10.5, 1.5))
        path.lineTo(4.5, 10.0)
        path.lineTo(8.5, 10.0)
        path.lineTo(7.5, 16.5)
        path.lineTo(14.0, 7.5)
        path.lineTo(10.0, 7.5)
        path.closeSubpath()
        painter.setBrush(color)
        painter.drawPath(path)

    painter.end()
    return pixmap
