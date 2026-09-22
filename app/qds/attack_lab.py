from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.qds.qds_package import QDSVerificationPackage
from app.qds.storage import (
    load_document,
    load_qds_package,
    save_attack_scenario,
    save_document,
)


ATTACK_SCENARIOS: dict[str, dict[str, str]] = {
    "DOCUMENT_TAMPERING": {
        "name": "Document / Message Tampering",
        "description": (
            "Modify the signed document while retaining "
            "the original QDS data."
        ),
    },
    "FORGERY": {
        "name": "QDS Forgery",
        "description": (
            "Create modified QDS data and test whether "
            "the protocol accepts it."
        ),
    },
    "IMPERSONATION": {
        "name": "Impersonation",
        "description": (
            "Substitute the claimed signer identity."
        ),
    },
    "REPLAY": {
        "name": "Replay",
        "description": (
            "Reuse previously valid QDS data in a new "
            "verification context."
        ),
    },
    "UNAUTHORIZED_VERIFICATION": {
        "name": "Unauthorized Verification",
        "description": (
            "Attempt verification without the required "
            "authorization context."
        ),
    },
    "QUANTUM_CHANNEL_MANIPULATION": {
        "name": "Quantum-Channel Manipulation",
        "description": (
            "Introduce a controlled disturbance into "
            "the quantum verification environment."
        ),
    },
}


def _scenario_id() -> str:
    return f"ATT-{uuid4().hex[:10].upper()}"


def _attack_document_id() -> str:
    return f"ATTDOC-{uuid4().hex[:10].upper()}"


def _timestamp() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def decode_attack_document(
    attack_case: dict[str, Any],
) -> bytes:
    encoded = attack_case.get(
        "submitted_document_base64"
    )

    if not encoded:
        raise ValueError(
            "Attack case does not contain "
            "submitted document data."
        )

    try:
        return base64.b64decode(
            encoded.encode("ascii"),
            validate=True,
        )
    except Exception as exc:
        raise ValueError(
            "Invalid attack-case document data."
        ) from exc


