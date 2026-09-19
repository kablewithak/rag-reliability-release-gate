from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.operation_aware_rrf_protocol import (
    Phase5OperationAwareRrfProtocolV1,
    build_phase5_operation_aware_rrf_protocol_v1,
)


def test_slice2_protocol_binds_exactly_one_candidate() -> None:
    protocol = build_phase5_operation_aware_rrf_protocol_v1()

    assert protocol.candidate.candidate_count == 1
    assert protocol.candidate.parameter_sweep_used is False
    assert protocol.candidate.tuning_parameter_optimization_used is False
    assert protocol.stop_after_candidate_failure is True
    assert protocol.nearby_candidate_execution_authorized_after_failure is False


def test_slice2_candidate_is_stable_partition_only() -> None:
    candidate = build_phase5_operation_aware_rrf_protocol_v1().candidate

    assert candidate.intervention == ("stable_partition_by_exact_resolved_operation_lineage")
    assert candidate.resolved_behavior == (
        "operation_linked_first_preserve_partition_relative_order"
    )
    assert candidate.ambiguous_behavior == "preserve_generic_rrf_exactly"
    assert candidate.unresolved_behavior == "preserve_generic_rrf_exactly"
    assert candidate.score_values_changed is False
    assert candidate.base_rrf_configuration_changed is False


def test_slice2_gate_requires_complete_k20_recovery() -> None:
    gate = build_phase5_operation_aware_rrf_protocol_v1().promotion_gate

    assert gate.full_gold_cases_at_k20_required == 15
    assert gate.micro_gold_recall_at_k20_required == "1.0"
    assert gate.maximum_raw_top_k_allowed == 20
    assert gate.maximum_eligible_items_allowed == 20
    assert gate.maximum_context_prefix_characters_allowed == 102463
    assert gate.unretrievable_cases_allowed == 0
    assert gate.filter_ineligible_cases_allowed == 0
    assert gate.full_gold_k20_regressions_allowed == 0


def test_slice2_does_not_confuse_incumbent_context_with_runtime_capacity() -> None:
    gate = build_phase5_operation_aware_rrf_protocol_v1().promotion_gate

    assert gate.context_limit_semantics == (
        "not_worse_than_measured_rrf_incumbent_not_runtime_capacity"
    )
    assert gate.semantic_runtime_capacity_gate_satisfied is False
    assert gate.semantic_runtime_promotion_authorized is False


def test_slice2_preserves_evaluator_boundary() -> None:
    protocol = build_phase5_operation_aware_rrf_protocol_v1()

    assert protocol.allowed_runtime_signal_fields == (
        "query",
        "phase3d_chunk.linked_operation_ids",
    )
    assert "required_evidence_ids" in protocol.forbidden_evaluator_fields
    assert "gold_operation_id" in protocol.forbidden_evaluator_fields
    assert protocol.provider_invoked is False
    assert protocol.held_out_outcomes_exposed is False
    assert protocol.development_gold_used is False


def test_slice2_cannot_enable_semantic_runtime_promotion_by_tampering() -> None:
    protocol = build_phase5_operation_aware_rrf_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["promotion_gate"]["semantic_runtime_promotion_authorized"] = True

    with pytest.raises(ValidationError):
        Phase5OperationAwareRrfProtocolV1.model_validate(payload)
