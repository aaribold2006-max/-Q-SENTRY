from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from app.qds.application_service import (
    QSentryApplicationService,
)
from app.qds.attack_experiment import (
    run_attack_experiment,
)
from app.qds.protocols import (
    TeleportationQDSPrototype,
)
from app.qds.storage import (
    list_attack_scenarios,
    load_attack_scenario,
)
import app.qds.storage as qds_storage


# ============================================================================
# Paths
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


# ============================================================================
# FastAPI application
# ============================================================================

app = FastAPI(
    title="Q-SENTRY",
    description=(
        "Quantum Digital Signature Security "
        "Testing Framework"
    ),
    version="2.2.0",
)


# ============================================================================
# Application service
# ============================================================================

service = QSentryApplicationService()

service.register_protocol(
    TeleportationQDSPrototype()
)


# ============================================================================
# Request models
# ============================================================================

class ExperimentRequest(BaseModel):
    """
    Existing quantum experiment endpoint.

    Kept for backward compatibility with the original prototype.
    """

    message_bit: int = Field(
        default=0,
        ge=0,
        le=1,
    )

    basis: str = Field(
        default="X",
    )

    shots: int = Field(
        default=1000,
        gt=0,
    )

    attack: str = Field(
        default="Z",
    )

    noise: str = Field(
        default="PHASE_FLIP",
    )

    noise_probability: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
    )

    threshold: float = Field(
        default=0.058,
        ge=0.0,
        le=1.0,
    )

    seed: int = Field(
        default=42,
    )


class QDSSessionRequest(BaseModel):
    """
    Create a signer-side QDS package.
    """

    protocol_id: str

    signer_id: str

    package_name: str | None = None


class DocumentCreateRequest(BaseModel):
    """
    Create and save a fictional document.
    """

    template_id: str

    signer_id: str

    signature_text: str

    document_name: str | None = None


class SignDocumentRequest(BaseModel):
    """
    Bind a saved document to a saved QDS package.
    """

    document_id: str


class VerificationRequest(BaseModel):
    """
    Normal QDS detection request.
    """

    package_id: str

    document_id: str


class RenameRequest(BaseModel):
    """
    Generic rename request.
    """

    name: str


class DocumentTamperingRequest(BaseModel):
    """
    Create a document tampering attack case.
    """

    package_id: str

    document_id: str

    search_text: str

    replacement_text: str


class ForgeryRequest(BaseModel):
    """
    Create a QDS forgery attack case.
    """

    package_id: str

    forged_signature_data: dict[str, Any]


class ImpersonationRequest(BaseModel):
    """
    Create an impersonation attack case.
    """

    package_id: str

    impersonated_signer_id: str


class ReplayRequest(BaseModel):
    """
    Create a replay attack case.
    """

    package_id: str

    replay_context_id: str


class UnauthorizedVerificationRequest(BaseModel):
    """
    Create an unauthorized verification attack case.
    """

    package_id: str

    verifier_id: str

    authorized: bool = False


class ChannelManipulationRequest(BaseModel):
    """
    Create a quantum-channel manipulation case.
    """

    package_id: str

    manipulation: str = Field(
        default="PHASE_FLIP",
    )

    probability: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
    )


class SimulationRequest(BaseModel):
    """
    Technical simulation controls.
    """

    scenario: str = Field(
        default="NORMAL",
    )

    message_bit: int = Field(
        default=0,
        ge=0,
        le=1,
    )

    basis: str = Field(
        default="X",
    )

    shots: int = Field(
        default=1000,
        gt=0,
    )

    attack: str = Field(
        default="Z",
    )

    threshold: float = Field(
        default=0.058,
        ge=0.0,
        le=1.0,
    )

    seed: int = Field(
        default=42,
    )

    noise: str = Field(
        default="PHASE_FLIP",
    )

    noise_probability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    protocol_id: str | None = None


# ============================================================================
# Frontend
# ============================================================================

@app.get("/")
def dashboard():
    """
    Serve the Q-SENTRY web interface.
    """

    return FileResponse(
        STATIC_DIR / "index.html"
    )


@app.get("/health")
def health():
    """
    Health check.
    """

    return {
        "status": "healthy",
        "system": "Q-SENTRY",
    }


# ============================================================================
# Protocol API
# ============================================================================

@app.get("/api/protocols")
def get_protocols():
    """
    Return registered QDS protocols.
    """

    return {
        "protocols": service.list_protocols()
    }


# ============================================================================
# Document template API
# ============================================================================

@app.get("/api/document-templates")
def get_document_templates():
    """
    Return the five fictional document templates.
    """

    return {
        "templates": (
            service.list_document_templates()
        )
    }


# ============================================================================
# Document API
# ============================================================================

@app.get("/api/documents")
def get_documents():
    """
    Return all saved documents.
    """

    return {
        "documents": (
            service.list_saved_documents()
        )
    }


