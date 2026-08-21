"""
Version: 1.9.4
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Present human-readable network identities in interface selectors.
"""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox

from core.i18n import tr
from core.interface_models import InterfaceChoice
from core.interface_service import collect_interface_choices


def populate_interface_selector(
    combo: QComboBox,
    names: list[str] | tuple[str, ...],
    selected_name: str = "",
) -> None:
    """Replace selector entries while preserving the selected system name."""
    choices = collect_interface_choices(names)
    combo.clear()
    for choice in choices:
        combo.addItem(interface_choice_text(choice), choice.name)
    index = combo.findData(selected_name)
    if index >= 0:
        combo.setCurrentIndex(index)


def selected_interface_name(combo: QComboBox) -> str:
    """Return the raw system interface name stored behind the visible label."""
    value = combo.currentData()
    return str(value) if value else combo.currentText().split(" — ", 1)[0]


def interface_choice_text(choice: InterfaceChoice) -> str:
    """Format one interface without hiding its command-line device name."""
    kind = tr(choice.interface_type)
    if choice.hardware_port and choice.hardware_port.casefold() != kind.casefold():
        return f"{choice.name} — {choice.hardware_port} ({kind})"
    return f"{choice.name} — {kind}"
