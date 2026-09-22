from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.qds.document_binding import (
    create_document_binding,
)
from app.qds.qds_package import (
    QDSVerificationPackage,
)
from app.qds.storage import (
    load_document,
    save_document,
)


DOCUMENT_TEMPLATES: dict[str, dict[str, str]] = {
    "achievement_certificate": {
        "name": "Achievement Certificate",
        "description": (
            "A fictional sports or achievement certificate."
        ),
    },
    "academic_certificate": {
        "name": "Academic Certificate",
        "description": (
            "A fictional academic achievement certificate."
        ),
    },
    "employment_certificate": {
        "name": "Employment Certificate",
        "description": (
            "A fictional employment or experience certificate."
        ),
    },
    "official_agreement": {
        "name": "Official Agreement",
        "description": (
            "A fictional official agreement document."
        ),
    },
    "authorization_letter": {
        "name": "Authorization Letter",
        "description": (
            "A fictional authorization letter."
        ),
    },
}


def list_document_templates() -> list[dict[str, str]]:
    return [
        {
            "template_id": template_id,
            "name": details["name"],
            "description": details["description"],
        }
        for template_id, details
        in DOCUMENT_TEMPLATES.items()
    ]


def get_document_template(
    template_id: str,
) -> dict[str, str]:

    template_id = template_id.strip()

    if template_id not in DOCUMENT_TEMPLATES:
        raise KeyError(
            f"Unknown document template: {template_id}"
        )

    return {
        "template_id": template_id,
        **DOCUMENT_TEMPLATES[template_id],
    }


def _escape_html(
    value: str,
) -> str:

    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }

    for old, new in replacements.items():
        value = value.replace(
            old,
            new,
        )

    return value


