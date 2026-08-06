"""
Version: 0.11.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Add bounded read-only SNMP v2c GET and WALK operations.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SnmpValue:
    """One object identifier and its formatted SNMP value."""

    oid: str
    value: str


class SnmpService:
    """Execute read-only SNMP v2c operations through PySNMP asyncio APIs."""

    def get(self, target: str, community: str, oid: str, timeout: float = 3.0) -> list[SnmpValue]:
        """Read one OID from an SNMP v2c agent."""
        self._validate(target, community, oid)
        return asyncio.run(self._get(target.strip(), community, oid.strip(), timeout))

    def walk(self, target: str, community: str, oid: str, timeout: float = 3.0, maximum_rows: int = 500) -> list[SnmpValue]:
        """Walk an OID subtree with a hard response-row limit."""
        self._validate(target, community, oid)
        if not 1 <= maximum_rows <= 5000:
            raise ValueError("SNMP walk row limit must be between 1 and 5000.")
        return asyncio.run(self._walk(target.strip(), community, oid.strip(), timeout, maximum_rows))

    @staticmethod
    def _validate(target: str, community: str, oid: str) -> None:
        if not target.strip():
            raise ValueError("Enter an SNMP target.")
        if not community:
            raise ValueError("Enter an SNMP community string.")
        if not re.fullmatch(r"\.?\d+(?:\.\d+)+", oid.strip()):
            raise ValueError("Enter a numeric OID, for example 1.3.6.1.2.1.1.1.0.")

    @staticmethod
    async def _get(target: str, community: str, oid: str, timeout: float) -> list[SnmpValue]:
        from pysnmp.hlapi.v3arch.asyncio import CommunityData, ContextData, ObjectIdentity, ObjectType, SnmpEngine, UdpTransportTarget, get_cmd

        engine = SnmpEngine()
        try:
            response = await get_cmd(
                engine,
                CommunityData(community, mpModel=1),
                await UdpTransportTarget.create((target, 161), timeout=timeout, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lookupMib=False,
            )
            return SnmpService._decode_response(response)
        finally:
            engine.close_dispatcher()

    @staticmethod
    async def _walk(target: str, community: str, oid: str, timeout: float, maximum_rows: int) -> list[SnmpValue]:
        from pysnmp.hlapi.v3arch.asyncio import CommunityData, ContextData, ObjectIdentity, ObjectType, SnmpEngine, UdpTransportTarget, walk_cmd

        engine = SnmpEngine()
        values: list[SnmpValue] = []
        try:
            iterator = walk_cmd(
                engine,
                CommunityData(community, mpModel=1),
                await UdpTransportTarget.create((target, 161), timeout=timeout, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
                maxRows=maximum_rows,
                lookupMib=False,
            )
            async for response in iterator:
                values.extend(SnmpService._decode_response(response))
            return values
        finally:
            engine.close_dispatcher()

    @staticmethod
    def _decode_response(response: tuple[object, object, object, object]) -> list[SnmpValue]:
        error_indication, error_status, error_index, var_binds = response
        if error_indication:
            raise RuntimeError(str(error_indication))
        if error_status:
            raise RuntimeError(f"{error_status} at response index {error_index}")
        return [SnmpValue(binding[0].prettyPrint(), binding[1].prettyPrint()) for binding in var_binds]
