from __future__ import annotations

import base64
from typing import Any

from app.qds.document_binding import (
    verify_document_binding,
)
from app.qds.protocol_registry import ProtocolRegistry
from app.qds.qds_package import QDSVerificationPackage
from app.qds.storage import (
    get_document_path,
    load_attack_scenario,
    load_qds_package,
)


class VerificationManager:
    """
    Coordinates normal QDS verification and attack-case verification.
    """

    def __init__(
        self,
        protocol_registry: ProtocolRegistry,
    ) -> None:
        self.protocol_registry = protocol_registry

    def load_package(
        self,
        package_id: str,
    ) -> QDSVerificationPackage:

        package = load_qds_package(
            package_id
        )

        package.validate()

        return package

    def verify_document_binding(
        self,
        package: QDSVerificationPackage,
        document_bytes: bytes,
    ) -> dict[str, Any]:

        if not package.is_document_bound:
            return {
                "status": "NOT_BOUND",
                "matches": False,
                "message": (
                    "The QDS package is not associated "
                    "with a document."
                ),
            }

        return verify_document_binding(
            document_bytes=document_bytes,
            binding=package.document_binding,
        )

    def _verify_with_package(
        self,
        package: QDSVerificationPackage,
        document_bytes: bytes,
        document_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        context = context or {}

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

        binding_result = (
            self.verify_document_binding(
                package=package,
                document_bytes=document_bytes,
            )
        )

        identity_match = True

        if (
            document_id is not None
            and package.document_id is not None
        ):
            identity_match = (
                document_id
                == package.document_id
            )

        if not binding_result["matches"]:

            return {
                "package_id": package.package_id,
                "protocol_id": package.protocol_id,
                "signer_id": package.signer_id,
                "document_id": document_id,
                "expected_document_id": (
                    package.document_id
                ),
                "document_identity_match": (
                    identity_match
                ),
                "document_binding": (
                    binding_result
                ),
                "protocol_verification": {
                    "status": "NOT_EXECUTED",
                    "reason": (
                        "Document binding mismatch."
                    ),
                },
                "security_decision": {
                    "status": "DOCUMENT_MISMATCH",
                    "anomalous": True,
                    "reason": (
                        "The submitted document does not "
                        "match the document associated with "
                        "the QDS package."
                    ),
                },
                "context": context,
            }

        try:
            protocol = self.protocol_registry.get(
                package.protocol_id
            )

        except KeyError as exc:

            return {
                "package_id": package.package_id,
                "protocol_id": package.protocol_id,
                "signer_id": package.signer_id,
                "document_id": document_id,
                "expected_document_id": (
                    package.document_id
                ),
                "document_identity_match": (
                    identity_match
                ),
                "document_binding": (
                    binding_result
                ),
                "protocol_verification": {
                    "status": "PROTOCOL_UNAVAILABLE",
                    "reason": str(exc),
                },
                "security_decision": {
                    "status": "PROTOCOL_UNAVAILABLE",
                    "anomalous": True,
                    "reason": (
                        "The protocol referenced by "
                        "the QDS package is unavailable."
                    ),
                },
                "context": context,
            }

        message = base64.b64encode(
            document_bytes
        ).decode("ascii")

        verification_result = (
            protocol.verify_signature(
                message=message,
                qds_data=package.signature_data,
                **context,
            )
        )

        if not isinstance(
            verification_result,
            dict,
        ):
            raise TypeError(
                "Protocol verify_signature() "
                "must return a dictionary."
            )

        protocol_status = str(
            verification_result.get(
                "status",
                "UNKNOWN",
            )
        ).upper()

        protocol_anomalous = bool(
            verification_result.get(
                "anomalous",
                protocol_status
                in {
                    "ANOMALOUS",
                    "INVALID",
                    "FAILED",
                    "REJECTED",
                },
            )
        )

        security_status = (
            "ANOMALOUS"
            if protocol_anomalous
            else "WITHIN_EXPECTED_RANGE"
        )

        return {
            "package_id": package.package_id,
            "protocol_id": package.protocol_id,
            "signer_id": package.signer_id,
            "document_id": document_id,
            "expected_document_id": (
                package.document_id
            ),
            "document_identity_match": (
                identity_match
            ),
            "document_binding": (
                binding_result
            ),
            "protocol_verification": (
                verification_result
            ),
            "security_decision": {
                "status": security_status,
                "anomalous": protocol_anomalous,
                "reason": (
                    "Document binding matched and "
                    "protocol verification completed."
                ),
            },
            "context": context,
        }

    def verify(
        self,
        package_id: str,
        document_id: str | None = None,
        document_bytes: bytes | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:

        package = self.load_package(
            package_id
        )

        if document_bytes is None:

            if not document_id:
                document_id = package.document_id

            if not document_id:
                raise ValueError(
                    "A document ID is required."
                )

            document_path = get_document_path(
                document_id
            )

            document_bytes = (
                document_path.read_bytes()
            )

        return self._verify_with_package(
            package=package,
            document_bytes=document_bytes,
            document_id=document_id,
            context=kwargs,
        )

    def verify_saved_document(
        self,
        package_id: str,
        document_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.verify(
            package_id=package_id,
            document_id=document_id,
            **kwargs,
        )

    def verify_attack_scenario(
        self,
        scenario_id: str,
    ) -> dict[str, Any]:
        """
        Verify a detection-ready attack case.

        The original package/document remain untouched.
        """

        scenario = load_attack_scenario(
            scenario_id
        )

        scenario_type = str(
            scenario.get(
                "scenario_type",
                "",
            )
        ).upper()

        if not scenario.get(
            "detection_ready",
            False,
        ):
            return {
                "scenario_id": scenario_id,
                "security_decision": {
                    "status": "NOT_DETECTION_READY",
                    "anomalous": False,
                    "reason": (
                        "The saved attack scenario "
                        "cannot currently be used "
                        "for detection."
                    ),
                },
            }

        package_data = scenario.get(
            "qds_package"
        )

        if not isinstance(
            package_data,
            dict,
        ):
            raise ValueError(
                "Attack case does not contain QDS package data."
            )

        package = (
            QDSVerificationPackage.from_dict(
                package_data
            )
        )

        package.validate()

        encoded_document = scenario.get(
            "submitted_document_base64"
        )

        if not encoded_document:
            raise ValueError(
                "Attack case does not contain "
                "submitted document data."
            )

        try:
            document_bytes = (
                base64.b64decode(
                    encoded_document.encode("ascii"),
                    validate=True,
                )
            )
        except Exception as exc:
            raise ValueError(
                "Invalid attack-case document data."
            ) from exc

        attack_context = dict(
            scenario.get(
                "attack_case",
                {},
            )
        )

        # ---------------------------------------------------------------
        # Some attack categories require protocol-specific mechanisms
        # that our current prototype adapter does not yet implement.
        # Do not falsely classify those as detected.
        # ---------------------------------------------------------------

        if scenario_type == "REPLAY":

            return {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "package_id": package.package_id,
                "protocol_id": package.protocol_id,
                "document_id": package.document_id,
                "attack_context": attack_context,
                "security_decision": {
                    "status": (
                        "PROTOCOL_SPECIFIC_CHECK_REQUIRED"
                    ),
                    "anomalous": False,
                    "reason": (
                        "Replay detection requires the "
                        "selected QDS protocol's session/"
                        "freshness mechanism."
                    ),
                },
            }

        if scenario_type == (
            "UNAUTHORIZED_VERIFICATION"
        ):

            return {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "package_id": package.package_id,
                "protocol_id": package.protocol_id,
                "document_id": package.document_id,
                "attack_context": attack_context,
                "security_decision": {
                    "status": (
                        "AUTHORIZATION_CHECK_REQUIRED"
                    ),
                    "anomalous": False,
                    "reason": (
                        "Unauthorized verification requires "
                        "a protocol/system-specific "
                        "authorization mechanism."
                    ),
                },
            }

        if scenario_type == (
            "QUANTUM_CHANNEL_MANIPULATION"
        ):

            return {
                "scenario_id": scenario_id,
                "scenario_type": scenario_type,
                "package_id": package.package_id,
                "protocol_id": package.protocol_id,
                "document_id": package.document_id,
                "attack_context": attack_context,
                "security_decision": {
                    "status": (
                        "SIMULATION_REQUIRED"
                    ),
                    "anomalous": False,
                    "reason": (
                        "Quantum-channel manipulation "
                        "must be evaluated through the "
                        "quantum simulation engine."
                    ),
                },
            }

        result = self._verify_with_package(
            package=package,
            document_bytes=document_bytes,
            document_id=package.document_id,
            context={
                "attack_scenario": scenario_type,
                "attack_context": attack_context,
            },
        )

        result[
            "scenario_id"
        ] = scenario_id

        result[
            "scenario_type"
        ] = scenario_type

        result[
            "attack_context"
        ] = attack_context

        return result