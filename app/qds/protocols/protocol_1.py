from __future__ import annotations

import hashlib
import json
from typing import Any

from app.qds.protocol_base import QDSProtocol


class TeleportationQDSPrototype(QDSProtocol):
    """
    Q-SENTRY prototype adapter for a teleportation-based QDS workflow.

    IMPORTANT:
    This is an application-level prototype adapter.
    It is NOT a claim of full reproduction of a published QDS protocol.

    The adapter provides the stable interface required by Q-SENTRY:
        generate_signature()
        verify_signature()
        get_metadata()

    The exact published protocol mathematics can later replace the
    internals without changing the application architecture.
    """

    @property
    def protocol_id(self) -> str:
        return "TQDS-PROTOTYPE-01"

    @property
    def protocol_name(self) -> str:
        return (
            "Teleportation-Based QDS "
            "Prototype"
        )

    @property
    def protocol_description(self) -> str:
        return (
            "Qubit-based Q-SENTRY prototype "
            "adapter for a teleportation-based "
            "quantum digital signature workflow."
        )

    def generate_signature(
        self,
        message: str,
        signer_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate deterministic prototype QDS data
        from the exact message and signer identity.
        """

        if not message:
            raise ValueError(
                "message cannot be empty."
            )

        if not signer_id.strip():
            raise ValueError(
                "signer_id cannot be empty."
            )

        signer_id = signer_id.strip()

        message_digest = hashlib.sha256(
            message.encode("utf-8")
        ).hexdigest()

        binding_material = (
            f"{self.protocol_id}|"
            f"{signer_id}|"
            f"{message_digest}"
        )

        signature_digest = hashlib.sha256(
            binding_material.encode("utf-8")
        ).hexdigest()

        # Deterministic prototype quantum-state labels.
        state_labels = self._derive_state_labels(
            signature_digest
        )

        signature_data = {
            "protocol_id": self.protocol_id,
            "signer_id": signer_id,
            "message_digest": message_digest,
            "signature_digest": signature_digest,
            "state_labels": state_labels,
        }

        verification_data = {
            "binding_type": (
                "PROTOTYPE_MESSAGE_BINDING"
            ),
            "measurement_framework": (
                "Pauli eigenstate / projective "
                "measurement prototype"
            ),
            "teleportation_framework": (
                "Bell/EPR entanglement + "
                "teleportation prototype"
            ),
        }

        return {
            "signature_data": signature_data,
            "verification_data": verification_data,
        }

    def verify_signature(
        self,
        message: str,
        qds_data: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Verify prototype QDS data against the exact message.
        """

        if not message:
            raise ValueError(
                "message cannot be empty."
            )

        if not isinstance(qds_data, dict):
            raise TypeError(
                "qds_data must be a dictionary."
            )

        signer_id = str(
            qds_data.get(
                "signer_id",
                "",
            )
        ).strip()

        stored_message_digest = str(
            qds_data.get(
                "message_digest",
                "",
            )
        )

        stored_signature_digest = str(
            qds_data.get(
                "signature_digest",
                "",
            )
        )

        if not signer_id:
            return {
                "status": "INVALID",
                "anomalous": True,
                "reason": (
                    "Signer information is missing."
                ),
            }

        if not stored_message_digest:
            return {
                "status": "INVALID",
                "anomalous": True,
                "reason": (
                    "Message binding information "
                    "is missing."
                ),
            }

        if not stored_signature_digest:
            return {
                "status": "INVALID",
                "anomalous": True,
                "reason": (
                    "Signature information is missing."
                ),
            }

        observed_message_digest = (
            hashlib.sha256(
                message.encode("utf-8")
            ).hexdigest()
        )

        message_matches = (
            observed_message_digest
            == stored_message_digest
        )

        binding_material = (
            f"{self.protocol_id}|"
            f"{signer_id}|"
            f"{stored_message_digest}"
        )

        expected_signature_digest = (
            hashlib.sha256(
                binding_material.encode("utf-8")
            ).hexdigest()
        )

        signature_matches = (
            expected_signature_digest
            == stored_signature_digest
        )

        valid = (
            message_matches
            and signature_matches
        )

        return {
            "status": (
                "VALID"
                if valid
                else "INVALID"
            ),
            "anomalous": not valid,
            "message_binding_match": (
                message_matches
            ),
            "signature_integrity_match": (
                signature_matches
            ),
            "expected_message_digest": (
                stored_message_digest
            ),
            "observed_message_digest": (
                observed_message_digest
            ),
            "reason": (
                "Document/message matches the "
                "stored prototype QDS binding."
                if valid
                else
                "Document/message does not match "
                "the stored prototype QDS binding."
            ),
        }

    def get_metadata(self) -> dict[str, str]:
        """
        Return protocol metadata for the UI.
        """

        return {
            "protocol_id": self.protocol_id,
            "protocol_name": self.protocol_name,
            "description": self.protocol_description,
        }

    @staticmethod
    def _derive_state_labels(
        digest: str,
    ) -> list[str]:
        """
        Derive prototype Pauli eigenstate labels
        from the signature digest.

        This is a deterministic prototype representation,
        not a claim about a published protocol's state
        encoding.
        """

        mapping = {
            "0": "|0>",
            "1": "|1>",
            "2": "|+>",
            "3": "|->",
            "4": "|+i>",
            "5": "|-i>",
            "6": "|0>",
            "7": "|1>",
            "8": "|+>",
            "9": "|->",
            "a": "|+i>",
            "b": "|-i>",
            "c": "|0>",
            "d": "|1>",
            "e": "|+>",
            "f": "|->",
        }

        labels = [
            mapping[character]
            for character in digest[:8]
        ]

        return labels