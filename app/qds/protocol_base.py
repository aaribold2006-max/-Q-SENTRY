from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class QDSProtocol(ABC):
    """
    Common interface for every QDS protocol supported by Q-SENTRY.

    A concrete protocol implementation must define:
    - protocol identity
    - signature generation
    - verification
    - protocol metadata

    The goal is to keep the application layer independent
    from the details of any particular QDS construction.
    """

    @property
    @abstractmethod
    def protocol_id(self) -> str:
        """Return a unique identifier for the protocol."""
        raise NotImplementedError

    @property
    @abstractmethod
    def protocol_name(self) -> str:
        """Return the human-readable protocol name."""
        raise NotImplementedError

    @property
    def protocol_description(self) -> str:
        """Return a short description of the protocol."""
        return ""

    @abstractmethod
    def generate_signature(
        self,
        message: str,
        signer_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate protocol-specific QDS signature data.

        Parameters
        ----------
        message:
            Exact content being signed.

        signer_id:
            Identifier of the signer.

        kwargs:
            Additional protocol-specific parameters.

        Returns
        -------
        dict
            Protocol-specific QDS signature package.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_signature(
        self,
        message: str,
        qds_data: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Verify a message against its QDS data.

        Parameters
        ----------
        message:
            Exact submitted content.

        qds_data:
            Previously generated QDS verification/signature data.

        kwargs:
            Additional protocol-specific verification parameters.

        Returns
        -------
        dict
            Verification and security evidence.
        """
        raise NotImplementedError

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata that can be displayed or stored by Q-SENTRY.
        """
        return {
            "protocol_id": self.protocol_id,
            "protocol_name": self.protocol_name,
            "description": self.protocol_description,
        }