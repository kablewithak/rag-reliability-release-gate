from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.post_stratified_readiness_review import (
    _FAILED_CASE_EXPECTATIONS,
    materialize_phase5_post_stratified_readiness_review,
)

ROOT = Path(__file__).resolve().parents[2]


def test_post_stratified_review_preserves_exact_causal_evidence() -> None:
    receipt, _digest = materialize_phase5_post_stratified_readiness_review(ROOT)

    observed = {
        item.case_id: (
            item.incumbent_minimum_raw_top_k,
            item.best_native_lane_rank,
            item.candidate_minimum_raw_top_k,
            item.candidate_full_gold_k20,
        )
        for item in receipt.failed_case_observations
    }

    assert observed == _FAILED_CASE_EXPECTATIONS


def test_post_stratified_review_stops_retrieval_tuning_and_advances_to_g5k() -> None:
    receipt, _digest = materialize_phase5_post_stratified_readiness_review(ROOT)

    assert receipt.characterization_valid is True
    assert receipt.characterization_decision == "REJECT"
    assert receipt.incumbent_retained is True
    assert receipt.rejected_candidate_selected is False
    assert receipt.further_retrieval_candidate_authorized is False
    assert receipt.retrieval_optimization_status == "PAUSED_UNTIL_NEW_EVIDENCE"
    assert receipt.protected_confirmation_authorized is False
    assert receipt.provider_live_qualification_required is True
    assert receipt.provider_live_qualification_satisfied is False
    assert receipt.advance_to_g5k_runtime_provider_qualification is True
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False
    assert receipt.release_eligible is False
    assert receipt.readiness_review_complete is True
