"""
Version: 1.4.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Apply tubbeTEC branding and a single author credit in the header.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from core.metadata import APP_NAME, AUTHOR_NAME
from core.resources import resource_path


class BrandHeader(QFrame):
    """Display product, organization, and author identity on every tab."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("brandHeader")
        self.setFixedHeight(72)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(18)

        logo = QLabel()
        logo.setObjectName("brandLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(190, 52)
        pixmap = QPixmap(str(resource_path("icons/tubbetec-logo.png")))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    160,
                    50,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        layout.addWidget(logo)

        layout.addStretch()
        product = QLabel(f"{APP_NAME} Tool by {AUTHOR_NAME}")
        product.setObjectName("brandProduct")
        product.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(product)
