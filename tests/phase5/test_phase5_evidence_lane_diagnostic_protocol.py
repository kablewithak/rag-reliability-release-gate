from __future__ import annotations

from rag_reliability.evaluation.evidence_lane_diagnostic_protocol import (
    build_phase5_evidence_lane_diagnostic_protocol_v1,
)


def test_evidence_lane_protocol_binds_three_rejection_chain() -> None:
    protocol = build_phase5_evidence_lane_diagnostic_protocol_v1()

    assert protocol.parent_development_rejection_sha256 == (
        "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
    )
    assert protocol.parent_a1_rejection_sha256 == (
        "2ad66ffeb2b86c2348789cdf8c19d55492bd8a0001871e0a2566d5829e92de88"
    )
    assert protocol.parent_a2_rejection_sha256 == (
        "3a113bc0ac59820e36dc46e9028ace60bdef5f307f6ba76633d36cf25e4f7d13"
    )
    assert protocol.parent_companion_rejection_sha256 == (
        "4997bb745e018ed69b24daad0062ccdb00b218bf66eabf33c1610a39f94e8f1b"
    )


def test_evidence_lane_diagnostic_runs_all_lanes_for_every_query() -> None:
    boundary = build_phase5_evidence_lane_diagnostic_protocol_v1().boundary

    assert boundary.lanes_executed_for_every_query == (
        "authored_section",
        "openapi_operation_core",
        "openapi_component",
    )
    assert boundary.retrieval_algorithm == (
        "existing_phase5_bm25_candidate_scoring"
    )
    assert boundary.lane_partition_field == "chunk_kind"

    assert boundary.evaluator_fields_passed_to_lane_retrievers is False
    assert boundary.case_ids_used_for_runtime_routing is False
    assert boundary.required_evidence_ids_used_for_runtime_routing is False
    assert boundary.lane_selected_from_gold is False


def test_evidence_lane_measurement_is_diagnostic_not_candidate() -> None:
    measurement = (
        build_phase5_evidence_lane_diagnostic_protocol_v1().measurement
    )

    assert measurement.characterization_scope == (
        "spent_development_answerable_cases",
        "tuning_answerable_cases",
    )
    assert measurement.compare_rank_surfaces == (
        "global_bm25",
        "global_operation_aware_rrf_incumbent",
        "native_lane_bm25",
    )
    assert measurement.deterministic_repeat_count == 3
    assert measurement.native_lane_top_k_threshold == 20

    assert measurement.candidate_ranking_emitted is False
    assert measurement.lane_fusion_emitted is False
    assert measurement.lane_quota_emitted is False
    assert measurement.parameter_sweep_allowed is False


def test_evidence_lane_decision_fork_preserves_failure_families() -> None:
    decision = (
        build_phase5_evidence_lane_diagnostic_protocol_v1().decision_fork
    )

    assert decision.authored_failure_case_ids == (
        "phase4-dev-breaking-version-migration",
        "phase4-dev-troubleshooting-method-and-rate-limit",
    )
    assert decision.operation_core_failure_case_ids == (
        "phase4-dev-repos-accept-invitation-current",
        "phase4-dev-repos-accept-invitation-success",
    )

    assert decision.diagnostic_may_authorize_candidate_implementation is False
    assert decision.diagnostic_may_select_runtime_configuration is False
    assert decision.baseline_readiness_review_required_after_diagnostic is True


def test_evidence_lane_protocol_preserves_protected_boundaries() -> None:
    protocol = build_phase5_evidence_lane_diagnostic_protocol_v1()

    assert protocol.diagnostic_implemented is False
    assert protocol.diagnostic_executed is False

    assert protocol.runtime_retriever_changed is False
    assert protocol.corpus_mutated is False
    assert protocol.chunking_policy_changed is False
    assert protocol.candidate_implemented is False
    assert protocol.candidate_executed is False
    assert protocol.composition_authorized is False

    assert protocol.post_reject_confirmation_inspected is False
    assert protocol.post_reject_confirmation_executed is False
    assert protocol.held_out_case_content_read is False
    assert protocol.held_out_outcomes_exposed is False

    assert protocol.provider_invoked is False
    assert protocol.retrieval_configuration_selected is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False
    assert protocol.release_eligible is False
