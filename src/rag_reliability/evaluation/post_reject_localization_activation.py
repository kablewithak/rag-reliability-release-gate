"""Activate Phase 5 DEVELOPMENT failure localization after fresh-suite freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.post_reject_confirmation_freeze import (
    Phase5PostRejectConfirmationFreezeReceipt,
)

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_investigation_protocol_v1.json"
)
_PROTOCOL_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_investigation_protocol_freeze_v1.json"
)
_CONFIRMATION_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_confirmation_cases_v1.json"
)
_CONFIRMATION_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_confirmation_freeze_v1.json"
)
_DEVELOPMENT_REJECTION_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_development_confirmation_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_localization_activation_v1.json"
)

_PROTOCOL_SHA256: Literal["4723c854f32d114958633203d9db0b9e629a38aea8242cc958f25f1d5eddbfed"] = (
    "4723c854f32d114958633203d9db0b9e629a38aea8242cc958f25f1d5eddbfed"
)

_PROTOCOL_FREEZE_SHA256: Literal[
    "76035d9dd68c7f02198fcfba1481ab9bb705a116a03ec57588d5772fb7811288"
] = "76035d9dd68c7f02198fcfba1481ab9bb705a116a03ec57588d5772fb7811288"

_CONFIRMATION_SHA256: Literal[
    "fde5b7005d9fa52dffff488b26224ebf90b7fcaaa6b443a55e136e01f397053c"
] = "fde5b7005d9fa52dffff488b26224ebf90b7fcaaa6b443a55e136e01f397053c"

_CONFIRMATION_FREEZE_SHA256: Literal[
    "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"
] = "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"

_DEVELOPMENT_REJECTION_SHA256: Literal[
    "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
] = "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"


class Phase5PostRejectLocalizationActivationV1(ContractModel):
    """Irreversible evidence-role transition before opening failed cases."""

    receipt_version: Literal["phase5-post-reject-localization-activation-v1"] = (
        "phase5-post-reject-localization-activation-v1"
    )

    post_reject_protocol_sha256: Sha256 = _PROTOCOL_SHA256
    post_reject_protocol_freeze_sha256: Sha256 = _PROTOCOL_FREEZE_SHA256

    fresh_confirmation_suite_sha256: Sha256 = _CONFIRMATION_SHA256
    fresh_confirmation_freeze_sha256: Sha256 = _CONFIRMATION_FREEZE_SHA256

    development_rejection_sha256: Sha256 = _DEVELOPMENT_REJECTION_SHA256

    fresh_confirmation_materialized: Literal[True] = True
    fresh_confirmation_frozen: Literal[True] = True
    localization_activation_condition_satisfied: Literal[True] = True

    failure_localization_started: Literal[True] = True
    development_spent_for_future_confirmation: Literal[True] = True

    failure_specific_development_evidence_opened: Literal[False] = False
    failure_specific_case_ids_opened: Literal[False] = False
    failure_specific_gold_opened: Literal[False] = False

    development_role_after_activation: Literal["diagnostic_only_spent_for_future_confirmation"] = (
        "diagnostic_only_spent_for_future_confirmation"
    )

    fresh_confirmation_role: Literal[
        "independent_confirmation_for_next_semantic_runtime_candidate"
    ] = "independent_confirmation_for_next_semantic_runtime_candidate"

    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    candidate_retuning_authorized: Literal[False] = False
    parameter_sweep_authorized: Literal[False] = False
    new_candidate_execution_authorized: Literal[False] = False
    provider_invocation_authorized: Literal[False] = False

    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_transition(self) -> Self:
        if not (
            self.fresh_confirmation_materialized
            and self.fresh_confirmation_frozen
            and self.localization_activation_condition_satisfied
        ):
            raise ValueError("localization activation precondition is incomplete")

        if not (
            self.failure_localization_started and self.development_spent_for_future_confirmation
        ):
            raise ValueError("DEVELOPMENT role transition is incomplete")

        if (
            self.failure_specific_development_evidence_opened
            or self.failure_specific_case_ids_opened
            or self.failure_specific_gold_opened
        ):
            raise ValueError("activation receipt must precede failure inspection")

        if self.held_out_case_content_read or self.held_out_outcomes_exposed:
            raise ValueError("HELD_OUT must remain sealed")

        if (
            self.candidate_retuning_authorized
            or self.parameter_sweep_authorized
            or self.new_candidate_execution_authorized
            or self.provider_invocation_authorized
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("activation receipt cannot authorize downstream work")

        return self


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_exact_artifact(
    repo_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> None:
    path = repo_root / relative_path

    if _sha256(path) != expected_sha256:
        raise ValueError(f"artifact hash mismatch: {relative_path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise ValueError(f"artifact sidecar mismatch: {relative_path}")


def materialize_phase5_post_reject_localization_activation(
    repo_root: Path,
) -> tuple[Phase5PostRejectLocalizationActivationV1, str]:
    """Verify all prerequisites, then record the DEVELOPMENT role transition."""

    _verify_exact_artifact(
        repo_root,
        _PROTOCOL_PATH,
        _PROTOCOL_SHA256,
    )
    _verify_exact_artifact(
        repo_root,
        _PROTOCOL_FREEZE_PATH,
        _PROTOCOL_FREEZE_SHA256,
    )
    _verify_exact_artifact(
        repo_root,
        _CONFIRMATION_PATH,
        _CONFIRMATION_SHA256,
    )
    _verify_exact_artifact(
        repo_root,
        _CONFIRMATION_FREEZE_PATH,
        _CONFIRMATION_FREEZE_SHA256,
    )
    _verify_exact_artifact(
        repo_root,
        _DEVELOPMENT_REJECTION_PATH,
        _DEVELOPMENT_REJECTION_SHA256,
    )

    freeze = Phase5PostRejectConfirmationFreezeReceipt.model_validate_json(
        (repo_root / _CONFIRMATION_FREEZE_PATH).read_bytes()
    )

    if not freeze.failure_localization_activation_condition_satisfied:
        raise ValueError("fresh confirmation freeze does not authorize localization")

    if not freeze.fresh_confirmation_materialized or not freeze.fresh_confirmation_frozen:
        raise ValueError("fresh confirmation custody is incomplete")

    if freeze.failure_localization_started:
        raise ValueError("fresh confirmation freeze unexpectedly started localization")

    receipt = Phase5PostRejectLocalizationActivationV1()

    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        receipt,
    )

    return receipt, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    receipt, digest = materialize_phase5_post_reject_localization_activation(repo_root)

    print(f"PHASE5_LOCALIZATION_ACTIVATION_SHA256={digest}")
    print(
        f"PHASE5_FAILURE_LOCALIZATION_STARTED={str(receipt.failure_localization_started).lower()}"
    )
    print(
        "PHASE5_DEVELOPMENT_SPENT_FOR_FUTURE_CONFIRMATION="
        f"{str(receipt.development_spent_for_future_confirmation).lower()}"
    )
    print(
        "PHASE5_FAILURE_SPECIFIC_DEVELOPMENT_EVIDENCE_OPENED="
        f"{str(receipt.failure_specific_development_evidence_opened).lower()}"
    )
    print(f"PHASE5_HELD_OUT_EXPOSED={str(receipt.held_out_outcomes_exposed).lower()}")
    print("PHASE5_CANDIDATE_RETUNING_AUTHORIZED=false")
    print("PHASE5_NEW_CANDIDATE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")


if __name__ == "__main__":
    main()