@app.post("/api/documents/create")
def create_document(
    request: DocumentCreateRequest,
):
    """
    Create and save a fictional demonstration document.
    """

    try:

        document = (
            service.create_demo_document(
                template_id=request.template_id,
                signer_id=request.signer_id,
                signature_text=request.signature_text,
                document_name=request.document_name,
            )
        )

        path = (
            service.save_demo_document(
                document
            )
        )

        return {
            "status": "created",
            "document": {
                "document_id": (
                    document["document_id"]
                ),
                "document_name": (
                    document["document_name"]
                ),
                "template_id": (
                    document["template_id"]
                ),
                "template_name": (
                    document["template_name"]
                ),
                "signer_id": (
                    document["signer_id"]
                ),
                "filename": (
                    document["filename"]
                ),
                "path": str(path),
            },
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/documents/{document_id}/view"
)
def view_document(
    document_id: str,
):
    """
    Display a saved HTML document.
    """

    try:

        document_bytes = (
            service.load_saved_document(
                document_id
            )
        )

        html = document_bytes.decode(
            "utf-8"
        )

        return HTMLResponse(
            content=html
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
        UnicodeDecodeError,
    ) as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.put(
    "/api/documents/{document_id}/rename"
)
def rename_document(
    document_id: str,
    request: RenameRequest,
):
    """
    Rename the user-facing document name.

    The permanent DOC-... identifier does not change.
    """

    try:

        document = (
            service.rename_document(
                document_id=document_id,
                new_name=request.name,
            )
        )

        return {
            "status": "renamed",
            "document": document,
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.delete(
    "/api/documents/{document_id}"
)
def delete_document(
    document_id: str,
):
    """
    Delete a saved document.

    The service prevents deletion when the document
    is still referenced by a saved QDS package.
    """

    try:

        service.delete_document(
            document_id
        )

        return {
            "status": "deleted",
            "document_id": document_id,
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================================
# QDS package API
# ============================================================================

@app.get("/api/qds/packages")
def get_qds_packages():
    """
    Return all saved QDS packages.
    """

    return {
        "packages": (
            service.list_saved_qds_packages()
        )
    }


@app.post("/api/qds/packages/create")
def create_qds_package(
    request: QDSSessionRequest,
):
    """
    Create and save an initial QDS package.
    """

    try:

        package = (
            service.generate_unbound_qds_package(
                protocol_id=request.protocol_id,
                signer_id=request.signer_id,
                package_name=request.package_name,
            )
        )

        path = (
            service.save_qds_package(
                package
            )
        )

        return {
            "status": "created",
            "package": package.to_dict(),
            "path": str(path),
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.put(
    "/api/qds/packages/{package_id}/rename"
)
def rename_qds_package(
    package_id: str,
    request: RenameRequest,
):
    """
    Rename the user-facing QDS package name.

    The permanent QDS-... identifier does not change.
    """

    try:

        package = (
            service.rename_qds_package(
                package_id=package_id,
                new_name=request.name,
            )
        )

        return {
            "status": "renamed",
            "package": {
                "package_id": (
                    package.package_id
                ),
                "package_name": (
                    package.package_name
                ),
                "protocol_id": (
                    package.protocol_id
                ),
                "signer_id": (
                    package.signer_id
                ),
                "document_id": (
                    package.document_id
                ),
            },
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.delete(
    "/api/qds/packages/{package_id}"
)
def delete_qds_package(
    package_id: str,
):
    """
    Delete a saved QDS package.
    """

    try:

        service.delete_qds_package(
            package_id
        )

        return {
            "status": "deleted",
            "package_id": package_id,
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/qds/packages/{package_id}/sign-document"
)
def sign_document(
    package_id: str,
    request: SignDocumentRequest,
):
    """
    Bind a saved document to the QDS package
    and generate the protocol-specific signature data.
    """

    try:

        package = (
            service.load_qds_package(
                package_id
            )
        )

        package = (
            service.sign_document(
                package=package,
                document_id=request.document_id,
            )
        )

        return {
            "status": "signed",
            "package": package.to_dict(),
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================================
# Normal Detection
# ============================================================================

@app.post(
    "/api/detection/verify"
)
def verify_document(
    request: VerificationRequest,
):
    """
    Verify a saved document against saved QDS data.

    The endpoint first exposes the package/document binding state
    explicitly so the dashboard can distinguish:
        - NOT_BOUND
        - MISMATCH
        - VALID

    The existing service-level verification is still responsible for
    the protocol-specific verification decision.
    """

    try:

        # ------------------------------------------------------------------
        # 1. Load the selected QDS package and inspect its stored binding.
        # ------------------------------------------------------------------
        package = service.load_qds_package(
            request.package_id
        )

        package_data = package.to_dict()

        bound_document_id = package_data.get(
            "document_id"
        )

        # ------------------------------------------------------------------
        # 2. No document has been bound to this package yet.
        # ------------------------------------------------------------------
        if not bound_document_id:

            return {
                "status": "NOT_BOUND",
                "result": "NOT_BOUND",
                "binding_status": "NOT_BOUND",
                "package_id": request.package_id,
                "package_document_id": None,
                "selected_document_id": request.document_id,
                "explanation": (
                    "This QDS package has not been bound to a document yet. "
                    "Use Step 3 — Bind & Sign before running detection."
                ),
            }

        # ------------------------------------------------------------------
        # 3. The selected document is different from the document stored
        #    in the QDS package.
        # ------------------------------------------------------------------
        if bound_document_id != request.document_id:

            return {
                "status": "DOCUMENT_MISMATCH",
                "result": "DOCUMENT_MISMATCH",
                "binding_status": "MISMATCH",
                "package_id": request.package_id,
                "package_document_id": bound_document_id,
                "selected_document_id": request.document_id,
                "explanation": (
                    "The selected document does not match the document "
                    "bound to this QDS package."
                ),
            }

        # ------------------------------------------------------------------
        # 4. Package/document IDs match. Run the existing protocol-level
        #    verification logic.
        # ------------------------------------------------------------------
        result = service.verify_document(
            package_id=request.package_id,
            document_id=request.document_id,
        )

        # Make a defensive copy because the service may return a dict
        # containing nested protocol-specific objects.
        if isinstance(result, dict):
            response = dict(result)
        else:
            response = {
                "result": result
            }

        # ------------------------------------------------------------------
        # 5. Explicitly expose the verified document binding in the API
        #    response so the frontend never has to infer it.
        # ------------------------------------------------------------------
        response["package_id"] = request.package_id
        response["package_document_id"] = bound_document_id
        response["selected_document_id"] = request.document_id
        response["binding_status"] = "VALID"
        response["document_binding_status"] = "VALID"

        # Preserve the service's actual security/protocol decision.
        # The service may return the decision inside nested dictionaries,
        # so extract a scalar value instead of converting an object to text.
        def _extract_scalar_decision(value: Any, depth: int = 6) -> Any:
            if value is None or depth < 0:
                return None

            if isinstance(value, (str, int, float, bool)):
                return value

            if isinstance(value, list):
                for item in value:
                    found = _extract_scalar_decision(item, depth - 1)
                    if found not in (None, ""):
                        return found
                return None

            if isinstance(value, dict):
                preferred_keys = (
                    "security_decision",
                    "decision",
                    "status",
                    "result",
                    "verification_status",
                    "verification_result",
                    "protocol_decision",
                    "verdict",
                    "outcome",
                    "verified",
                    "valid",
                    "accepted",
                )

                for key in preferred_keys:
                    if key not in value:
                        continue

                    item = value[key]

                    # Boolean verification fields should become a clear
                    # scalar status rather than the literal True/False.
                    if key in {"verified", "valid", "accepted"} and isinstance(item, bool):
                        return "VERIFIED" if item else "REJECTED"

                    found = _extract_scalar_decision(item, depth - 1)
                    if found not in (None, ""):
                        return found

                for item in value.values():
                    if isinstance(item, (dict, list)):
                        found = _extract_scalar_decision(item, depth - 1)
                        if found not in (None, ""):
                            return found

            return None

        decision = _extract_scalar_decision(response)

        if decision is not None and decision != "":
            response["status"] = str(decision)
            response["result"] = str(decision)
        else:
            response.setdefault("status", "UNKNOWN")
            response.setdefault("result", response["status"])

        if not response.get("explanation"):
            response["explanation"] = (
                "Document ID matches the QDS package binding. "
                "Protocol verification completed."
            )

        return response

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================================
# Attack Lab
# ============================================================================

@app.get("/api/attacks")
def get_attack_scenarios():
    """
    Return the six attack scenario definitions.
    """

    return {
        "scenarios": (
            service.list_attack_scenarios()
        )
    }


@app.post(
    "/api/attacks/document-tampering"
)
def create_document_tampering(
    request: DocumentTamperingRequest,
):
    """
    Create a detection-ready document tampering case.
    """

    try:

        return (
            service.create_document_tampering(
                package_id=request.package_id,
                document_id=request.document_id,
                search_text=request.search_text,
                replacement_text=(
                    request.replacement_text
                ),
            )
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/api/attacks/forgery")
def create_forgery(
    request: ForgeryRequest,
):
    """
    Create a QDS forgery case.
    """

    try:

        return (
            service.create_forgery(
                package_id=request.package_id,
                forged_signature_data=(
                    request.forged_signature_data
                ),
            )
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/attacks/impersonation"
)
def create_impersonation(
    request: ImpersonationRequest,
):
    """
    Create an impersonation case.
    """

    try:

        return (
            service.create_impersonation(
                package_id=request.package_id,
                impersonated_signer_id=(
                    request.impersonated_signer_id
                ),
            )
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/api/attacks/replay")
def create_replay(
    request: ReplayRequest,
):
    """
    Create a replay case.
    """

    try:

        return (
            service.create_replay(
                package_id=request.package_id,
                replay_context_id=(
                    request.replay_context_id
                ),
            )
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/attacks/unauthorized-verification"
)
def create_unauthorized_verification(
    request: UnauthorizedVerificationRequest,
):
    """
    Create an unauthorized verification case.
    """

    try:

        return (
            service.create_unauthorized_verification(
                package_id=request.package_id,
                verifier_id=request.verifier_id,
                authorized=request.authorized,
            )
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/attacks/quantum-channel"
)
def create_quantum_channel_manipulation(
    request: ChannelManipulationRequest,
):
    """
    Create a quantum-channel manipulation case.
    """

    try:

        return (
            service.create_quantum_channel_manipulation(
                package_id=request.package_id,
                manipulation=request.manipulation,
                probability=request.probability,
            )
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================================
# Saved Attack Cases
# ============================================================================

@app.get("/api/attack-cases")
def get_attack_cases():
    """
    Return saved detection-ready attack cases.
    """

    try:

        scenarios = list_attack_scenarios()

        cases: list[dict[str, Any]] = []

        for item in scenarios:

            scenario = item.get(
                "scenario",
                {},
            )

            if not isinstance(
                scenario,
                dict,
            ):
                continue

            cases.append(
                {
                    "scenario_id": (
                        scenario.get(
                            "scenario_id"
                        )
                    ),
                    "scenario_type": (
                        scenario.get(
                            "scenario_type"
                        )
                    ),
                    "scenario_name": (
                        scenario.get(
                            "scenario_name"
                        )
                    ),
                    "created_at": (
                        scenario.get(
                            "created_at"
                        )
                    ),
                    "original_package_id": (
                        scenario.get(
                            "original_package_id"
                        )
                    ),
                    "original_document_id": (
                        scenario.get(
                            "original_document_id"
                        )
                    ),
                    "attack_document_id": (
                        scenario.get(
                            "attack_document_id"
                        )
                    ),
                    "detection_ready": (
                        scenario.get(
                            "detection_ready",
                            False,
                        )
                    ),
                }
            )

        return {
            "attack_cases": cases
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/attack-cases/{scenario_id}"
)
def get_attack_case(
    scenario_id: str,
):
    """
    Return the complete saved attack case.
    """

    try:

        return load_attack_scenario(
            scenario_id
        )

    except (
        KeyError,
        ValueError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/attack-cases/{scenario_id}/document"
)
def view_attack_document(
    scenario_id: str,
):
    """
    Open an attack case as a visual comparison:

        LEFT  = original signed document
        RIGHT = attacked / modified representation

    The right-hand document is reconstructed from the saved attack data so
    users can understand what changed by simply looking at the document.
    Context-only attacks (replay, unauthorized verification and channel
    manipulation) keep the original document content but receive an
    attack-specific visual stamp inside the attacked view.
    """

    import base64
    import html as html_module
    import re

    def _escape(value: Any) -> str:
        return html_module.escape(
            str(value if value is not None else ""),
            quote=True,
        )

    def _read_original_document(scenario_data: dict[str, Any]) -> str:
        original_document_id = scenario_data.get(
            "original_document_id"
        )

        if not original_document_id:
            raise ValueError(
                "Attack case does not reference its original document."
            )

        original_bytes = service.load_saved_document(
            original_document_id
        )
        return original_bytes.decode("utf-8")

    def _decode_saved_attack_document(
        scenario_data: dict[str, Any],
    ) -> str | None:
        encoded = scenario_data.get(
            "submitted_document_base64"
        )

        if not encoded:
            return None

        try:
            document_bytes = base64.b64decode(
                encoded.encode("ascii"),
                validate=True,
            )
            return document_bytes.decode("utf-8")
        except (
            ValueError,
            UnicodeDecodeError,
            base64.binascii.Error,
        ):
            return None

    def _body_insert(document_html: str, fragment: str) -> str:
        lower = document_html.lower()
        body_pos = lower.find("<body")

        if body_pos >= 0:
            body_end = document_html.find(">", body_pos)
            if body_end >= 0:
                return (
                    document_html[:body_end + 1]
                    + fragment
                    + document_html[body_end + 1:]
                )

        return fragment + document_html

    def _attack_banner(
        title: str,
        summary: str,
        detail_rows: list[tuple[str, str]],
        visual_change: str,
    ) -> str:
        rows = "".join(
            "<div style='display:grid;grid-template-columns:minmax(130px,190px) 1fr;gap:6px 12px;"
            "padding:8px 0;border-top:1px solid #fecaca;'>"
            f"<div style='font-weight:900;color:#7f1d1d;'>{_escape(label)}</div>"
            f"<div style='color:#111827;'>{_escape(value)}</div>"
            "</div>"
            for label, value in detail_rows
        )

        return (
            "<div style='margin:0 0 18px;padding:20px 22px;"
            "border:3px solid #dc2626;border-radius:14px;"
            "background:linear-gradient(180deg,#fff1f2,#ffffff);"
            "font-family:Arial,sans-serif;color:#111827;'>"
            "<div style='display:inline-flex;align-items:center;gap:8px;padding:7px 11px;border-radius:999px;"
            "background:#b91c1c;color:#ffffff;font-size:12px;font-weight:900;"
            "letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px;'>"
            "⚠ ATTACKED DOCUMENT</div>"
            f"<div style='font-size:26px;font-weight:900;line-height:1.2;margin-bottom:8px;'>"
            f"{_escape(title)}</div>"
            f"<div style='font-size:16px;line-height:1.55;color:#374151;margin-bottom:12px;'>"
            f"{_escape(summary)}</div>"
            "<div style='padding:13px 15px;margin:12px 0;background:#fef2f2;border:2px solid #fca5a5;"
            "border-radius:10px;'>"
            "<div style='font-size:11px;font-weight:900;color:#991b1b;text-transform:uppercase;letter-spacing:.07em;'>"
            "VISIBLE ATTACK EFFECT</div>"
            f"<div style='font-size:17px;font-weight:900;line-height:1.45;margin-top:5px;color:#111827;'>"
            f"{_escape(visual_change)}</div>"
            "</div>"
            f"<div>{rows}</div>"
            "</div>"
        )

    def _repair_bare_data_images(document_html: str) -> str:
        """
        Some saved documents contain a raw data:image/... base64 string as
        visible text instead of an <img> element. Convert only those bare
        data URIs into an actual image element. Existing src=... data URIs
        are left untouched.
        """

        data_pattern = re.compile(
            r"data:image/(?:png|jpeg|jpg|gif|webp);base64,[A-Za-z0-9+/=]+",
            re.IGNORECASE,
        )

        def _replace(match: re.Match[str]) -> str:
            prefix = document_html[max(0, match.start() - 16):match.start()]
            if re.search(
                r"src\s*=\s*['\"]\s*$",
                prefix,
                flags=re.IGNORECASE,
            ):
                return match.group(0)

            uri = match.group(0)
            return (
                "<div class='qs-signature-image' style='margin:8px 0 4px;text-align:center;'>"
                f"<img src='{uri}' alt='Digital signature' "
                "style='max-width:340px;max-height:110px;object-fit:contain;display:inline-block;'>"
                "</div>"
            )

        return data_pattern.sub(_replace, document_html)

    def _inject_head_style(document_html: str, css: str) -> str:
        lower = document_html.lower()
        style_tag = f"<style>{css}</style>"
        head_pos = lower.find("<head")
        if head_pos >= 0:
            head_end = document_html.find(">", head_pos)
            if head_end >= 0:
                return (
                    document_html[:head_end + 1]
                    + style_tag
                    + document_html[head_end + 1:]
                )
        return style_tag + document_html

    def _body_insert(document_html: str, fragment: str) -> str:
        lower = document_html.lower()
        body_pos = lower.find("<body")

        if body_pos >= 0:
            body_end = document_html.find(">", body_pos)
            if body_end >= 0:
                return (
                    document_html[:body_end + 1]
                    + fragment
                    + document_html[body_end + 1:]
                )

        return fragment + document_html

    def _extract_visible_signer(document_html: str) -> str:
        match = re.search(
            r"Signer\s*:\s*</?(?:strong|span|b)?[^>]*>\s*([^<\n]+)",
            document_html,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()
        return "ORIGINAL SIGNER"

    def _replace_signer_line(document_html: str, attacker: str) -> tuple[str, bool]:
        replacement = (
            r"\1"
            "<span style='background:#fee2e2;border:2px solid #ef4444;"
            "padding:3px 7px;border-radius:6px;color:#991b1b;font-weight:900;'>"
            + _escape(attacker)
            + " — IMPERSONATED"
            "</span>"
        )

        updated, count = re.subn(
            r"(Signer\s*:\s*)([^<\n]+)",
            replacement,
            document_html,
            count=1,
            flags=re.IGNORECASE,
        )
        return updated, count > 0

    def _replace_signature_image_with_forged_marker(document_html: str) -> tuple[str, bool]:
        forged_visual = (
            "<div style='margin:10px auto 6px;max-width:390px;padding:18px 14px;"
            "border:3px dashed #dc2626;border-radius:10px;background:#fff1f2;text-align:center;>"
            "<div style='font-size:11px;font-weight:900;letter-spacing:.10em;color:#b91c1c;text-transform:uppercase;'>"
            "FORGED SIGNATURE — SIMULATED</div>"
            "<div style='font-family:cursive;font-style:italic;font-size:30px;font-weight:900;"
            "color:#7f1d1d;margin-top:6px;transform:rotate(-4deg);>FORGED SIGNATURE</div>"
            "<div style='font-size:12px;font-weight:800;color:#991b1b;margin-top:6px;'>"
            "Signature authentication data altered for this test case</div>"
            "</div>"
        )

        image_pattern = re.compile(
            r"<img\b[^>]*\bsrc\s*=\s*['\"]data:image/[^'\"]+['\"][^>]*>",
            re.IGNORECASE,
        )
        updated, count = image_pattern.subn(
            forged_visual,
            document_html,
            count=1,
        )

        if count:
            return updated, True

        # Fallback when no signature image is present.
        marker = (
            "<div style='margin:12px 0;padding:18px;border:3px dashed #dc2626;"
            "background:#fff1f2;border-radius:10px;text-align:center;'>"
            "<div style='font-size:20px;font-weight:900;color:#991b1b;'>FORGED SIGNATURE — SIMULATED</div>"
            "<div style='margin-top:5px;font-size:13px;color:#7f1d1d;'>Signature authentication data altered for this test case.</div>"
            "</div>"
        )

        updated, count = re.subn(
            r"(Authorized\s+Signature[^<]*</[^>]+>)",
            r"\1" + marker,
            document_html,
            count=1,
            flags=re.IGNORECASE,
        )
        return updated, count > 0

    def _attack_watermark(attack_type: str) -> str:
        label = attack_type.replace("_", " ").upper()
        return (
            "<div style='position:absolute;right:18px;top:120px;z-index:5;"
            "padding:8px 12px;border:3px solid #dc2626;border-radius:7px;"
            "color:#b91c1c;background:rgba(255,255,255,.92);font:900 15px/1 Arial,sans-serif;"
            "letter-spacing:.08em;transform:rotate(4deg);'>"
            f"ATTACK: {_escape(label)}"
            "</div>"
        )

    def _simple_explanation(
        attack_type: str,
        scenario_data: dict[str, Any],
    ) -> tuple[str, str, str, list[tuple[str, str]], str]:
        attack_type = attack_type.upper()

        if attack_type == "DOCUMENT_TAMPERING":
            search_text = str(
                scenario_data.get("search_text") or "original text"
            )
            replacement_text = str(
                scenario_data.get("replacement_text") or "changed text"
            )
            return (
                "Document Tampering",
                "The attacker changed information inside the document. The left side is the original document; the right side shows the changed version.",
                "Look for the changed wording highlighted in the attacked document.",
                [
                    ("Original text", search_text),
                    ("Attacked text", replacement_text),
                    ("What Q-SENTRY should notice", "The document content is no longer the same as the signed original."),
                ],
                "Document text is visibly changed and highlighted.",
            )

        if attack_type == "FORGERY":
            forged = scenario_data.get("forged_signature_data")
            if isinstance(forged, dict):
                forged_text = ", ".join(
                    f"{k}={v}" for k, v in list(forged.items())[:4]
                )
            else:
                forged_text = str(forged or "Signature data was changed")
            return (
                "Forgery",
                "The document content can remain the same, but the signature/authentication condition is changed to simulate a forgery attempt.",
                "Look directly at the signature area: the legitimate signature is replaced by a clearly marked forged signature.",
                [
                    ("Original state", "Legitimate QDS signature"),
                    ("Attacked state", "Forged signature condition"),
                    ("Forged data", forged_text),
                ],
                "The signature area is visibly replaced with a FORGED SIGNATURE marker.",
            )

        if attack_type == "IMPERSONATION":
            signer = str(
                scenario_data.get("original_signer_id")
                or scenario_data.get("signer_id")
                or "Original signer"
            )
            attacker = str(
                scenario_data.get("impersonated_signer_id")
                or "ATTACKER"
            )
            return (
                "Impersonation",
                "The attacker is pretending to be a different signer. The left side shows the legitimate signer; the right side visibly changes the signer identity used in the test.",
                "Look at the Signer field on the right: it is highlighted as an impersonated identity.",
                [
                    ("Original signer", signer),
                    ("Attacker identity", attacker),
                    ("What Q-SENTRY should notice", "The signer context is not the legitimate signer."),
                ],
                "The signer identity itself is highlighted and marked IMPERSONATED.",
            )

        if attack_type == "REPLAY":
            context = str(
                scenario_data.get("replay_context_id")
                or scenario_data.get("new_verification_context")
                or "NEW_CONTEXT"
            )
            return (
                "Replay",
                "The same previously valid QDS information is reused in a new verification context. The underlying certificate can remain unchanged, so the replay context is made visible inside the attacked document.",
                "Look for the large REPLAYED stamp and the new verification context.",
                [
                    ("Original context", "Original signed verification"),
                    ("Replay context", context),
                    ("What Q-SENTRY should notice", "Previously valid information is being reused outside its original context."),
                ],
                "A REPLAYED stamp and a new verification-context card are shown on the attacked document.",
            )

        if attack_type == "UNAUTHORIZED_VERIFICATION":
            verifier = str(
                scenario_data.get("verifier_id")
                or "UNAUTHORIZED-VERIFIER"
            )
            return (
                "Unauthorized Verification",
                "The document can remain unchanged, but the verification request is made by a verifier without the required authorization.",
                "Look for the authorization block showing the verifier and DENIED state.",
                [
                    ("Verifier", verifier),
                    ("Authorization", "UNAUTHORIZED / DENIED"),
                    ("What Q-SENTRY should notice", "The verification request has no valid authorization."),
                ],
                "The attacked document shows an UNAUTHORIZED VERIFIER and an AUTHORIZATION DENIED state.",
            )

        if attack_type == "QUANTUM_CHANNEL_MANIPULATION":
            manipulation = str(
                scenario_data.get("manipulation")
                or scenario_data.get("attack_model")
                or "PHASE_FLIP"
            )
            probability = str(
                scenario_data.get("probability")
                if scenario_data.get("probability") is not None
                else "0.10"
            )
            return (
                "Quantum Channel Manipulation",
                "The document can remain unchanged while the quantum channel carrying the signature information is intentionally disturbed before measurement.",
                "Look at the quantum-channel diagram: the attacked path is visibly marked as manipulated.",
                [
                    ("Manipulation", manipulation),
                    ("Probability", probability),
                    ("What Q-SENTRY should notice", "The measured behaviour can deviate from the legitimate baseline."),
                ],
                "A visible quantum-channel disturbance diagram marks the manipulated communication path.",
            )

        return (
            attack_type.replace("_", " ").title(),
            "The right side shows the attack condition applied to this saved test case.",
            "Compare the two sides to see what changed.",
            [("Attack type", attack_type)],
            "An attack-specific visual marker is shown.",
        )

    def _build_attacked_document(
        original_html: str,
        scenario_data: dict[str, Any],
        attack_type: str,
    ) -> str:
        attack_type = attack_type.upper()

        (
            title,
            summary,
            _notice,
            detail_rows,
            visual_change,
        ) = _simple_explanation(
            attack_type,
            scenario_data,
        )

        saved_attack_html = _decode_saved_attack_document(
            scenario_data
        )

        if attack_type == "DOCUMENT_TAMPERING" and saved_attack_html:
            attacked_html = saved_attack_html
        else:
            attacked_html = original_html

        attacked_html = _repair_bare_data_images(attacked_html)

        if attack_type == "DOCUMENT_TAMPERING":
            search_text = str(
                scenario_data.get("search_text") or ""
            )
            replacement_text = str(
                scenario_data.get("replacement_text") or ""
            )

            if search_text and replacement_text and search_text in attacked_html:
                attacked_html = attacked_html.replace(
                    search_text,
                    (
                        "<mark style='background:#fef08a;border:3px solid #ca8a04;"
                        "padding:3px 6px;font-weight:900;border-radius:5px;'>"
                        + _escape(replacement_text)
                        + "</mark>"
                    ),
                    1,
                )

        elif attack_type == "FORGERY":
            attacked_html, _ = _replace_signature_image_with_forged_marker(
                attacked_html
            )

        elif attack_type == "IMPERSONATION":
            attacker = str(
                scenario_data.get("impersonated_signer_id")
                or "ATTACKER"
            )
            attacked_html, replaced = _replace_signer_line(
                attacked_html,
                attacker,
            )
            if not replaced:
                attacked_html = _body_insert(
                    attacked_html,
                    (
                        "<div style='margin:0 0 18px;padding:15px;border:3px solid #dc2626;"
                        "border-radius:10px;background:#fff1f2;font:900 18px/1.4 Arial,sans-serif;color:#991b1b;'>"
                        f"SIGNER: {_escape(attacker)} — IMPERSONATED"
                        "</div>"
                    ),
                )

        elif attack_type == "REPLAY":
            context = str(
                scenario_data.get("replay_context_id")
                or scenario_data.get("new_verification_context")
                or "NEW_CONTEXT"
            )
            replay_visual = (
                "<div style='margin:0 0 18px;padding:16px;border:3px dashed #dc2626;"
                "background:#fff1f2;border-radius:12px;font-family:Arial,sans-serif;text-align:center;'>"
                "<div style='display:inline-block;padding:7px 12px;background:#b91c1c;color:#fff;"
                "border-radius:6px;font-size:13px;font-weight:900;letter-spacing:.08em;'>"
                "REPLAYED SIGNATURE</div>"
                f"<div style='font-size:21px;font-weight:900;color:#7f1d1d;margin-top:10px;'>NEW VERIFICATION CONTEXT</div>"
                f"<div style='font-size:15px;font-weight:800;color:#991b1b;margin-top:5px;'>"
                f"{_escape(context)}</div>"
                "<div style='font-size:13px;color:#7f1d1d;margin-top:7px;'>Previously valid QDS information is being reused here.</div>"
                "</div>"
            )
            attacked_html = _body_insert(attacked_html, replay_visual)

        elif attack_type == "UNAUTHORIZED_VERIFICATION":
            verifier = str(
                scenario_data.get("verifier_id")
                or "UNAUTHORIZED-VERIFIER"
            )
            auth_visual = (
                "<div style='margin:0 0 18px;padding:16px;border:3px solid #dc2626;"
                "background:#fff1f2;border-radius:12px;font-family:Arial,sans-serif;'>"
                "<div style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center;'>"
                "<div style='font-size:22px;font-weight:900;color:#7f1d1d;'>UNAUTHORIZED VERIFICATION</div>"
                "<div style='padding:7px 11px;border-radius:999px;background:#b91c1c;color:#fff;"
                "font-size:12px;font-weight:900;letter-spacing:.07em;'>ACCESS DENIED</div>"
                "</div>"
                f"<div style='margin-top:12px;font-size:16px;color:#111827;'><b>Verifier:</b> "
                f"<span style='color:#991b1b;font-weight:900;'>{_escape(verifier)}</span></div>"
                "<div style='margin-top:5px;font-size:14px;color:#7f1d1d;font-weight:700;'>"
                "Authorization state: NOT AUTHORIZED</div>"
                "</div>"
            )
            attacked_html = _body_insert(attacked_html, auth_visual)

        elif attack_type == "QUANTUM_CHANNEL_MANIPULATION":
            manipulation = str(
                scenario_data.get("manipulation")
                or scenario_data.get("attack_model")
                or "PHASE_FLIP"
            )
            probability = str(
                scenario_data.get("probability")
                if scenario_data.get("probability") is not None
                else "0.10"
            )
            channel_visual = (
                "<div style='margin:0 0 18px;padding:16px;border:3px solid #dc2626;"
                "background:#fff1f2;border-radius:12px;font-family:Arial,sans-serif;'>"
                "<div style='font-size:21px;font-weight:900;color:#7f1d1d;'>QUANTUM CHANNEL MANIPULATION</div>"
                "<div style='margin-top:14px;display:grid;grid-template-columns:1fr auto 1fr auto 1fr;"
                "gap:8px;align-items:center;text-align:center;'>"
                "<div style='padding:11px 7px;border:2px solid #94a3b8;background:#fff;border-radius:8px;font-weight:900;'>SIGNER</div>"
                "<div style='font-size:24px;font-weight:900;color:#64748b;'>→</div>"
                "<div style='padding:11px 7px;border:3px solid #dc2626;background:#fee2e2;border-radius:8px;font-weight:900;color:#991b1b;'>"
                "⚠ MANIPULATED</div>"
                "<div style='font-size:24px;font-weight:900;color:#64748b;'>→</div>"
                "<div style='padding:11px 7px;border:2px solid #94a3b8;background:#fff;border-radius:8px;font-weight:900;'>VERIFIER</div>"
                "</div>"
                f"<div style='margin-top:12px;display:flex;gap:18px;flex-wrap:wrap;font-size:14px;line-height:1.5;'>"
                f"<div><b>Manipulation:</b> {_escape(manipulation)}</div>"
                f"<div><b>Probability:</b> {_escape(probability)}</div>"
                "</div>"
                "<div style='margin-top:7px;font-size:13px;color:#7f1d1d;font-weight:700;'>"
                "The attack is applied to the simulated quantum communication path, not to the document text.</div>"
                "</div>"
            )
            attacked_html = _body_insert(attacked_html, channel_visual)

        # Common attack banner + visual watermark make the right-hand document
        # unmistakable for every attack type, while the attack-specific content
        # above shows what was actually changed or simulated.
        banner = _attack_banner(
            title,
            summary,
            detail_rows,
            visual_change,
        )

        attacked_html = _body_insert(
            attacked_html,
            banner,
        )

        css = (
            "body{position:relative;}"
            ".qs-attack-watermark{pointer-events:none;}"
        )
        attacked_html = _inject_head_style(
            attacked_html,
            css,
        )

        watermark = _attack_watermark(attack_type)
        attacked_html = _body_insert(
            attacked_html,
            watermark,
        )

        return attacked_html

    def _frame_document(document_html: str, label: str, attacked: bool = False) -> str:
        header_bg = "#fff1f2" if attacked else "#eff6ff"
        header_border = "#fecaca" if attacked else "#bfdbfe"
        header_text = "#b91c1c" if attacked else "#1d4ed8"
        badge = (
            "<span style='margin-left:8px;padding:4px 8px;border-radius:999px;"
            "background:#b91c1c;color:#ffffff;font-size:10px;font-weight:900;'>ATTACK</span>"
            if attacked
            else "<span style='margin-left:8px;padding:4px 8px;border-radius:999px;"
                 "background:#1d4ed8;color:#ffffff;font-size:10px;font-weight:900;'>TRUSTED</span>"
        )
        return (
            "<section style='min-width:0;background:#ffffff;border:2px solid "
            + header_border
            + ";border-radius:14px;overflow:hidden;box-shadow:0 3px 10px rgba(15,23,42,.06);'>"
            f"<div style='padding:13px 15px;background:{header_bg};border-bottom:1px solid {header_border};"
            f"font-family:Arial,sans-serif;font-size:15px;font-weight:900;color:{header_text};'>"
            f"{_escape(label)}{badge}</div>"
            "<iframe sandbox='allow-same-origin'"
            " style='display:block;width:100%;height:760px;border:0;background:#ffffff;'"
            f" srcdoc='{_escape(document_html)}'></iframe>"
            "</section>"
        )

    try:
        scenario = load_attack_scenario(scenario_id)

        attack_type = str(
            scenario.get("scenario_type")
            or scenario.get("attack_type")
            or "ATTACK"
        ).upper()

        original_html = _read_original_document(
            scenario
        )

        attacked_html = _build_attacked_document(
            original_html,
            scenario,
            attack_type,
        )

        (
            title,
            summary,
            notice,
            detail_rows,
            visual_change,
        ) = _simple_explanation(
            attack_type,
            scenario,
        )

        detail_html = "".join(
            "<div style='padding:13px 15px;border-top:1px solid #e5e7eb;'>"
            f"<div style='font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.06em;"
            f"color:#64748b;margin-bottom:4px;'>{_escape(label)}</div>"
            f"<div style='font-size:16px;line-height:1.5;color:#111827;'>{_escape(value)}</div>"
            "</div>"
            for label, value in detail_rows
        )

        wrapper = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>Q-SENTRY — {_escape(title)} — Document Comparison</title>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "</head><body style='margin:0;background:#f1f5f9;color:#111827;'>"
            "<div style='font-family:Arial,sans-serif;padding:22px;max-width:1500px;margin:0 auto;'>"
            "<div style='background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:24px 26px;margin-bottom:18px;'>"
            "<div style='font-size:12px;font-weight:900;letter-spacing:.08em;color:#1d4ed8;text-transform:uppercase;margin-bottom:8px;'>"
            "Q-SENTRY ATTACK DOCUMENT COMPARISON</div>"
            f"<h1 style='margin:0 0 10px;font-size:28px;line-height:1.2;'>{_escape(title)}</h1>"
            f"<p style='margin:0 0 16px;font-size:18px;line-height:1.65;color:#374151;'>{_escape(summary)}</p>"
            "<div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;'>"
            "<div style='padding:15px;border-radius:12px;background:#f8fafc;border:1px solid #e5e7eb;'>"
            "<div style='font-size:12px;font-weight:900;color:#64748b;text-transform:uppercase;'>LEFT</div>"
            "<div style='font-size:17px;font-weight:900;margin-top:4px;'>Original Document</div>"
            "<div style='font-size:14px;color:#64748b;margin-top:4px;'>The legitimate signed document.</div>"
            "</div>"
            "<div style='padding:15px;border-radius:12px;background:#fff1f2;border:1px solid #fecaca;'>"
            "<div style='font-size:12px;font-weight:900;color:#b91c1c;text-transform:uppercase;'>RIGHT</div>"
            "<div style='font-size:17px;font-weight:900;margin-top:4px;'>Attacked Document</div>"
            "<div style='font-size:14px;color:#64748b;margin-top:4px;'>The attack condition is shown here.</div>"
            "</div>"
            "<div style='padding:15px;border-radius:12px;background:#eff6ff;border:1px solid #bfdbfe;'>"
            "<div style='font-size:12px;font-weight:900;color:#1d4ed8;text-transform:uppercase;'>WHAT TO NOTICE</div>"
            f"<div style='font-size:17px;font-weight:900;margin-top:4px;'>{_escape(notice)}</div>"
            "<div style='font-size:14px;color:#64748b;margin-top:4px;'>Compare the same area on both sides.</div>"
            "</div>"
            "</div></div>"
            "<div style='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;align-items:start;'>"
            f"{_frame_document(original_html, 'ORIGINAL DOCUMENT', attacked=False)}"
            f"{_frame_document(attacked_html, 'ATTACKED / MODIFIED DOCUMENT', attacked=True)}"
            "</div>"
            "<div style='margin-top:18px;background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;'>"
            "<div style='padding:18px 20px;background:#eff6ff;border-bottom:1px solid #dbeafe;'>"
            "<div style='font-size:12px;font-weight:900;letter-spacing:.08em;color:#1d4ed8;text-transform:uppercase;'>SIMPLE EXPLANATION</div>"
            f"<div style='font-size:22px;font-weight:900;margin-top:5px;'>{_escape(notice)}</div>"
            f"<div style='font-size:18px;line-height:1.65;color:#374151;margin-top:8px;'>{_escape(summary)}</div>"
            f"<div style='margin-top:12px;padding:13px 15px;background:#fff7ed;border:2px solid #fdba74;border-radius:10px;"
            "font-size:16px;line-height:1.5;color:#7c2d12;>"
            "<strong>What is visibly different on the attacked side?</strong><br>"
            f"{_escape(visual_change)}"
            "</div>"
            "</div>"
            f"{detail_html}"
            "</div>"
            "<div style='margin-top:14px;font-size:12px;line-height:1.6;color:#64748b;'>"
            "Q-SENTRY comparison view. Context-only attacks may leave the visible document unchanged; in those cases the attacked side shows the changed security context inside the document view."
            "</div></div></body></html>"
        )

        return HTMLResponse(
            content=wrapper
        )

    except (
        KeyError,
        ValueError,
        OSError,
        UnicodeDecodeError,
        base64.binascii.Error,
    ) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/attack-cases/{scenario_id}/verify"
)
def verify_attack_case(
    scenario_id: str,
):
    """
    Send a saved attack case directly into Detection and expose the
    document/QDS binding state alongside the attack result.
    """

    try:
        result = service.verify_attack_scenario(
            scenario_id
        )

        response = (
            dict(result)
            if isinstance(result, dict)
            else {"result": result}
        )

        scenario = load_attack_scenario(
            scenario_id
        )

        original_package_id = scenario.get(
            "original_package_id"
        ) or scenario.get("package_id")

        original_document_id = scenario.get(
            "original_document_id"
        )

        attack_document_id = scenario.get(
            "attack_document_id"
        )

        bound_document_id = None
        package = None

        if original_package_id:
            try:
                package = service.load_qds_package(
                    original_package_id
                )
                package_data = package.to_dict()
                bound_document_id = package_data.get(
                    "document_id"
                )
            except (
                KeyError,
                ValueError,
                TypeError,
                OSError,
            ):
                bound_document_id = None

        # The package binding is about the original signed document.
        # For document tampering, the attack document is intentionally a
        # different artifact and therefore should be reported as MISMATCH.
        if bound_document_id is None:
            binding_status = "UNKNOWN"
        elif attack_document_id:
            binding_status = (
                "VALID"
                if attack_document_id == bound_document_id
                else "MISMATCH"
            )
        elif original_document_id:
            binding_status = (
                "VALID"
                if original_document_id == bound_document_id
                else "MISMATCH"
            )
        else:
            binding_status = "UNKNOWN"

        # Explicit attack metadata makes the detection result self-contained.
        response["scenario_id"] = scenario_id
        response["scenario_type"] = (
            scenario.get("scenario_type")
            or scenario.get("attack_type")
        )
        response["original_package_id"] = original_package_id
        response["package_document_id"] = bound_document_id
        response["original_document_id"] = original_document_id
        response["attack_document_id"] = attack_document_id
        response["binding_status"] = binding_status
        response["document_binding_status"] = binding_status

        if not response.get("explanation"):
            attack_type = str(
                response.get("scenario_type") or "ATTACK"
            ).upper()

            if binding_status == "MISMATCH":
                response["explanation"] = (
                    f"{attack_type.replace('_', ' ').title()} case: the attack artifact "
                    "does not match the document bound to the QDS package."
                )
            elif binding_status == "VALID":
                response["explanation"] = (
                    f"{attack_type.replace('_', ' ').title()} case: the QDS package remains "
                    "bound to the original document; the attack condition is evaluated separately."
                )

        return response

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================================
# Attack Case Deletion Helpers
# ============================================================================

def _collect_candidate_paths(value: Any, key_hint: str = "") -> list[Path]:
    """
    Collect file/directory paths embedded in an attack-case record.

    This intentionally only accepts paths that resolve inside the Q-SENTRY
    project root, preventing deletion outside the application directory.
    """

    candidates: list[Path] = []
    project_root = BASE_DIR.parent.resolve()

    if isinstance(value, dict):
        for key, item in value.items():
            candidates.extend(_collect_candidate_paths(item, str(key)))
        return candidates

    if isinstance(value, list):
        for item in value:
            candidates.extend(_collect_candidate_paths(item, key_hint))
        return candidates

    if not isinstance(value, str):
        return candidates

    key_lower = key_hint.lower()
    looks_like_path = any(token in key_lower for token in (
        "path",
        "file",
        "filename",
        "location",
    ))

    if not looks_like_path:
        return candidates

    try:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = project_root / candidate
        candidate = candidate.resolve()

        try:
            candidate.relative_to(project_root)
        except ValueError:
            return candidates

        candidates.append(candidate)
    except (OSError, RuntimeError, ValueError):
        pass

    return candidates


def _delete_attack_case_record(scenario_id: str) -> bool:
    """
    Delete a saved attack case using the project's existing storage API when
    available, with a safe filesystem fallback for older storage versions.
    """

    # 1. Prefer an explicitly implemented storage/service delete function.
    for function_name in (
        "delete_attack_scenario",
        "delete_attack_case",
        "remove_attack_scenario",
        "remove_attack_case",
    ):
        function = getattr(qds_storage, function_name, None)
        if callable(function):
            function(scenario_id)
            return True

    for function_name in (
        "delete_attack_case",
        "delete_attack_scenario",
        "remove_attack_case",
        "remove_attack_scenario",
    ):
        function = getattr(service, function_name, None)
        if callable(function):
            function(scenario_id)
            return True

    # 2. Load the record so we can discover explicitly stored artifact paths.
    scenario = load_attack_scenario(scenario_id)

    try:
        scenarios = list_attack_scenarios()
    except Exception:
        scenarios = []

    matched_record: Any = scenario

    for item in scenarios:
        candidate = item.get("scenario", item) if isinstance(item, dict) else {}
        if isinstance(candidate, dict) and str(candidate.get("scenario_id", "")) == scenario_id:
            matched_record = item
            break

    deleted_any = False

    for candidate_path in _collect_candidate_paths(matched_record):
        if candidate_path.is_file():
            candidate_path.unlink()
            deleted_any = True
        elif candidate_path.is_dir() and candidate_path.name == scenario_id:
            import shutil
            shutil.rmtree(candidate_path)
            deleted_any = True

    # 3. Safe fallback for per-case files named with the scenario ID.
    #    Only inspect conventional Q-SENTRY storage locations.
    project_root = BASE_DIR.parent.resolve()
    search_roots = [
        project_root / "data",
        project_root / "storage",
        project_root / "attack_cases",
        project_root / "attack_scenarios",
        BASE_DIR / "data",
        BASE_DIR / "storage",
    ]

    allowed_suffixes = {
        ".json", ".html", ".txt", ".bin", ".dat", ".pkl", ".pickle"
    }

    for root in search_roots:
        if not root.exists() or not root.is_dir():
            continue

        try:
            for candidate_path in root.rglob("*"):
                if not candidate_path.is_file():
                    continue
                if scenario_id not in candidate_path.name:
                    continue
                if candidate_path.suffix.lower() not in allowed_suffixes:
                    continue

                resolved = candidate_path.resolve()
                try:
                    resolved.relative_to(project_root)
                except ValueError:
                    continue

                resolved.unlink()
                deleted_any = True
        except OSError:
            continue

    if not deleted_any:
        raise KeyError(
            f"Attack case '{scenario_id}' exists, but its storage record could not be located for deletion."
        )

    return True


# ============================================================================
# Saved Attack Case Deletion API
# ============================================================================

@app.delete("/api/attack-cases/{scenario_id}")
def delete_attack_case(scenario_id: str):
    """Delete a saved attack case without touching its original document/package."""

    try:
        _delete_attack_case_record(scenario_id)
        return {
            "status": "deleted",
            "scenario_id": scenario_id,
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, TypeError, OSError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/attack-cases/{scenario_id}/delete")
def delete_attack_case_post(scenario_id: str):
    """
    POST alias for environments/clients that do not issue DELETE reliably.
    """

    return delete_attack_case(scenario_id)


# ============================================================================
# Simulation
# ============================================================================

@app.post(
    "/api/simulation/run"
)
def run_simulation(
    request: SimulationRequest,
):
    """
    Run the controlled quantum simulation.
    """

    try:

        return service.run_simulation(
            scenario=request.scenario,
            message_bit=request.message_bit,
            basis=request.basis,
            shots=request.shots,
            attack=request.attack,
            threshold=request.threshold,
            seed=request.seed,
            noise=request.noise,
            noise_probability=(
                request.noise_probability
            ),
            protocol_id=request.protocol_id,
        )

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================================
# Existing Experiment API
# ============================================================================

@app.post("/api/experiment")
def run_experiment(
    request: ExperimentRequest,
):
    """
    Original experiment endpoint.
    Kept for compatibility with the earlier prototype.
    """

    try:

        result = run_attack_experiment(
            message_bit=request.message_bit,
            basis=request.basis.upper(),
            shots=request.shots,
            attack=request.attack.upper(),
            threshold=request.threshold,
            seed=request.seed,
            noise=request.noise.upper(),
            noise_probability=(
                request.noise_probability
            ),
        )

        normal = result[
            "normal_with_noise"
        ]

        attack = result[
            "attack_with_noise"
        ]

        normal_detection = (
            normal["detection"]
        )

        attack_detection = (
            attack["detection"]
        )

        return {
            "configuration": {
                "message_bit": (
                    request.message_bit
                ),
                "basis": (
                    request.basis.upper()
                ),
                "shots": (
                    request.shots
                ),
                "attack": (
                    request.attack.upper()
                ),
                "noise": (
                    request.noise.upper()
                ),
                "noise_probability": (
                    request.noise_probability
                ),
                "threshold": (
                    request.threshold
                ),
            },

            "normal": {
                "observed_probabilities": (
                    normal[
                        "observed_probabilities"
                    ]
                ),
                "tvd": (
                    normal_detection[
                        "total_variation_distance"
                    ]
                ),
                "status": (
                    normal_detection[
                        "status"
                    ]
                ),
            },

            "attack": {
                "attack_type": (
                    request.attack.upper()
                ),
                "observed_probabilities": (
                    attack[
                        "observed_probabilities"
                    ]
                ),
                "tvd": (
                    attack_detection[
                        "total_variation_distance"
                    ]
                ),
                "status": (
                    attack_detection[
                        "status"
                    ]
                ),
            },

            "security_evidence": {
                "normal_status": (
                    normal_detection[
                        "status"
                    ]
                ),
                "attack_status": (
                    attack_detection[
                        "status"
                    ]
                ),
                "threshold": (
                    request.threshold
                ),
                "interpretation": (
                    "An anomalous result indicates "
                    "statistical deviation from "
                    "expected behaviour and does "
                    "not automatically prove a "
                    "specific attack."
                ),
            },
        }

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
