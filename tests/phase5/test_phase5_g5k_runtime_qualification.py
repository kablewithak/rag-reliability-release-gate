from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.runtime_qualification import (
    materialize_phase5_g5k_runtime_qualification,
)

ROOT = Path(__file__).resolve().parents[2]


def test_g5k_runtime_qualification_preserves_decision_boundary() -> None:
    receipt, _digest = (
        materialize_phase5_g5k_runtime_qualification(
            ROOT
        )
    )

    assert receipt.retrieval_parity_case_count == 42
    assert receipt.retrieval_parity_mismatch_count == 0

    assert len(receipt.control_checks) == 6
    assert all(
        item.passed
        for item in receipt.control_checks
    )

    assert len(receipt.scorer_applicability) == 13
    assert all(
        item.applicable
        for item in receipt.scorer_applicability
    )

    assert receipt.qualification_decision == "PASS"
    assert receipt.lane_a_complete_runtime_qualified is True
    assert receipt.lane_a_generation_is_context_sensitive is False

    assert receipt.lane_b_live_qualification_bound is True
    assert receipt.lane_b_new_live_calls_executed == 0

    assert receipt.post_reject_confirmation_deferred is True
    assert receipt.advance_to_g5m_b0_selection is True

    assert receipt.protected_confirmation_authorized is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False
    assert receipt.held_out_outcomes_exposed is False
