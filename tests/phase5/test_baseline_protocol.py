from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import EvaluationRole
from rag_reliability.evaluation.baseline_protocol import (
    Phase5BaselineProtocolV1,
    build_phase5_baseline_protocol_v1,
)


def test_protocol_binds_all_three_frozen_roles() -> None:
    protocol = build_phase5_baseline_protocol_v1()

    bindings = {
        binding.role: binding
        for binding in protocol.role_bindings
    }

    assert set(bindings) == set(EvaluationRole)

    assert bindings[EvaluationRole.DEVELOPMENT].case_count == 24
    assert bindings[EvaluationRole.DEVELOPMENT].cluster_count == 12
    assert bindings[EvaluationRole.DEVELOPMENT].included_in_baseline is True

    assert bindings[EvaluationRole.TUNING].case_count == 18
    assert bindings[EvaluationRole.TUNING].cluster_count == 9
    assert bindings[EvaluationRole.TUNING].included_in_baseline is True

    assert bindings[EvaluationRole.HELD_OUT].case_count == 18
    assert bindings[EvaluationRole.HELD_OUT].cluster_count == 9
    assert bindings[EvaluationRole.HELD_OUT].included_in_baseline is False


def test_protocol_keeps_execution_unauthorized() -> None:
    protocol = build_phase5_baseline_protocol_v1()

    assert protocol.protocol_status == "draft_unfrozen"
    assert protocol.baseline_execution_authorized is False
    assert protocol.chaos_authorized is False
    assert protocol.intervention_authorized is False
    assert protocol.release_eligible is False


def test_protocol_preserves_runtime_gold_boundary() -> None:
    protocol = build_phase5_baseline_protocol_v1()

    assert protocol.runtime_projection_fields == (
        "case_id",
        "query",
    )
    assert protocol.held_out_outcomes_exposed is False


def test_baseline_validity_is_not_a_quality_threshold() -> None:
    protocol = build_phase5_baseline_protocol_v1()

    measurement = protocol.measurement

    assert measurement.terminal_record_percent_required == 100
    assert measurement.trace_completeness_percent_required == 100
    assert measurement.unauthorized_role_execution_tolerance == 0
    assert measurement.evaluator_leakage_tolerance == 0
    assert measurement.configuration_identity_mismatch_tolerance == 0
    assert measurement.quality_threshold_is_baseline_validity_gate is False


def test_replay_lane_has_explicit_external_validity_limit() -> None:
    protocol = build_phase5_baseline_protocol_v1()

    execution = protocol.execution

    assert execution.evidence_lane == "deterministic_replay_control"
    assert execution.provider_semantics == "query_keyed_scripted_response"
    assert execution.generation_is_context_sensitive is False

    assert "context_sensitive_generation_improvement" in execution.prohibited_claim_ids
    assert "real_provider_robustness" in execution.prohibited_claim_ids
    assert "release_readiness" in execution.prohibited_claim_ids


def test_protocol_budget_is_bounded_and_replicated() -> None:
    protocol = build_phase5_baseline_protocol_v1()

    assert protocol.included_case_count == 42
    assert protocol.included_cluster_count == 21

    assert protocol.execution.primary_execution_count_per_case == 1
    assert protocol.execution.deterministic_replication_count_per_case == 1
    assert protocol.execution.maximum_total_case_executions == 84
    assert protocol.execution.same_stage_failure_stop_count == 2


def test_held_out_cannot_be_added_to_baseline_by_payload_tampering() -> None:
    protocol = build_phase5_baseline_protocol_v1()
    payload = protocol.model_dump(mode="json")

    for binding in payload["role_bindings"]:
        if binding["role"] == EvaluationRole.HELD_OUT.value:
            binding["included_in_baseline"] = True

    with pytest.raises(ValidationError, match="HELD_OUT binding drifted"):
        Phase5BaselineProtocolV1.model_validate(payload)
