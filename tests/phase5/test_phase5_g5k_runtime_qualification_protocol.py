from __future__ import annotations

from rag_reliability.evaluation.runtime_qualification_protocol import (
    build_phase5_g5k_runtime_qualification_protocol_v1,
)


def test_g5k_protocol_preserves_lane_boundary() -> None:
    protocol = build_phase5_g5k_runtime_qualification_protocol_v1()

    assert protocol.selected_retrieval_id == (
        "phase5-operation-aware-rrf-stable-partition-v1"
    )

    assert protocol.lane_a_provider_mode == "query_keyed_scripted_response"
    assert protocol.lane_a_generation_is_context_sensitive is False

    assert protocol.lane_b_provider_model_id == "glm-5.2"
    assert protocol.lane_b_live_qualification_satisfied is True
    assert protocol.lane_b_new_live_calls_authorized == 0

    assert "context_sensitive_generation" in protocol.lane_a_prohibited_claim_ids
    assert "trace_accounting" in protocol.lane_a_supported_claim_ids


def test_g5k_protocol_freezes_runtime_and_evaluator_boundaries() -> None:
    protocol = build_phase5_g5k_runtime_qualification_protocol_v1()

    assert protocol.runtime_projection_fields == ("case_id", "query")
    assert "required_evidence_ids" in protocol.forbidden_runtime_evaluator_fields
    assert "gold_facts" in protocol.forbidden_runtime_evaluator_fields

    assert protocol.retrieval_parity_mismatch_tolerance == 0
    assert protocol.control_failure_tolerance == 0
    assert protocol.evaluator_leakage_tolerance == 0
    assert protocol.automatic_retry_tolerance == 0

    assert protocol.protected_confirmation_authorized is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False
    assert protocol.held_out_outcomes_exposed is False
