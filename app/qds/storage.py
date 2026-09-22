from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.qds.qds_package import QDSVerificationPackage


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

QDS_PACKAGE_DIR = DATA_DIR / "qds_packages"
DOCUMENT_DIR = DATA_DIR / "documents"
DOCUMENT_METADATA_DIR = DATA_DIR / "document_metadata"
ATTACK_DIR = DATA_DIR / "attack_scenarios"


def initialize_storage() -> None:
    QDS_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    ATTACK_DIR.mkdir(parents=True, exist_ok=True)


def _safe_identifier(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Identifier must be a string.")

    value = value.strip()

    if not value:
        raise ValueError("Identifier cannot be empty.")

    return re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        value,
    )


def _save_json(
    path: Path,
    data: dict[str, Any],
) -> Path:
    initialize_storage()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return path


def _load_json(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Stored data not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Stored JSON must contain an object."
        )

    return data


# ---------------------------------------------------------------------------
# QDS packages
# ---------------------------------------------------------------------------

def save_qds_package(
    package: QDSVerificationPackage,
) -> Path:
    package.validate()

    package_id = _safe_identifier(
        package.package_id
    )

    path = (
        QDS_PACKAGE_DIR
        / f"{package_id}.json"
    )

    return _save_json(
        path,
        package.to_dict(),
    )


def load_qds_package(
    package_id: str,
) -> QDSVerificationPackage:
    safe_id = _safe_identifier(
        package_id
    )

    path = (
        QDS_PACKAGE_DIR
        / f"{safe_id}.json"
    )

    package = (
        QDSVerificationPackage.from_dict(
            _load_json(path)
        )
    )

    package.validate()

    return package


def rename_qds_package(
    package_id: str,
    new_name: str,
) -> QDSVerificationPackage:
    package = load_qds_package(
        package_id
    )

    package.rename(
        new_name
    )

    save_qds_package(
        package
    )

    return package


def delete_qds_package(
    package_id: str,
) -> None:
    safe_id = _safe_identifier(
        package_id
    )

    path = (
        QDS_PACKAGE_DIR
        / f"{safe_id}.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"QDS package not found: {package_id}"
        )

    path.unlink()


def list_qds_packages() -> list[dict[str, Any]]:
    initialize_storage()

    packages: list[dict[str, Any]] = []

    for path in sorted(
        QDS_PACKAGE_DIR.glob("*.json")
    ):
        try:
            data = _load_json(path)

            packages.append(
                {
                    "package_id": data.get(
                        "package_id"
                    ),
                    "package_name": data.get(
                        "package_name",
                        "Unnamed QDS Package",
                    ),
                    "protocol_id": data.get(
                        "protocol_id"
                    ),
                    "signer_id": data.get(
                        "signer_id"
                    ),
                    "document_id": data.get(
                        "document_id"
                    ),
                    "created_at": data.get(
                        "created_at"
                    ),
                }
            )

        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
        ):
            continue

    return packages


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

def _document_metadata_path(
    document_id: str,
) -> Path:
    safe_id = _safe_identifier(
        document_id
    )

    return (
        DOCUMENT_METADATA_DIR
        / f"{safe_id}.json"
    )


def save_document(
    document_id: str,
    document_bytes: bytes,
    filename: str,
    document_name: str | None = None,
) -> Path:
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

    safe_id = _safe_identifier(
        document_id
    )

    original_filename = Path(
        filename
    ).name

    suffix = Path(
        original_filename
    ).suffix.lower()

    if not suffix:
        raise ValueError(
            "Document filename must have an extension."
        )

    if document_name is None:
        document_name = Path(
            original_filename
        ).stem

    document_name = document_name.strip()

    if not document_name:
        raise ValueError(
            "document_name cannot be empty."
        )

    if len(document_name) > 120:
        raise ValueError(
            "document_name cannot exceed 120 characters."
        )

    path = (
        DOCUMENT_DIR
        / f"{safe_id}{suffix}"
    )

    initialize_storage()

    path.write_bytes(
        document_bytes
    )

    metadata = {
        "document_id": document_id,
        "document_name": document_name,
        "filename": path.name,
        "created_at": None,
    }

    _save_json(
        _document_metadata_path(document_id),
        metadata,
    )

    return path


def load_document(
    document_id: str,
) -> bytes:
    return get_document_path(
        document_id
    ).read_bytes()


def get_document_path(
    document_id: str,
) -> Path:
    safe_id = _safe_identifier(
        document_id
    )

    initialize_storage()

    matches = [
        path
        for path in DOCUMENT_DIR.glob(
            f"{safe_id}.*"
        )
        if path.is_file()
    ]

    if not matches:
        raise FileNotFoundError(
            f"No saved document found for ID: "
            f"{document_id}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"Multiple documents found for ID: "
            f"{document_id}"
        )

    return matches[0]


def get_document_metadata(
    document_id: str,
) -> dict[str, Any]:
    path = _document_metadata_path(
        document_id
    )

    if not path.exists():
        document_path = get_document_path(
            document_id
        )

        return {
            "document_id": document_id,
            "document_name": document_path.stem,
            "filename": document_path.name,
        }

    return _load_json(path)


def rename_document(
    document_id: str,
    new_name: str,
) -> dict[str, Any]:
    new_name = new_name.strip()

    if not new_name:
        raise ValueError(
            "Document name cannot be empty."
        )

    if len(new_name) > 120:
        raise ValueError(
            "Document name cannot exceed 120 characters."
        )

    metadata = get_document_metadata(
        document_id
    )

    metadata["document_name"] = new_name

    _save_json(
        _document_metadata_path(document_id),
        metadata,
    )

    return metadata


def delete_document(
    document_id: str,
) -> None:
    document_path = get_document_path(
        document_id
    )

    metadata_path = _document_metadata_path(
        document_id
    )

    document_path.unlink()

    if metadata_path.exists():
        metadata_path.unlink()


def list_documents() -> list[dict[str, str]]:
    initialize_storage()

    documents: list[dict[str, str]] = []

    for path in sorted(
        DOCUMENT_DIR.iterdir()
    ):
        if not path.is_file():
            continue

        document_id = path.stem

        try:
            metadata = get_document_metadata(
                document_id
            )

            documents.append(
                {
                    "document_id": document_id,
                    "document_name": str(
                        metadata.get(
                            "document_name",
                            document_id,
                        )
                    ),
                    "filename": path.name,
                    "path": str(path),
                }
            )

        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
        ):
            continue

    return documents


# ---------------------------------------------------------------------------
# Attack scenarios
# ---------------------------------------------------------------------------

def save_attack_scenario(
    scenario_id: str,
    scenario: dict[str, Any],
) -> Path:
    safe_id = _safe_identifier(
        scenario_id
    )

    path = (
        ATTACK_DIR
        / f"{safe_id}.json"
    )

    return _save_json(
        path,
        scenario,
    )


def load_attack_scenario(
    scenario_id: str,
) -> dict[str, Any]:
    safe_id = _safe_identifier(
        scenario_id
    )

    path = (
        ATTACK_DIR
        / f"{safe_id}.json"
    )

    return _load_json(path)


def list_attack_scenarios() -> list[dict[str, Any]]:
    initialize_storage()

    scenarios: list[dict[str, Any]] = []

    for path in sorted(
        ATTACK_DIR.glob("*.json")
    ):
        try:
            scenarios.append(
                {
                    "scenario_id": path.stem,
                    "scenario": _load_json(path),
                    "path": str(path),
                }
            )

        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
        ):
            continue

    return scenarios


initialize_storage()