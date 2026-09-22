from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ALGORITHM = "SHA-256"


def calculate_document_digest(
    document_bytes: bytes,
    algorithm: str = DEFAULT_ALGORITHM,
) -> str:
    """
    Calculate a cryptographic digest of the exact document bytes.

    This provides the prototype's document-integrity binding layer.
    """

    if not isinstance(document_bytes, bytes):
        raise TypeError("document_bytes must be bytes.")

    if not document_bytes:
        raise ValueError("document_bytes cannot be empty.")

    algorithm = algorithm.upper().replace("-", "")

    try:
        digest = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported hash algorithm: {algorithm}"
        ) from exc

    digest.update(document_bytes)

    return digest.hexdigest()


def calculate_file_digest(
    file_path: str | Path,
    algorithm: str = DEFAULT_ALGORITHM,
) -> str:
    """
    Calculate a digest directly from a document file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    document_bytes = path.read_bytes()

    return calculate_document_digest(
        document_bytes=document_bytes,
        algorithm=algorithm,
    )


def create_document_binding(
    document_id: str,
    document_bytes: bytes,
    algorithm: str = DEFAULT_ALGORITHM,
) -> dict[str, Any]:
    """
    Create the document-binding information stored with QDS data.
    """

    if not isinstance(document_id, str):
        raise TypeError("document_id must be a string.")

    document_id = document_id.strip()

    if not document_id:
        raise ValueError(
            "document_id cannot be empty."
        )

    digest = calculate_document_digest(
        document_bytes=document_bytes,
        algorithm=algorithm,
    )

    normalized_algorithm = (
        algorithm.upper()
        .replace("-", "")
    )

    return {
        "document_id": document_id,
        "binding_algorithm": normalized_algorithm,
        "document_digest": digest,
        "document_size_bytes": len(document_bytes),
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def verify_document_binding(
    document_bytes: bytes,
    binding: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare a submitted document against stored binding information.
    """

    if not isinstance(binding, dict):
        raise TypeError(
            "binding must be a dictionary."
        )

    expected_digest = binding.get(
        "document_digest"
    )

    if not expected_digest:
        raise ValueError(
            "Binding does not contain document_digest."
        )

    algorithm = binding.get(
        "binding_algorithm",
        DEFAULT_ALGORITHM,
    )

    observed_digest = calculate_document_digest(
        document_bytes=document_bytes,
        algorithm=algorithm,
    )

    matches = (
        observed_digest.lower()
        == str(expected_digest).lower()
    )

    return {
        "document_id": binding.get(
            "document_id"
        ),
        "binding_algorithm": algorithm,
        "expected_digest": expected_digest,
        "observed_digest": observed_digest,
        "matches": matches,
        "status": (
            "MATCH"
            if matches
            else "MISMATCH"
        ),
    }


def verify_file_binding(
    file_path: str | Path,
    binding: dict[str, Any],
) -> dict[str, Any]:
    """
    Verify a document file against stored binding information.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    return verify_document_binding(
        document_bytes=path.read_bytes(),
        binding=binding,
    )