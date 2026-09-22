from __future__ import annotations

import base64
from typing import Any
from uuid import uuid4

from app.qds.document_binding import (
    create_document_binding,
)
from app.qds.protocol_registry import ProtocolRegistry
from app.qds.qds_package import QDSVerificationPackage
from app.qds.storage import save_qds_package


class SignatureManager:
    """
    Coordinates QDS signature generation.

    The manager does not implement a QDS protocol itself.
    It delegates signing to the selected protocol implementation.
    """

    def __init__(
        self,
        protocol_registry: ProtocolRegistry,
    ) -> None:
        self.protocol_registry = protocol_registry

    def generate_signature_data(
        self,
        protocol_id: str,
        signer_id: str,
        message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate protocol-specific signature data.
        """

        if not signer_id.strip():
            raise ValueError(
                "signer_id cannot be empty."
            )

        if not message:
            raise ValueError(
                "message cannot be empty."
            )

        protocol = self.protocol_registry.get(
            protocol_id
        )

        result = protocol.generate_signature(
            message=message,
            signer_id=signer_id,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise TypeError(
                "Protocol generate_signature() "
                "must return a dictionary."
            )

        return result

    def create_unbound_package(
        self,
        protocol_id: str,
        signer_id: str,
        signature_data: dict[str, Any],
        verification_data: (
            dict[str, Any] | None
        ) = None,
        metadata: (
            dict[str, Any] | None
        ) = None,
    ) -> QDSVerificationPackage:
        """
        Create a QDS package before it is associated
        with a particular document.
        """

        package = QDSVerificationPackage(
            package_id=(
                f"QDS-{uuid4().hex[:10].upper()}"
            ),
            protocol_id=protocol_id,
            signer_id=signer_id,
            signature_data=dict(
                signature_data
            ),
            verification_data=dict(
                verification_data or {}
            ),
            metadata=dict(
                metadata or {}
            ),
        )

        package.metadata[
            "stage"
        ] = "SIGNER_CREATED"

        package.validate()

        return package

    def save_package(
        self,
        package: QDSVerificationPackage,
    ):
        """
        Save a QDS package to persistent storage.
        """
        package.validate()

        return save_qds_package(
            package
        )

    def sign_document(
        self,
        package: QDSVerificationPackage,
        document_id: str,
        document_bytes: bytes,
        **kwargs: Any,
    ) -> QDSVerificationPackage:
        """
        Generate the document-bound QDS signature.

        The exact document bytes are encoded into a stable textual
        representation before being supplied to the protocol.
        """

        if not isinstance(
            document_bytes,
            bytes,
        ):
            raise TypeError(
                "document_bytes must be bytes."
            )

        if not document_bytes:
            raise ValueError(
                "document_bytes cannot be empty."
            )

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        protocol = self.protocol_registry.get(
            package.protocol_id
        )

        message = base64.b64encode(
            document_bytes
        ).decode("ascii")

        result = protocol.generate_signature(
            message=message,
            signer_id=package.signer_id,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise TypeError(
                "Protocol generate_signature() "
                "must return a dictionary."
            )

        binding = create_document_binding(
            document_id=document_id,
            document_bytes=document_bytes,
        )

        package.signature_data = dict(
            result.get(
                "signature_data",
                result,
            )
        )

        package.verification_data = dict(
            result.get(
                "verification_data",
                {},
            )
        )

        package.bind_to_document(
            document_id=document_id,
            document_binding=binding,
        )

        package.metadata[
            "stage"
        ] = "DOCUMENT_SIGNED"

        package.validate()

        return package

    def get_protocols(
        self,
    ) -> list[dict[str, str]]:
        """
        Return available protocol metadata.
        """
        return self.protocol_registry.list_protocols()