class AttackLab:
    """
    Creates saved, detection-ready attack cases.

    Original QDS packages and original documents are never
    modified directly.
    """

    def list_attack_scenarios(
        self,
    ) -> list[dict[str, str]]:
        return [
            {
                "scenario_id": scenario_id,
                "name": details["name"],
                "description": details["description"],
            }
            for scenario_id, details
            in ATTACK_SCENARIOS.items()
        ]

    def load_original_package(
        self,
        package_id: str,
    ) -> QDSVerificationPackage:

        package = load_qds_package(
            package_id
        )

        package.validate()

        return package

    def load_original_document(
        self,
        document_id: str,
    ) -> bytes:

        return load_document(
            document_id
        )

    def _save_case(
        self,
        attack_case: dict[str, Any],
    ) -> dict[str, Any]:

        path = save_attack_scenario(
            attack_case["scenario_id"],
            attack_case,
        )

        return {
            "status": "created",
            "scenario_id": attack_case[
                "scenario_id"
            ],
            "scenario_type": attack_case[
                "scenario_type"
            ],
            "name": attack_case[
                "scenario_name"
            ],
            "original_package_id": attack_case[
                "original_package_id"
            ],
            "original_document_id": (
                attack_case.get(
                    "original_document_id"
                )
            ),
            "attack_document_id": (
                attack_case.get(
                    "attack_document_id"
                )
            ),
            "detection_ready": attack_case.get(
                "detection_ready",
                False,
            ),
            "path": str(path),
        }

    def create_document_tampering(
        self,
        package_id: str,
        original_document_id: str,
        search_text: str,
        replacement_text: str,
    ) -> dict[str, Any]:

        if not search_text:
            raise ValueError(
                "search_text cannot be empty."
            )

        package = self.load_original_package(
            package_id
        )

        document_bytes = (
            self.load_original_document(
                original_document_id
            )
        )

        source = search_text.encode(
            "utf-8"
        )

        if source not in document_bytes:
            raise ValueError(
                "search_text was not found "
                "in the selected document."
            )

        modified_bytes = document_bytes.replace(
            source,
            replacement_text.encode("utf-8"),
            1,
        )

        scenario_id = _scenario_id()

        attack_document_id = (
            _attack_document_id()
        )

        attack_filename = (
            f"{attack_document_id}.html"
        )

        attack_path = save_document(
            document_id=attack_document_id,
            document_bytes=modified_bytes,
            filename=attack_filename,
        )

        attack_case = {
            "scenario_id": scenario_id,
            "scenario_type": (
                "DOCUMENT_TAMPERING"
            ),
            "scenario_name": (
                ATTACK_SCENARIOS[
                    "DOCUMENT_TAMPERING"
                ]["name"]
            ),
            "created_at": _timestamp(),

            "original_package_id": (
                package.package_id
            ),

            "original_document_id": (
                original_document_id
            ),

            "attack_document_id": (
                attack_document_id
            ),

            "attack_case": {
                "document_modified": True,
                "qds_data_modified": False,
                "search_text": search_text,
                "replacement_text": replacement_text,
            },

            "qds_package": package.to_dict(),

            "submitted_document_base64": _encode(
                modified_bytes
            ),

            "detection_ready": True,

            "document_path": str(
                attack_path
            ),
        }

        return self._save_case(
            attack_case
        )

    def create_forgery(
        self,
        package_id: str,
        forged_signature_data: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(
            forged_signature_data,
            dict,
        ):
            raise TypeError(
                "forged_signature_data must be a dictionary."
            )

        package = self.load_original_package(
            package_id
        )

        document_id = package.document_id

        if document_id is None:
            raise ValueError(
                "QDS package is not associated "
                "with a document."
            )

        document_bytes = (
            self.load_original_document(
                document_id
            )
        )

        forged_package = deepcopy(
            package.to_dict()
        )

        forged_package[
            "signature_data"
        ] = deepcopy(
            forged_signature_data
        )

        forged_package[
            "metadata"
        ]["attack_scenario"] = "FORGERY"

        attack_case = {
            "scenario_id": _scenario_id(),
            "scenario_type": "FORGERY",
            "scenario_name": (
                ATTACK_SCENARIOS[
                    "FORGERY"
                ]["name"]
            ),
            "created_at": _timestamp(),

            "original_package_id": (
                package.package_id
            ),

            "original_document_id": (
                document_id
            ),

            "attack_document_id": (
                document_id
            ),

            "attack_case": {
                "document_modified": False,
                "qds_data_modified": True,
            },

            "qds_package": forged_package,

            "submitted_document_base64": _encode(
                document_bytes
            ),

            "detection_ready": True,
        }

        return self._save_case(
            attack_case
        )

    def create_impersonation(
        self,
        package_id: str,
        impersonated_signer_id: str,
    ) -> dict[str, Any]:

        if not impersonated_signer_id.strip():
            raise ValueError(
                "impersonated_signer_id cannot be empty."
            )

        package = self.load_original_package(
            package_id
        )

        document_id = package.document_id

        if document_id is None:
            raise ValueError(
                "QDS package is not associated "
                "with a document."
            )

        document_bytes = (
            self.load_original_document(
                document_id
            )
        )

        impersonated_package = deepcopy(
            package.to_dict()
        )

        impersonated_package[
            "signer_id"
        ] = impersonated_signer_id.strip()

        impersonated_package[
            "metadata"
        ]["attack_scenario"] = "IMPERSONATION"

        attack_case = {
            "scenario_id": _scenario_id(),
            "scenario_type": "IMPERSONATION",
            "scenario_name": (
                ATTACK_SCENARIOS[
                    "IMPERSONATION"
                ]["name"]
            ),
            "created_at": _timestamp(),

            "original_package_id": (
                package.package_id
            ),

            "original_document_id": (
                document_id
            ),

            "attack_document_id": (
                document_id
            ),

            "attack_case": {
                "document_modified": False,
                "qds_data_modified": True,
                "original_signer": (
                    package.signer_id
                ),
                "impersonated_signer": (
                    impersonated_signer_id.strip()
                ),
            },

            "qds_package": impersonated_package,

            "submitted_document_base64": _encode(
                document_bytes
            ),

            "detection_ready": True,
        }

        return self._save_case(
            attack_case
        )

    def create_replay(
        self,
        package_id: str,
        replay_context_id: str,
    ) -> dict[str, Any]:

        if not replay_context_id.strip():
            raise ValueError(
                "replay_context_id cannot be empty."
            )

        package = self.load_original_package(
            package_id
        )

        document_id = package.document_id

        if document_id is None:
            raise ValueError(
                "QDS package is not associated "
                "with a document."
            )

        document_bytes = (
            self.load_original_document(
                document_id
            )
        )

        attack_case = {
            "scenario_id": _scenario_id(),
            "scenario_type": "REPLAY",
            "scenario_name": (
                ATTACK_SCENARIOS[
                    "REPLAY"
                ]["name"]
            ),
            "created_at": _timestamp(),

            "original_package_id": (
                package.package_id
            ),

            "original_document_id": (
                document_id
            ),

            "attack_document_id": (
                document_id
            ),

            "attack_case": {
                "replayed_package_id": (
                    package.package_id
                ),
                "replay_context_id": (
                    replay_context_id.strip()
                ),
                "reused_qds_data": True,
            },

            "qds_package": package.to_dict(),

            "submitted_document_base64": _encode(
                document_bytes
            ),

            "detection_ready": True,

            "detection_note": (
                "Replay rejection requires a "
                "protocol-specific freshness mechanism."
            ),
        }

        return self._save_case(
            attack_case
        )

    def create_unauthorized_verification(
        self,
        package_id: str,
        verifier_id: str,
        authorized: bool = False,
    ) -> dict[str, Any]:

        if not verifier_id.strip():
            raise ValueError(
                "verifier_id cannot be empty."
            )

        package = self.load_original_package(
            package_id
        )

        document_id = package.document_id

        if document_id is None:
            raise ValueError(
                "QDS package is not associated "
                "with a document."
            )

        document_bytes = (
            self.load_original_document(
                document_id
            )
        )

        attack_case = {
            "scenario_id": _scenario_id(),
            "scenario_type": (
                "UNAUTHORIZED_VERIFICATION"
            ),
            "scenario_name": (
                ATTACK_SCENARIOS[
                    "UNAUTHORIZED_VERIFICATION"
                ]["name"]
            ),
            "created_at": _timestamp(),

            "original_package_id": (
                package.package_id
            ),

            "original_document_id": (
                document_id
            ),

            "attack_document_id": (
                document_id
            ),

            "attack_case": {
                "verifier_id": (
                    verifier_id.strip()
                ),
                "authorized": bool(
                    authorized
                ),
            },

            "qds_package": package.to_dict(),

            "submitted_document_base64": _encode(
                document_bytes
            ),

            "detection_ready": True,

            "detection_note": (
                "Authorization rejection requires "
                "a protocol/system-specific mechanism."
            ),
        }

        return self._save_case(
            attack_case
        )

    def create_quantum_channel_manipulation(
        self,
        package_id: str,
        manipulation: str = "PHASE_FLIP",
        probability: float = 0.05,
    ) -> dict[str, Any]:

        if not manipulation.strip():
            raise ValueError(
                "manipulation cannot be empty."
            )

        if probability < 0 or probability > 1:
            raise ValueError(
                "probability must be between 0 and 1."
            )

        package = self.load_original_package(
            package_id
        )

        document_id = package.document_id

        if document_id is None:
            raise ValueError(
                "QDS package is not associated "
                "with a document."
            )

        document_bytes = (
            self.load_original_document(
                document_id
            )
        )

        attack_case = {
            "scenario_id": _scenario_id(),
            "scenario_type": (
                "QUANTUM_CHANNEL_MANIPULATION"
            ),
            "scenario_name": (
                ATTACK_SCENARIOS[
                    "QUANTUM_CHANNEL_MANIPULATION"
                ]["name"]
            ),
            "created_at": _timestamp(),

            "original_package_id": (
                package.package_id
            ),

            "original_document_id": (
                document_id
            ),

            "attack_document_id": (
                document_id
            ),

            "attack_case": {
                "manipulation": (
                    manipulation.upper()
                ),
                "probability": float(
                    probability
                ),
            },

            "qds_package": package.to_dict(),

            "submitted_document_base64": _encode(
                document_bytes
            ),

            "detection_ready": True,

            "detection_note": (
                "Quantum-channel manipulation is "
                "evaluated by the quantum simulation engine."
            ),
        }

        return self._save_case(
            attack_case
        )