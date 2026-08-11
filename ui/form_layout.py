"""
Version: 1.6.7
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Align expandable spin boxes with full-width form fields.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QLayout, QSizePolicy, QWidget

CONTROL_HEIGHT = 42


class CenteredFormLayout(QFormLayout):
    """Form layout that avoids Qt's inconsistent native label alignment on macOS."""

    def addRow(  # type: ignore[override]
        self,
        label: str | QWidget | QLayout,
        field: QWidget | QLayout | None = None,
    ) -> None:
        """Add a row with an explicit, control-height label for reliable centering."""
        if (
            isinstance(field, QWidget)
            and self.fieldGrowthPolicy()
            == QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        ):
            policy = field.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
            field.setSizePolicy(policy)
        if isinstance(label, str) and field is not None:
            label_widget = QLabel(label)
            label_widget.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            label_widget.setFixedHeight(CONTROL_HEIGHT)
            label_widget.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
            )
            super().addRow(label_widget, field)
            return
        if field is None:
            super().addRow(label)
            return
        super().addRow(label, field)


def centered_form(
    parent: QWidget | None = None, *, grow_fields: bool = False
) -> QFormLayout:
    """Create a form whose block, labels, and controls are centered consistently."""
    form = CenteredFormLayout(parent)
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
