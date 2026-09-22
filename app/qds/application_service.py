from __future__ import annotations

from typing import Any

from app.qds.attack_lab import AttackLab
from app.qds.document_manager import (
    create_document,
    list_document_templates,
)
from app.qds.protocol_base import QDSProtocol
from app.qds.protocol_registry import ProtocolRegistry
from app.qds.qds_package import QDSVerificationPackage
from app.qds.signature_manager import SignatureManager
from app.qds.simulation_manager import SimulationManager
from app.qds.verification_manager import VerificationManager

from app.qds.storage import (
    delete_document,
    delete_qds_package,
    list_documents,
    list_qds_packages,
    load_document,
    load_qds_package,
    rename_document,
    rename_qds_package,
    save_document,
    save_qds_package,
)


class QSentryApplicationService:

    def __init__(self) -> None:

        self.protocol_registry = ProtocolRegistry()

        self.signature_manager = (
            SignatureManager(
                self.protocol_registry
            )
        )

        self.verification_manager = (
            VerificationManager(
                self.protocol_registry
            )
        )

        self.attack_lab = AttackLab()

        self.simulation_manager = (
            SimulationManager()
        )

    # ------------------------------------------------------------------
    # Protocols
    # ------------------------------------------------------------------

    def register_protocol(
        self,
        protocol: QDSProtocol,
    ) -> None:

        self.protocol_registry.register(
            protocol
        )

    def list_protocols(
        self,
    ) -> list[dict[str, str]]:

        return (
            self.protocol_registry
            .list_protocols()
        )

    # ------------------------------------------------------------------
    # Document templates
    # ------------------------------------------------------------------

    def list_document_templates(
        self,
    ) -> list[dict[str, str]]:

        return list_document_templates()

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def create_demo_document(
        self,
        template_id: str,
        signer_id: str,
        signature_text: str,
        document_name: str | None = None,
    ) -> dict[str, Any]:

        return create_document(
            template_id=template_id,
            signer_id=signer_id,
            signature_text=signature_text,
            document_name=document_name,
        )

    def save_demo_document(
        self,
        document: dict[str, Any],
    ):

        return save_document(
            document_id=document["document_id"],
            document_bytes=document[
                "document_bytes"
            ],
            filename=document["filename"],
            document_name=document.get(
                "document_name"
            ),
        )

    def load_saved_document(
        self,
        document_id: str,
    ) -> bytes:

        return load_document(
            document_id
        )

    def list_saved_documents(
        self,
    ) -> list[dict[str, str]]:

        return list_documents()

    def rename_document(
        self,
        document_id: str,
        new_name: str,
    ) -> dict[str, Any]:

        return rename_document(
            document_id=document_id,
            new_name=new_name,
        )

    def delete_document(
        self,
        document_id: str,
    ) -> None:

        # Prevent deleting a document that is still
        # associated with a saved QDS package.
        packages = list_qds_packages()

        for package in packages:

            if (
                package.get("document_id")
                == document_id
            ):
                raise ValueError(
                    "This document is associated "
                    "with a saved QDS package. "
                    "Delete or update the associated "
                    "QDS package first."
                )

        delete_document(
            document_id
        )

    # ------------------------------------------------------------------
    # QDS packages
    # ------------------------------------------------------------------

    def load_qds_package(
        self,
        package_id: str,
    ) -> QDSVerificationPackage:

        return load_qds_package(
            package_id
        )

    def list_saved_qds_packages(
        self,
    ) -> list[dict[str, Any]]:

        return list_qds_packages()

    def save_qds_package(
        self,
        package: QDSVerificationPackage,
    ):

        return save_qds_package(
            package
        )

    def rename_qds_package(
        self,
        package_id: str,
        new_name: str,
    ) -> QDSVerificationPackage:

        return rename_qds_package(
            package_id=package_id,
            new_name=new_name,
        )

    def delete_qds_package(
        self,
        package_id: str,
    ) -> None:

        delete_qds_package(
            package_id
        )

    # ------------------------------------------------------------------
    # QDS creation
    # ------------------------------------------------------------------

    def generate_unbound_qds_package(
        self,
        protocol_id: str,
        signer_id: str,
        package_name: str | None = None,
        **kwargs: Any,
    ) -> QDSVerificationPackage:

        protocol = (
            self.protocol_registry.get(
                protocol_id
            )
        )

        if package_name is None:
            package_name = (
                f"{signer_id.strip()} "
                f"QDS Package"
            )

        package = (
            self.signature_manager
            .create_unbound_package(
                protocol_id=protocol.protocol_id,
                signer_id=signer_id,
                signature_data={},
                verification_data={},
                metadata={
                    "stage": "SIGNER_CREATED",
                    "initialization": kwargs,
                },
            )
        )

        package.rename(
            package_name
        )

        return package

    def sign_document(
        self,
        package: QDSVerificationPackage,
        document_id: str,
        **kwargs: Any,
    ) -> QDSVerificationPackage:

        document_bytes = (
            self.load_saved_document(
                document_id
            )
        )

        updated_package = (
            self.signature_manager
            .sign_document(
                package=package,
                document_id=document_id,
                document_bytes=document_bytes,
                **kwargs,
            )
        )

        self.save_qds_package(
            updated_package
        )

        return updated_package

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def verify_document(
        self,
        package_id: str,
        document_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return (
            self.verification_manager
            .verify_saved_document(
                package_id=package_id,
                document_id=document_id,
                **kwargs,
            )
        )

    def verify_attack_scenario(
        self,
        scenario_id: str,
    ) -> dict[str, Any]:

        return (
            self.verification_manager
            .verify_attack_scenario(
                scenario_id
            )
        )

    # ------------------------------------------------------------------
    # Attack Lab
    # ------------------------------------------------------------------

    def list_attack_scenarios(
        self,
    ) -> list[dict[str, str]]:

        return (
            self.attack_lab
            .list_attack_scenarios()
        )

    def create_document_tampering(
        self,
        package_id: str,
        document_id: str,
        search_text: str,
        replacement_text: str,
    ) -> dict[str, Any]:

        return (
            self.attack_lab
            .create_document_tampering(
                package_id=package_id,
                original_document_id=document_id,
                search_text=search_text,
                replacement_text=replacement_text,
            )
        )

    def create_forgery(
        self,
        package_id: str,
        forged_signature_data: dict[str, Any],
    ) -> dict[str, Any]:

        return (
            self.attack_lab
            .create_forgery(
                package_id=package_id,
                forged_signature_data=(
                    forged_signature_data
                ),
            )
        )

    def create_impersonation(
        self,
        package_id: str,
        impersonated_signer_id: str,
    ) -> dict[str, Any]:

        return (
            self.attack_lab
            .create_impersonation(
                package_id=package_id,
                impersonated_signer_id=(
                    impersonated_signer_id
                ),
            )
        )

    def create_replay(
        self,
        package_id: str,
        replay_context_id: str,
    ) -> dict[str, Any]:

        return self.attack_lab.create_replay(
            package_id=package_id,
            replay_context_id=replay_context_id,
        )

    def create_unauthorized_verification(
        self,
        package_id: str,
        verifier_id: str,
        authorized: bool = False,
    ) -> dict[str, Any]:

        return (
            self.attack_lab
            .create_unauthorized_verification(
                package_id=package_id,
                verifier_id=verifier_id,
                authorized=authorized,
            )
        )

    def create_quantum_channel_manipulation(
        self,
        package_id: str,
        manipulation: str = "PHASE_FLIP",
        probability: float = 0.05,
    ) -> dict[str, Any]:

        return (
            self.attack_lab
            .create_quantum_channel_manipulation(
                package_id=package_id,
                manipulation=manipulation,
                probability=probability,
            )
        )

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def run_simulation(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.simulation_manager.run(
            **kwargs
        )