def _build_document_html(
    template_id: str,
    signer_id: str,
    signature_text: str,
) -> str:

    template = get_document_template(
        template_id
    )

    title = _escape_html(
        template["name"]
    )

    signer = _escape_html(
        signer_id
    )

    signature = _escape_html(
        signature_text
    )

    generated_at = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    if template_id == "achievement_certificate":

        body = f"""
        <h1>Certificate of Achievement</h1>
        <p>This is to certify that</p>
        <h2>{signer}</h2>
        <p>has successfully achieved the stated accomplishment.</p>
        <p class="placeholder">
            Fictional demonstration document for Q-SENTRY.
        </p>
        """

    elif template_id == "academic_certificate":

        body = f"""
        <h1>Academic Achievement Certificate</h1>
        <p>This document certifies that</p>
        <h2>{signer}</h2>
        <p>has successfully completed the specified academic achievement.</p>
        <p class="placeholder">
            Fictional demonstration document for Q-SENTRY.
        </p>
        """

    elif template_id == "employment_certificate":

        body = f"""
        <h1>Employment Certificate</h1>
        <p>This is to certify that</p>
        <h2>{signer}</h2>
        <p>has completed the specified period of service.</p>
        <p class="placeholder">
            Fictional demonstration document for Q-SENTRY.
        </p>
        """

    elif template_id == "official_agreement":

        body = f"""
        <h1>Official Agreement</h1>
        <p>Parties acknowledge this fictional agreement involving</p>
        <h2>{signer}</h2>
        <p>under the terms represented in this demonstration document.</p>
        <p class="placeholder">
            Fictional demonstration document for Q-SENTRY.
        </p>
        """

    elif template_id == "authorization_letter":

        body = f"""
        <h1>Authorization Letter</h1>
        <p>This fictional document authorizes</p>
        <h2>{signer}</h2>
        <p>for the purpose represented in this demonstration.</p>
        <p class="placeholder">
            Fictional demonstration document for Q-SENTRY.
        </p>
        """

    else:
        raise KeyError(
            f"Unsupported document template: {template_id}"
        )

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>{title}</title>

    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            background: #f4f7fb;
            margin: 0;
            padding: 50px;
            color: #172033;
        }}

        .document {{
            max-width: 850px;
            margin: auto;
            background: white;
            padding: 60px;
            border: 1px solid #dbe3ef;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }}

        h1 {{
            text-align: center;
            margin-bottom: 45px;
        }}

        h2 {{
            text-align: center;
            margin: 25px 0;
        }}

        p {{
            font-size: 17px;
            line-height: 1.7;
            text-align: center;
        }}

        .placeholder {{
            margin-top: 45px;
            font-size: 12px;
            color: #64748b;
        }}

        .signature {{
            margin-top: 55px;
            text-align: center;
        }}

        .signature-line {{
            margin: 18px auto 8px;
            width: 240px;
            border-bottom: 1px solid #172033;
        }}

        .signature-value {{
            font-family: "Brush Script MT", cursive;
            font-size: 30px;
            font-weight: bold;
        }}

        .metadata {{
            margin-top: 45px;
            padding-top: 15px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 12px;
            color: #64748b;
        }}
    </style>
</head>

<body>

<div class="document">

    {body}

    <div class="signature">
        <div>Authorized Signature</div>

        <div class="signature-line"></div>

        <div class="signature-value">
            {signature}
        </div>

        <div>
            Signer: {signer}
        </div>
    </div>

    <div class="metadata">
        Generated: {generated_at}
    </div>

</div>

</body>
</html>
"""


def create_document(
    template_id: str,
    signer_id: str,
    signature_text: str,
    document_name: str | None = None,
) -> dict[str, Any]:

    template = get_document_template(
        template_id
    )

    signer_id = signer_id.strip()
    signature_text = signature_text.strip()

    if not signer_id:
        raise ValueError(
            "signer_id cannot be empty."
        )

    if not signature_text:
        raise ValueError(
            "signature_text cannot be empty."
        )

    if document_name is None:
        document_name = (
            f"{signer_id} - "
            f"{template['name']}"
        )

    document_name = document_name.strip()

    if not document_name:
        raise ValueError(
            "document_name cannot be empty."
        )

    document_id = (
        f"DOC-{uuid4().hex[:10].upper()}"
    )

    html = _build_document_html(
        template_id=template_id,
        signer_id=signer_id,
        signature_text=signature_text,
    )

    document_bytes = html.encode(
        "utf-8"
    )

    return {
        "document_id": document_id,
        "document_name": document_name,
        "template_id": template_id,
        "template_name": template["name"],
        "signer_id": signer_id,
        "signature_text": signature_text,
        "filename": f"{document_id}.html",
        "document_bytes": document_bytes,
    }


def save_created_document(
    document: dict[str, Any],
):
    return save_document(
        document_id=document["document_id"],
        document_bytes=document["document_bytes"],
        filename=document["filename"],
        document_name=document.get(
            "document_name"
        ),
    )


def create_qds_binding_for_document(
    document: dict[str, Any],
) -> dict[str, Any]:

    return create_document_binding(
        document_id=document["document_id"],
        document_bytes=document["document_bytes"],
    )


def create_signed_qds_package(
    document: dict[str, Any],
    protocol_id: str,
    signer_id: str,
    signature_data: dict[str, Any],
    verification_data: dict[str, Any],
) -> QDSVerificationPackage:

    binding = create_qds_binding_for_document(
        document
    )

    package = QDSVerificationPackage(
        package_id=(
            f"QDS-{uuid4().hex[:10].upper()}"
        ),
        protocol_id=protocol_id,
        signer_id=signer_id,
        document_id=document["document_id"],
        document_binding=binding,
        signature_data=signature_data,
        verification_data=verification_data,
        package_name=(
            f"{document.get('document_name', 'Document')} "
            f"QDS"
        ),
        metadata={
            "template_id": document[
                "template_id"
            ],
            "template_name": document[
                "template_name"
            ],
        },
    )

    return package


def load_saved_document(
    document_id: str,
) -> bytes:

    return load_document(
        document_id
    )