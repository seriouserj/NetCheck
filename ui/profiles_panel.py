"""
Version: 0.8.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add profile creation, editing, and deletion interface.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from profiles.models import NetworkProfile
from profiles.repository import ProfileRepository


class ProfilesPanel(QWidget):
    """Manage reusable network diagnostic profiles."""

    def __init__(self, repository: ProfileRepository | None = None) -> None:
        super().__init__()
        self._repository = repository or ProfileRepository()
        layout = QVBoxLayout(self)
        selector = QHBoxLayout()
        selector.addWidget(QLabel("Saved profile"))
        self._profiles = QComboBox()
        self._profiles.currentIndexChanged.connect(self._select)
        selector.addWidget(self._profiles, 1)
        form = QFormLayout()
        self._name = QLineEdit()
        self._vlans = QLineEdit()
        self._vlans.setPlaceholderText("20, 30-35, 100")
        self._dns = QLineEdit()
        self._subnet = QLineEdit()
        self._subnet.setPlaceholderText("192.168.1.0/24")
        form.addRow("Name", self._name)
        form.addRow("Default VLANs", self._vlans)
        form.addRow("Preferred DNS", self._dns)
        form.addRow("Default subnet", self._subnet)
        buttons = QHBoxLayout()
        new_button = QPushButton("New")
        new_button.clicked.connect(self._clear)
        save_button = QPushButton("Save profile")
        save_button.clicked.connect(self._save)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete)
        buttons.addWidget(new_button)
        buttons.addStretch()
        buttons.addWidget(delete_button)
        buttons.addWidget(save_button)
        self._status = QLabel("")
        self._status.setObjectName("mutedLabel")
        layout.addLayout(selector)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._status)
        layout.addStretch()
        self._reload()

    def _reload(self, selected_name: str = "") -> None:
        self._profiles.blockSignals(True)
        self._profiles.clear()
        try:
            profiles = self._repository.list()
        except ValueError as error:
            profiles = []
            self._status.setText(str(error))
        for profile in profiles:
            self._profiles.addItem(profile.name, profile)
        self._profiles.blockSignals(False)
        index = self._profiles.findText(selected_name) if selected_name else 0
        if self._profiles.count():
            self._profiles.setCurrentIndex(max(0, index))
            self._select()
        else:
            self._clear()

    def _select(self) -> None:
        profile = self._profiles.currentData()
        if not isinstance(profile, NetworkProfile):
            return
        self._name.setText(profile.name)
        self._vlans.setText(", ".join(str(vlan) for vlan in profile.default_vlans))
        self._dns.setText(profile.preferred_dns)
        self._subnet.setText(profile.default_subnet)

    def _clear(self) -> None:
        for field in (self._name, self._vlans, self._dns, self._subnet):
            field.clear()
        self._status.setText("New profile")

    def _save(self) -> None:
        try:
            profile = NetworkProfile.from_fields(self._name.text(), self._vlans.text(), self._dns.text(), self._subnet.text())
            self._repository.save(profile)
        except (ValueError, OSError) as error:
            self._status.setText(f"Error: {error}")
            return
        self._status.setText("Profile saved.")
        self._reload(profile.name)

    def _delete(self) -> None:
        name = self._name.text().strip()
        if not name:
            return
        answer = QMessageBox.question(self, "Delete profile", f'Delete profile "{name}"?')
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self._repository.delete(name)
        except (ValueError, OSError) as error:
            self._status.setText(f"Error: {error}")
            return
        self._reload()
