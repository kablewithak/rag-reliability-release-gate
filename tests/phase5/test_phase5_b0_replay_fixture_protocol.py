from __future__ import annotations

from rag_reliability.evaluation.b0_replay_fixture_protocol import (
    build_phase5_b0_replay_fixture_protocol_v1,
)


def test_b0_replay_fixture_protocol_preserves_evaluator_boundary() -> None:
    protocol = build_phase5_b0_replay_fixture_protocol_v1()

    assert protocol.authorized_case_count == 42
    assert protocol.development_case_count == 24
    assert protocol.tuning_case_count == 18
    assert protocol.runtime_projection_fields == ("case_id", "query")

    assert "required_facts" in protocol.forbidden_authoring_fields
    assert "required_evidence_ids" in protocol.forbidden_authoring_fields
    assert "expected_response_mode" in protocol.forbidden_authoring_fields

    assert protocol.evaluator_fields_used_for_fixture_authoring is False
    assert protocol.expected_modes_used_for_fixture_authoring is False
    assert protocol.gold_facts_used_for_fixture_authoring is False
    assert protocol.gold_evidence_used_for_fixture_authoring is False


def test_b0_replay_fixture_protocol_freezes_deterministic_policy() -> None:
    protocol = build_phase5_b0_replay_fixture_protocol_v1()

    assert protocol.provider_mode == "query_keyed_scripted_response"
    assert protocol.generation_is_context_sensitive is False
    assert protocol.fixture_generation_policy == (
        "first_eligible_bounded_context_item_verbatim"
    )
    assert protocol.new_live_provider_calls_authorized == 0
    assert protocol.parameter_sweep_authorized is False
    assert protocol.post_hoc_response_editing_authorized is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False
