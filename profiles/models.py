"""
Version: 0.8.0
Date: 2026-08-06
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Add validated network profile model and serialization.
"""

from __future__ import annotations

import ipaddress
from dataclasses import asdict, dataclass
from typing import Any

from core.vlan_parser import parse_vlan_ids


@dataclass(frozen=True, slots=True)
class NetworkProfile:
    """Reusable defaults for diagnostics at one location."""

    name: str
    default_vlans: tuple[int, ...] = ()
    preferred_dns: str = ""
    default_subnet: str = ""

    def validate(self) -> NetworkProfile:
        """Validate all profile fields and return this instance."""
        if not self.name.strip() or len(self.name.strip()) > 80:
            raise ValueError("Profile name must contain 1 to 80 characters.")
        if any(vlan < 1 or vlan > 4094 for vlan in self.default_vlans):
            raise ValueError("Profile VLAN IDs must be between 1 and 4094.")
        if self.preferred_dns:
            try:
                ipaddress.ip_address(self.preferred_dns)
            except ValueError as error:
                raise ValueError("Profile DNS must be a valid IP address.") from error
        if self.default_subnet:
            try:
                network = ipaddress.ip_network(self.default_subnet, strict=False)
            except ValueError as error:
                raise ValueError("Profile subnet must be a valid IPv4 subnet.") from error
            if not isinstance(network, ipaddress.IPv4Network):
                raise ValueError("Profile discovery subnet must use IPv4.")
        return self

    @classmethod
    def from_fields(cls, name: str, vlans: str, dns: str, subnet: str) -> NetworkProfile:
        """Build a normalized profile from editable text fields."""
        vlan_ids = parse_vlan_ids(vlans) if vlans.strip() else ()
        normalized_subnet = str(ipaddress.ip_network(subnet.strip(), strict=False)) if subnet.strip() else ""
        return cls(name.strip(), vlan_ids, dns.strip(), normalized_subnet).validate()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this profile into JSON-compatible primitives."""
        data = asdict(self)
        data["default_vlans"] = list(self.default_vlans)
        return data

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> NetworkProfile:
        """Load and validate a profile from persisted JSON data."""
        try:
            profile = cls(
                name=str(value["name"]),
                default_vlans=tuple(int(item) for item in value.get("default_vlans", [])),
                preferred_dns=str(value.get("preferred_dns", "")),
                default_subnet=str(value.get("default_subnet", "")),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Profile data has an invalid structure.") from error
        return profile.validate()
