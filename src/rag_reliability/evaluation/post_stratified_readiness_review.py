"""Phase 5 post-stratified retrieval readiness and causal review."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.evidence_lane_diagnostic import (
    Phase5EvidenceLaneDiagnosticV1,
)
from rag_reliability.evaluation.semantic_provider_profile_freeze import (
    Phase5SemanticProviderProfileFreezeReceipt,
)
from rag_reliability.evaluation.stratified_retrieval_characterization import (
    Phase5StratifiedRetrievalCharacterizationV1,
)

_DIAGNOSTIC_PATH = Path("artifacts") / "development" / "phase5_evidence_lane_diagnostic_v1.json"
_CHARACTERIZATION_PATH = (
    Path("artifacts") / "development" / "phase5_stratified_retrieval_characterization_v1.json"
)
_PROVIDER_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_provider_profile_freeze_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts") / "development" / "phase5_post_stratified_readiness_review_v1.json"
)

_DIAGNOSTIC_SHA256: Sha256 = (
    "bd3aa5893b7447fb91cf586dd2f2568e18fe6915d162bf2f04e43fad2c433b8e"
)
_CHARACTERIZATION_SHA256: Sha256 = (
    "a7287440000c313ba305a08c8ac860605511345c6539d9c3a21df8c6fb7dd1ac"
)
_PROVIDER_FREEZE_SHA256: Sha256 = (
    "2467146329874ddc02ba6740da90f52a0b53b5d945979fa3e7270c64021d445e"
)

_FAILED_CASE_EXPECTATIONS = {
    "phase4-dev-breaking-version-migration": (37, 6, 27, False),
    "phase4-dev-repos-accept-invitation-current": (45, 1, 17, True),
    "phase4-dev-repos-accept-invitation-success": (49, 4, 25, False),
    "phase4-dev-troubleshooting-method-and-rate-limit": (27, 7, 21, False),
}


class PostStratifiedFailureObservationV1(ContractModel):
    case_id: NonEmptyStr
    incumbent_minimum_raw_top_k: int = Field(ge=1)
    best_native_lane_rank: int = Field(ge=1)
    candidate_minimum_raw_top_k: int = Field(ge=1)
    candidate_full_gold_k20: bool


class Phase5PostStratifiedReadinessReviewV1(ContractModel):
    """Evidence-backed decision after the frozen stratified candidate result."""

    review_version: Literal["phase5-post-stratified-readiness-review-v1"] = (
        "phase5-post-stratified-readiness-review-v1"
    )
    diagnostic_sha256: Sha256 = _DIAGNOSTIC_SHA256
    characterization_sha256: Sha256 = _CHARACTERIZATION_SHA256
    provider_profile_freeze_sha256: Sha256 = _PROVIDER_FREEZE_SHA256

    characterization_valid: Literal[True] = True
    characterization_decision: Literal["REJECT"] = "REJECT"
    diagnostic_failed_development_native_lane_recovered_count: Literal[4] = 4
    candidate_failed_development_recovered_count: Literal[1] = 1
    candidate_full_gold_k20_case_count: Literal[32] = 32
    candidate_required_evidence_reference_count: Literal[43] = 43
    candidate_retrieved_required_evidence_at_k20: Literal[40] = 40
    candidate_micro_gold_recall_at_k20: Literal["0.930233"] = "0.930233"

    candidate_nondeterministic_case_count: Literal[0] = 0
    candidate_k20_regression_count: Literal[0] = 0
    candidate_source_filter_regression_count: Literal[0] = 0
    candidate_context_inclusion_regression_count: Literal[0] = 0
    candidate_refusal_or_fallback_regression_count: Literal[0] = 0

    failed_case_observations: tuple[
        PostStratifiedFailureObservationV1,
        PostStratifiedFailureObservationV1,
        PostStratifiedFailureObservationV1,
        PostStratifiedFailureObservationV1,
    ]

    causal_finding: Literal[
        "native_lane_recoverability_did_not_translate_to_sufficient_merged_rank_gain_under_equal_weight_rrf"
    ] = (
        "native_lane_recoverability_did_not_translate_to_sufficient_merged_rank_gain_under_equal_weight_rrf"
    )
    causal_interpretation: Literal[
        "the_diagnostic_established_within_lane_signal_but_not_that_equal_weight_fusion_would_cross_the_runtime_top20_boundary"
    ] = (
        "the_diagnostic_established_within_lane_signal_but_not_that_equal_weight_fusion_would_cross_the_runtime_top20_boundary"
    )

    incumbent_retained: Literal[True] = True
    rejected_candidate_selected: Literal[False] = False
    further_retrieval_candidate_authorized: Literal[False] = False
    retrieval_optimization_status: Literal["PAUSED_UNTIL_NEW_EVIDENCE"] = (
        "PAUSED_UNTIL_NEW_EVIDENCE"
    )

    protected_confirmation_authorized: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_live_qualification_required: Literal[True] = True
    provider_live_qualification_satisfied: Literal[False] = False
    advance_to_g5k_runtime_provider_qualification: Literal[True] = True

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False
    readiness_review_complete: Literal[True] = True

    @model_validator(mode="after")
    def validate_review(self) -> Self:
        observed = {
            item.case_id: (
                item.incumbent_minimum_raw_top_k,
                item.best_native_lane_rank,
                item.candidate_minimum_raw_top_k,
                item.candidate_full_gold_k20,
            )
            for item in self.failed_case_observations
        }
        if observed != _FAILED_CASE_EXPECTATIONS:
            raise ValueError("failed-case causal evidence drifted")
        if self.rejected_candidate_selected:
            raise ValueError("rejected stratified candidate cannot be selected")
        if self.further_retrieval_candidate_authorized:
            raise ValueError("readiness review cannot authorize another retrieval candidate")
        if self.protected_confirmation_authorized:
            raise ValueError("rejected candidate cannot proceed to protected confirmation")
        if self.provider_live_qualification_satisfied:
            raise ValueError("provider live qualification remains unsatisfied")
        if not self.advance_to_g5k_runtime_provider_qualification:
            raise ValueError("readiness review must advance to G5K")
        if self.baseline_execution_authorized or self.b0_executed or self.release_eligible:
            raise ValueError("readiness review overclaims downstream state")
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


def _failed_case_observations(
    diagnostic: Phase5EvidenceLaneDiagnosticV1,
    characterization: Phase5StratifiedRetrievalCharacterizationV1,
) -> tuple[
    PostStratifiedFailureObservationV1,
    PostStratifiedFailureObservationV1,
    PostStratifiedFailureObservationV1,
    PostStratifiedFailureObservationV1,
]:
    diagnostic_by_case = {
        item.case_id: item
        for item in diagnostic.observations
        if item.role == "development" and item.previously_failed_development_case
    }
    characterization_by_case = {
        item.case_id: item
        for item in characterization.case_results
        if item.role == "development" and item.previously_failed_development_case
    }

    if set(diagnostic_by_case) != set(_FAILED_CASE_EXPECTATIONS):
        raise ValueError("diagnostic failed-case identities drifted")
    if set(characterization_by_case) != set(_FAILED_CASE_EXPECTATIONS):
        raise ValueError("characterization failed-case identities drifted")

    observations: list[PostStratifiedFailureObservationV1] = []
    for case_id in sorted(_FAILED_CASE_EXPECTATIONS):
        diagnostic_case = diagnostic_by_case[case_id]
        characterization_case = characterization_by_case[case_id]

        incumbent = characterization_case.incumbent_minimum_raw_top_k
        candidate = characterization_case.candidate_minimum_raw_top_k
        if incumbent is None or candidate is None:
            raise ValueError(f"failed case lacks required rank evidence: {case_id}")

        native_ranks = tuple(item.native_lane_bm25_rank for item in diagnostic_case.evidence)
        if any(rank is None for rank in native_ranks):
            raise ValueError(f"failed case lacks native-lane rank evidence: {case_id}")

        observations.append(
            PostStratifiedFailureObservationV1(
                case_id=case_id,
                incumbent_minimum_raw_top_k=incumbent,
                best_native_lane_rank=max(cast(int, rank) for rank in native_ranks),
                candidate_minimum_raw_top_k=candidate,
                candidate_full_gold_k20=characterization_case.candidate_full_gold_k20,
            )
        )

    typed = tuple(observations)
    return typed[0], typed[1], typed[2], typed[3]


def materialize_phase5_post_stratified_readiness_review(
    repo_root: Path,
) -> tuple[Phase5PostStratifiedReadinessReviewV1, str]:
    diagnostic = Phase5EvidenceLaneDiagnosticV1.model_validate_json(
        _verified_bytes(repo_root / _DIAGNOSTIC_PATH, _DIAGNOSTIC_SHA256)
    )
    characterization = Phase5StratifiedRetrievalCharacterizationV1.model_validate_json(
        _verified_bytes(repo_root / _CHARACTERIZATION_PATH, _CHARACTERIZATION_SHA256)
    )
    provider_freeze = Phase5SemanticProviderProfileFreezeReceipt.model_validate_json(
        _verified_bytes(repo_root / _PROVIDER_FREEZE_PATH, _PROVIDER_FREEZE_SHA256)
    )

    if diagnostic.failed_development_native_lane_recovered_count != 4:
        raise ValueError("diagnostic 4/4 recovery evidence drifted")
    if characterization.run_validity != "VALID":
        raise ValueError("stratified characterization is not valid")
    if characterization.characterization_decision != "REJECT":
        raise ValueError("stratified characterization is not the frozen REJECT result")

    point_20 = next(point for point in characterization.top_k_curve if point.top_k == 20)
    if point_20.retrieved_required_evidence_count != 40:
        raise ValueError("k20 retrieved-evidence numerator drifted")
    if provider_freeze.live_qualification_satisfied:
        raise ValueError("provider live-qualification state changed")

    receipt = Phase5PostStratifiedReadinessReviewV1(
        failed_case_observations=_failed_case_observations(diagnostic, characterization)
    )
    digest = write_json_with_sha256(repo_root / _OUTPUT_PATH, receipt)
    return receipt, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    receipt, digest = materialize_phase5_post_stratified_readiness_review(repo_root)

    print(f"PHASE5_POST_STRATIFIED_READINESS_SHA256={digest}")
    print(f"PHASE5_POST_STRATIFIED_CHARACTERIZATION_DECISION={receipt.characterization_decision}")
    print(f"PHASE5_POST_STRATIFIED_FAILED_DEV_RECOVERY={receipt.candidate_failed_development_recovered_count}/4")
    print(
        "PHASE5_POST_STRATIFIED_K20="
        f"full_gold:{receipt.candidate_full_gold_k20_case_count}/35,"
        f"required_evidence:{receipt.candidate_retrieved_required_evidence_at_k20}/43"
    )
    print(f"PHASE5_RETRIEVAL_OPTIMIZATION_STATUS={receipt.retrieval_optimization_status}")
    print(
        "PHASE5_FURTHER_RETRIEVAL_CANDIDATE_AUTHORIZED="
        f"{str(receipt.further_retrieval_candidate_authorized).lower()}"
    )
    print(
        "PHASE5_PROTECTED_CONFIRMATION_AUTHORIZED="
        f"{str(receipt.protected_confirmation_authorized).lower()}"
    )
    print(
        "PHASE5_PROVIDER_LIVE_QUALIFICATION_SATISFIED="
        f"{str(receipt.provider_live_qualification_satisfied).lower()}"
    )
    print(
        "PHASE5_ADVANCE_TO_G5K_RUNTIME_PROVIDER_QUALIFICATION="
        f"{str(receipt.advance_to_g5k_runtime_provider_qualification).lower()}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(receipt.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_READINESS_REVIEW_COMPLETE="
        f"{str(receipt.readiness_review_complete).lower()}"
    )


if __name__ == "__main__":
    main()
