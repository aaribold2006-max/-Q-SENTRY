from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------

class ProtocolInfo(BaseModel):
    protocol_id: str
    protocol_name: str
    description: str = ""


# ---------------------------------------------------------------------------
# Signature / QDS package
# ---------------------------------------------------------------------------

class QDSSessionRequest(BaseModel):
    protocol_id: str
    signer_id: str


class QDSSignatureResponse(BaseModel):
    package_id: str
    protocol_id: str
    signer_id: str
    document_id: str | None = None
    stage: str = "SIGNER_CREATED"


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class DocumentTemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str


class DocumentCreateRequest(BaseModel):
    template_id: str
    signer_id: str
    signature_text: str


class DocumentInfo(BaseModel):
    document_id: str
    template_id: str
    template_name: str
    signer_id: str
    filename: str


class DocumentCreateResponse(BaseModel):
    status: str
    document: DocumentInfo


class SignDocumentRequest(BaseModel):
    document_id: str


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

class VerificationRequest(BaseModel):
    package_id: str
    document_id: str


class VerificationResponse(BaseModel):
    package_id: str
    protocol_id: str
    signer_id: str
    document_id: str | None = None
    expected_document_id: str | None = None

    document_identity_match: bool

    document_binding: dict[str, Any] = Field(
        default_factory=dict
    )

    protocol_verification: dict[str, Any] = Field(
        default_factory=dict
    )

    security_decision: dict[str, Any] = Field(
        default_factory=dict
    )


# ---------------------------------------------------------------------------
# Attack Lab
# ---------------------------------------------------------------------------

class AttackScenarioInfo(BaseModel):
    scenario_id: str
    name: str
    description: str


class DocumentTamperingRequest(BaseModel):
    package_id: str
    document_id: str

    search_text: str
    replacement_text: str


class ForgeryRequest(BaseModel):
    package_id: str

    forged_signature_data: dict[str, Any]


class ImpersonationRequest(BaseModel):
    package_id: str
    impersonated_signer_id: str


class ReplayRequest(BaseModel):
    package_id: str
    replay_context_id: str


class UnauthorizedVerificationRequest(BaseModel):
    package_id: str
    verifier_id: str
    authorized: bool = False


class ChannelManipulationRequest(BaseModel):
    package_id: str

    manipulation: str = "PHASE_FLIP"

    probability: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
    )


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class SimulationRequest(BaseModel):
    scenario: str = "NORMAL"

    message_bit: int = Field(
        default=0,
        ge=0,
        le=1,
    )

    basis: str = "X"

    shots: int = Field(
        default=1000,
        gt=0,
    )

    attack: str = "Z"

    threshold: float = Field(
        default=0.058,
        ge=0.0,
        le=1.0,
    )

    seed: int = 42

    noise: str = "PHASE_FLIP"

    noise_probability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    protocol_id: str | None = None


# ---------------------------------------------------------------------------
# Generic responses
# ---------------------------------------------------------------------------

class StatusResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str