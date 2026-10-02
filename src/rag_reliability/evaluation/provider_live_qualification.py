"""Phase 5 live semantic-provider qualification receipt."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.provider_live_probe_capture import (
    Phase5LiveProviderProbeAttemptV1,
)
from rag_reliability.evaluation.semantic_provider_profile_freeze import (
    Phase5SemanticProviderProfileFreezeReceipt,
)

_PROVIDER_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_semantic_provider_profile_freeze_v1.json"
)
_CONTEXT_A_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_live_provider_context_a_attempt_v1.json"
)
_CONTEXT_B_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_live_provider_context_b_attempt_v1.json"
)
_REFUSAL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_live_provider_refusal_attempt_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_semantic_provider_live_qualification_v1.json"
)

_PROVIDER_FREEZE_SHA256: Sha256 = (
    "2467146329874ddc02ba6740da90f52a0b53b5d945979fa3e7270c64021d445e"
)
_CONTEXT_A_SHA256: Sha256 = (
    "f91df515b83a5b212cf1402d9a63482603feaa57e51cf039c0a1ec27942aceb4"
)
_CONTEXT_B_SHA256: Sha256 = (
    "71a6a516fbce97664c366f5a127db93e5e2889121238df84f8f09833b3ec36f1"
)
_REFUSAL_SHA256: Sha256 = (
    "5215da311d5566db0d096c3ed066f3b72ff5457cef3a572dd874600958473216"
)


class Phase5SemanticProviderLiveQualificationV1(ContractModel):
    """Bind the three required passing live probes to the frozen provider."""

    receipt_version: Literal[
        "phase5-semantic-provider-live-qualification-v1"
    ] = "phase5-semantic-provider-live-qualification-v1"

    provider_profile_freeze_sha256: Sha256 = _PROVIDER_FREEZE_SHA256

    context_a_attempt_sha256: Sha256 = _CONTEXT_A_SHA256
    context_b_attempt_sha256: Sha256 = _CONTEXT_B_SHA256
    refusal_attempt_sha256: Sha256 = _REFUSAL_SHA256

    binding_configuration_id: Sha256
    provider_configuration_id: Sha256

    required_probe_count: Literal[3] = 3
    passing_probe_count: Literal[3] = 3

    context_a_passed: Literal[True] = True
    context_b_passed: Literal[True] = True
    refusal_passed: Literal[True] = True

    generation_is_context_sensitive: Literal[True] = True
    semantic_refusal_observed: Literal[True] = True

    automatic_retry_count_per_probe: Literal[0] = 0

    credential_value_persisted: Literal[False] = False
    raw_request_payload_persisted: Literal[False] = False
    raw_provider_payload_persisted: Literal[False] = False
    raw_provider_error_body_persisted: Literal[False] = False

    live_qualification_satisfied: Literal[True] = True

    baseline_readiness_refresh_required: Literal[True] = True
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.passing_probe_count != self.required_probe_count:
            raise ValueError("all required live probes must pass")

        if not (
            self.context_a_passed
            and self.context_b_passed
            and self.refusal_passed
        ):
            raise ValueError("required live probe pass state drifted")

        if not self.live_qualification_satisfied:
            raise ValueError("qualification receipt must record satisfied state")

        if not self.baseline_readiness_refresh_required:
            raise ValueError("provider qualification must advance to readiness refresh")

        if (
            self.baseline_execution_authorized
            or self.b0_executed
            or self.post_reject_confirmation_inspected
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("provider qualification overclaims downstream state")

        return self


def _verified_bytes(path: Path, expected_sha256: str) -> bytes:
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()

    if digest != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"
    observed = sidecar.read_text(encoding="utf-8").strip()

    if observed != expected:
        raise ValueError(f"frozen artifact sidecar mismatch: {path}")

    return content


def _load_probe(
    repo_root: Path,
    path: Path,
    expected_sha256: str,
    expected_probe_id: Literal["context-a", "context-b", "refusal"],
) -> Phase5LiveProviderProbeAttemptV1:
    receipt = Phase5LiveProviderProbeAttemptV1.model_validate_json(
        _verified_bytes(
            repo_root / path,
            expected_sha256,
        )
    )

    if receipt.probe_id != expected_probe_id:
        raise ValueError(f"live probe identity drifted: {expected_probe_id}")

    if receipt.outcome != "PASS" or not receipt.probe_passed:
        raise ValueError(f"required live probe did not pass: {expected_probe_id}")

    if receipt.automatic_retry_count != 0:
        raise ValueError(f"live probe used automatic retry: {expected_probe_id}")

    return receipt


def materialize_phase5_semantic_provider_live_qualification(
    repo_root: Path,
) -> tuple[
    Phase5SemanticProviderLiveQualificationV1,
    str,
]:
    provider_freeze = (
        Phase5SemanticProviderProfileFreezeReceipt.model_validate_json(
            _verified_bytes(
                repo_root / _PROVIDER_FREEZE_PATH,
                _PROVIDER_FREEZE_SHA256,
            )
        )
    )

    context_a = _load_probe(
        repo_root,
        _CONTEXT_A_PATH,
        _CONTEXT_A_SHA256,
        "context-a",
    )
    context_b = _load_probe(
        repo_root,
        _CONTEXT_B_PATH,
        _CONTEXT_B_SHA256,
        "context-b",
    )
    refusal = _load_probe(
        repo_root,
        _REFUSAL_PATH,
        _REFUSAL_SHA256,
        "refusal",
    )

    if not provider_freeze.profile_frozen:
        raise ValueError("semantic provider profile is not frozen")

    receipts = (context_a, context_b, refusal)

    binding_ids = {
        receipt.binding_configuration_id
        for receipt in receipts
    }
    provider_ids = {
        receipt.provider_configuration_id
        for receipt in receipts
    }

    if binding_ids != {provider_freeze.binding_configuration_id}:
        raise ValueError("live probes do not match frozen provider binding")

    if provider_ids != {provider_freeze.provider_configuration_id}:
        raise ValueError("live probes do not match frozen provider configuration")

    receipt = Phase5SemanticProviderLiveQualificationV1(
        binding_configuration_id=provider_freeze.binding_configuration_id,
        provider_configuration_id=provider_freeze.provider_configuration_id,
    )

    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        receipt,
    )

    return receipt, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    receipt, digest = (
        materialize_phase5_semantic_provider_live_qualification(
            repo_root
        )
    )

    print(
        "PHASE5_SEMANTIC_PROVIDER_LIVE_QUALIFICATION_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_REQUIRED_PROBES="
        f"{receipt.passing_probe_count}/{receipt.required_probe_count}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_LIVE_QUALIFICATION_SATISFIED="
        f"{str(receipt.live_qualification_satisfied).lower()}"
    )
    print(
        "PHASE5_BASELINE_READINESS_REFRESH_REQUIRED="
        f"{str(receipt.baseline_readiness_refresh_required).lower()}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(receipt.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_B0_EXECUTED="
        f"{str(receipt.b0_executed).lower()}"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED="
        f"{str(receipt.held_out_outcomes_exposed).lower()}"
    )


if __name__ == "__main__":
    main()
