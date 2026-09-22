from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class QDSVerificationPackage:
    """
    Stores protocol-specific QDS information.

    package_id is the permanent internal identifier.
    package_name is the user-friendly editable name.
    """

    package_id: str
    protocol_id: str
    signer_id: str

    document_id: str | None = None

    package_name: str = "Unnamed QDS Package"

    document_binding: dict[str, Any] = field(
        default_factory=dict
    )

    signature_data: dict[str, Any] = field(
        default_factory=dict
    )

    verification_data: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    version: str = "1.0"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def is_document_bound(self) -> bool:
        return (
            self.document_id is not None
            and bool(self.document_binding)
        )

    def rename(
        self,
        new_name: str,
    ) -> None:
        """
        Change only the user-facing package name.
        The permanent package ID remains unchanged.
        """

        if not isinstance(new_name, str):
            raise TypeError(
                "new_name must be a string."
            )

        new_name = new_name.strip()

        if not new_name:
            raise ValueError(
                "Package name cannot be empty."
            )

        if len(new_name) > 120:
            raise ValueError(
                "Package name cannot exceed 120 characters."
            )

        self.package_name = new_name

    def bind_to_document(
        self,
        document_id: str,
        document_binding: dict[str, Any],
    ) -> None:

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        if not isinstance(
            document_binding,
            dict,
        ):
            raise TypeError(
                "document_binding must be a dictionary."
            )

        if not document_binding:
            raise ValueError(
                "document_binding cannot be empty."
            )

        self.document_id = document_id.strip()
        self.document_binding = dict(
            document_binding
        )

        self.metadata[
            "stage"
        ] = "DOCUMENT_BOUND"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "QDSVerificationPackage":

        required_fields = (
            "package_id",
            "protocol_id",
            "signer_id",
            "signature_data",
            "verification_data",
        )

        missing = [
            field_name
            for field_name in required_fields
            if field_name not in data
        ]

        if missing:
            raise ValueError(
                "Missing required QDS package fields: "
                + ", ".join(missing)
            )

        return cls(
            package_id=str(
                data["package_id"]
            ),
            protocol_id=str(
                data["protocol_id"]
            ),
            signer_id=str(
                data["signer_id"]
            ),
            document_id=(
                str(data["document_id"])
                if data.get("document_id")
                is not None
                else None
            ),
            package_name=str(
                data.get(
                    "package_name",
                    "Unnamed QDS Package",
                )
            ),
            document_binding=dict(
                data.get(
                    "document_binding",
                    {},
                )
            ),
            signature_data=dict(
                data.get(
                    "signature_data",
                    {},
                )
            ),
            verification_data=dict(
                data.get(
                    "verification_data",
                    {},
                )
            ),
            created_at=str(
                data.get(
                    "created_at",
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                )
            ),
            version=str(
                data.get(
                    "version",
                    "1.0",
                )
            ),
            metadata=dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
        )

    def validate(self) -> None:

        if not self.package_id.strip():
            raise ValueError(
                "package_id cannot be empty."
            )

        if not self.protocol_id.strip():
            raise ValueError(
                "protocol_id cannot be empty."
            )

        if not self.signer_id.strip():
            raise ValueError(
                "signer_id cannot be empty."
            )

        if not self.package_name.strip():
            raise ValueError(
                "package_name cannot be empty."
            )

        if not isinstance(
            self.signature_data,
            dict,
        ):
            raise TypeError(
                "signature_data must be a dictionary."
            )

        if not isinstance(
            self.verification_data,
            dict,
        ):
            raise TypeError(
                "verification_data must be a dictionary."
            )

        if self.document_id is not None:
            if not self.document_id.strip():
                raise ValueError(
                    "document_id cannot be empty."
                )

            if not self.document_binding:
                raise ValueError(
                    "A document-bound package must "
                    "contain document_binding."
                )

    def add_protocol_data(
        self,
        protocol_data: dict[str, Any],
    ) -> None:

        if not isinstance(
            protocol_data,
            dict,
        ):
            raise TypeError(
                "protocol_data must be a dictionary."
            )

        self.metadata[
            "protocol_data"
        ] = dict(protocol_data)

    def get_protocol_data(
        self,
    ) -> dict[str, Any]:

        data = self.metadata.get(
            "protocol_data",
            {},
        )

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Stored protocol_data is invalid."
            )

        return dict(data)