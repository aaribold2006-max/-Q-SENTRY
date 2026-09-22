from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SignerProfile:
    """
    Represents a signer using Q-SENTRY's prototype
    signature-generation workflow.
    """

    signer_id: str
    display_name: str
    protocol_id: str

    created_at: str = field(
        default_factory=utc_now
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class DocumentRecord:
    """
    Represents a document stored by Q-SENTRY.
    """

    document_id: str
    template_id: str
    filename: str
    signer_id: str

    qds_package_id: str | None = None

    created_at: str = field(
        default_factory=utc_now
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class AttackScenarioRecord:
    """
    Represents a saved attack/modification scenario.
    """

    scenario_id: str
    scenario_type: str

    original_document_id: str | None = None
    original_package_id: str | None = None

    created_at: str = field(
        default_factory=utc_now
    )

    status: str = "CREATED"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class SimulationRecord:
    """
    Represents a saved Q-SENTRY simulation run.
    """

    simulation_id: str
    scenario: str

    protocol_id: str | None = None

    created_at: str = field(
        default_factory=utc_now
    )

    result: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )