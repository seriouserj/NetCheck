"""
Version: 1.6.3
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Provide consistently centered form rows and labels.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QWidget


def centered_form(
    parent: QWidget | None = None, *, grow_fields: bool = False
) -> QFormLayout:
    """Create a form whose block, labels, and controls are centered consistently."""
    form = QFormLayout(parent)
    policy = (
        QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        if grow_fields
        else QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint
    )
    form.setFieldGrowthPolicy(policy)
    form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    form.setVerticalSpacing(12)
    return form
