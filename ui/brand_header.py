"""
Version: 1.2.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add persistent DITIS logo and author identity to the main window.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from core.metadata import APP_NAME, APP_VERSION, AUTHOR_EMAIL, AUTHOR_NAME
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
        product = QLabel(f"{APP_NAME} {APP_VERSION}")
        product.setObjectName("brandProduct")
        product.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(product)

        author = QLabel(f"{AUTHOR_NAME}\n{AUTHOR_EMAIL}")
        author.setObjectName("brandAuthor")
        author.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(author)
