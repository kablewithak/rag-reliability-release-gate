from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.provider_live_qualification import (
    materialize_phase5_semantic_provider_live_qualification,
)

ROOT = Path(__file__).resolve().parents[2]


def test_live_provider_qualification_binds_all_required_passes() -> None:
    receipt, _digest = (
        materialize_phase5_semantic_provider_live_qualification(
            ROOT
        )
    )

    assert receipt.required_probe_count == 3
    assert receipt.passing_probe_count == 3

    assert receipt.context_a_passed is True
    assert receipt.context_b_passed is True
    assert receipt.refusal_passed is True

    assert receipt.live_qualification_satisfied is True
    assert receipt.generation_is_context_sensitive is True
    assert receipt.semantic_refusal_observed is True

    assert receipt.automatic_retry_count_per_probe == 0


def test_live_provider_qualification_does_not_authorize_b0() -> None:
    receipt, _digest = (
        materialize_phase5_semantic_provider_live_qualification(
            ROOT
        )
    )

    assert receipt.baseline_readiness_refresh_required is True
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False

    assert receipt.post_reject_confirmation_inspected is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.release_eligible is False
