"""
Version: 1.2.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Load a plugin-independent raster copy of the official DITIS logo.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from core.i18n import tr
from core.metadata import APP_NAME, APP_VERSION, AUTHOR_EMAIL, AUTHOR_NAME, COPYRIGHT, ORGANIZATION_URL
from core.resources import resource_path


class AboutDialog(QDialog):
    """Present product identity, author, and official organization branding."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("About NetCheck"))
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(12)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(resource_path("icons/ditis-logo.png")))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(340, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(logo)

        product = QLabel(f"<h1>{APP_NAME}</h1><p>{tr('Version')}: {APP_VERSION}</p>")
        product.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(product)

        author = QLabel(
            f"<p><b>{tr('Author')}:</b> {AUTHOR_NAME}<br>"
            f'<a href="mailto:{AUTHOR_EMAIL}">{AUTHOR_EMAIL}</a><br>'
            f'<a href="{ORGANIZATION_URL}">{ORGANIZATION_URL}</a></p>'
        )
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author.setOpenExternalLinks(True)
        layout.addWidget(author)

        copyright_label = QLabel(COPYRIGHT)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setObjectName("mutedLabel")
        layout.addWidget(copyright_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
