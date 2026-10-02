from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.stratified_retrieval_candidate_protocol import (
    Phase5StratifiedRetrievalCandidateProtocolV1,
    build_phase5_stratified_retrieval_candidate_protocol_v1,
)


def test_stratified_protocol_binds_exactly_one_candidate() -> None:
    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()

    assert protocol.candidate.candidate_count == 1
    assert protocol.candidate.parameter_sweep_used is False
    assert protocol.candidate.tuning_parameter_optimization_used is False
    assert protocol.stop_after_candidate_failure is True
    assert protocol.nearby_candidate_execution_authorized_after_failure is False


def test_stratified_candidate_preserves_incumbent_and_all_three_lanes() -> None:
    candidate = build_phase5_stratified_retrieval_candidate_protocol_v1().candidate

    assert candidate.base_ranking == "global_operation_aware_rrf_incumbent"
    assert candidate.lanes == (
        "authored_section",
        "openapi_operation_core",
        "openapi_component",
    )
    assert candidate.lanes_executed_for_every_query is True
    assert candidate.lane_partition_field == "chunk_kind"
    assert candidate.lane_scoring == "existing_phase5_bm25_candidate_scoring"

    assert candidate.merge_method == (
        "equal_weight_rrf_incumbent_rank_plus_native_lane_rank"
    )
    assert candidate.fusion_constant == 60
    assert candidate.incumbent_rank_weight == 1
    assert candidate.native_lane_rank_weight == 1
    assert candidate.post_merge_operation_partition is False

    assert candidate.raw_cross_lane_score_comparison_used is False
    assert candidate.fixed_lane_quota_used is False
    assert candidate.round_robin_merge_used is False


def test_stratified_candidate_retains_existing_runtime_budgets() -> None:
    candidate = build_phase5_stratified_retrieval_candidate_protocol_v1().candidate

    assert candidate.final_retrieval_top_k == 20
    assert candidate.context_max_evidence_items == 15
    assert candidate.context_max_budget_characters == 69663
    assert candidate.corpus_changed is False
    assert candidate.chunking_changed is False
    assert candidate.source_policy_changed is False
    assert candidate.context_policy_changed is False


def test_stratified_gate_requires_total_recovery_without_regression() -> None:
    gate = build_phase5_stratified_retrieval_candidate_protocol_v1().promotion_gate

    assert gate.development_answerable_case_count == 20
    assert gate.tuning_answerable_case_count == 15
    assert gate.total_answerable_case_count == 35
    assert gate.required_evidence_reference_count == 43

    assert gate.failed_development_case_count == 4
    assert gate.failed_development_cases_required_recovered == 4
    assert gate.full_gold_cases_at_k20_required == 35
    assert gate.micro_gold_recall_at_k20_required == "1.0"

    assert gate.maximum_raw_top_k_allowed == 20
    assert gate.maximum_eligible_items_allowed == 15
    assert gate.maximum_context_prefix_characters_allowed == 69663

    assert gate.previously_passing_full_gold_k20_regressions_allowed == 0
    assert gate.source_filter_regressions_allowed == 0
    assert gate.context_inclusion_regressions_allowed == 0
    assert gate.refusal_or_fallback_regressions_allowed == 0

    assert gate.deterministic_repeat_count == 3
    assert gate.provider_calls_allowed == 0


def test_stratified_protocol_preserves_evaluator_boundary() -> None:
    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()

    assert protocol.allowed_runtime_signal_fields == (
        "query",
        "frozen_chunk_corpus",
        "phase3d_chunk.chunk_kind",
        "phase3d_chunk.linked_operation_ids",
    )
    assert "required_evidence_ids" in protocol.forbidden_evaluator_fields
    assert "case_id_as_runtime_signal" in protocol.forbidden_evaluator_fields
    assert "data_role_as_runtime_signal" in protocol.forbidden_evaluator_fields
    assert "held_out_outcomes" in protocol.forbidden_evaluator_fields

    assert protocol.development_gold_used_for_scoring_only is True
    assert protocol.tuning_gold_used_for_scoring_only is True
    assert protocol.post_reject_confirmation_inspected is False
    assert protocol.held_out_case_content_read is False


def test_stratified_protocol_preserves_nonexecution_and_readiness_review() -> None:
    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()

    assert protocol.candidate_implemented is False
    assert protocol.candidate_executed is False
    assert protocol.runtime_retriever_changed is False
    assert protocol.provider_invoked is False

    assert protocol.retrieval_configuration_selected is False
    assert protocol.semantic_runtime_configuration_selected is False
    assert protocol.semantic_runtime_configuration_frozen is False

    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False
    assert protocol.release_eligible is False
    assert protocol.baseline_readiness_review_required_after_result is True


def test_stratified_protocol_cannot_authorize_downstream_promotion_by_tampering() -> None:
    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["promotion_gate"]["semantic_runtime_promotion_authorized"] = True

    with pytest.raises(ValidationError):
        Phase5StratifiedRetrievalCandidateProtocolV1.model_validate(payload)
