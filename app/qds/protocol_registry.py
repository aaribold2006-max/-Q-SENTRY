from __future__ import annotations

from typing import Dict, List

from app.qds.protocol_base import QDSProtocol


class ProtocolRegistry:
    """
    Central registry for QDS protocols supported by Q-SENTRY.

    The registry keeps the application independent from the
    implementation details of individual QDS protocols.
    """

    def __init__(self) -> None:
        self._protocols: Dict[str, QDSProtocol] = {}

    def register(self, protocol: QDSProtocol) -> None:
        """
        Register a QDS protocol.

        Raises
        ------
        TypeError
            If the object does not implement QDSProtocol.

        ValueError
            If a protocol with the same ID is already registered.
        """
        if not isinstance(protocol, QDSProtocol):
            raise TypeError(
                "protocol must be an instance of QDSProtocol."
            )

        protocol_id = protocol.protocol_id.strip()

        if not protocol_id:
            raise ValueError(
                "protocol_id cannot be empty."
            )

        if protocol_id in self._protocols:
            raise ValueError(
                f"Protocol '{protocol_id}' is already registered."
            )

        self._protocols[protocol_id] = protocol

    def unregister(self, protocol_id: str) -> None:
        """
        Remove a registered protocol.
        """
        protocol_id = protocol_id.strip()

        if protocol_id not in self._protocols:
            raise KeyError(
                f"Protocol '{protocol_id}' is not registered."
            )

        del self._protocols[protocol_id]

    def get(self, protocol_id: str) -> QDSProtocol:
        """
        Retrieve a registered protocol by ID.
        """
        protocol_id = protocol_id.strip()

        try:
            return self._protocols[protocol_id]
        except KeyError as exc:
            raise KeyError(
                f"Protocol '{protocol_id}' is not registered."
            ) from exc

    def has(self, protocol_id: str) -> bool:
        """
        Check whether a protocol is registered.
        """
        return protocol_id.strip() in self._protocols

    def list_protocols(self) -> List[dict[str, str]]:
        """
        Return metadata for all registered protocols.
        """
        return [
            protocol.get_metadata()
            for protocol in self._protocols.values()
        ]

    def count(self) -> int:
        """
        Return the number of registered protocols.
        """
        return len(self._protocols)