from __future__ import annotations

from rag_reliability.evaluation.source_companion_rescue_protocol import (
    build_phase5_source_companion_rescue_protocol_v1,
)


def test_source_companion_binds_post_reject_evidence_chain() -> None:
    protocol = build_phase5_source_companion_rescue_protocol_v1()

    assert protocol.experiment_id == "phase5-authored-source-companion-rescue-v1"
    assert protocol.parent_development_rejection_sha256 == (
        "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
    )
    assert protocol.parent_failure_localization_sha256 == (
        "5ac9f4b6f7e117a1adf699496ae4d8f3a4e0de7874d597f90c75d8a282cc61d6"
    )
    assert protocol.parent_a1_rejection_sha256 == (
        "2ad66ffeb2b86c2348789cdf8c19d55492bd8a0001871e0a2566d5829e92de88"
    )
    assert protocol.parent_a2_rejection_sha256 == (
        "3a113bc0ac59820e36dc46e9028ace60bdef5f307f6ba76633d36cf25e4f7d13"
    )


def test_source_companion_derivation_matches_frozen_design() -> None:
    derivation = build_phase5_source_companion_rescue_protocol_v1().derivation

    assert derivation.anchor_window == 5
    assert derivation.maximum_anchor_sources == 1
    assert derivation.activation_resolution_states == (
        "ambiguous",
        "unresolved",
    )
    assert derivation.rescue_scope == (
        "same_source_current_authoritative_authored_chunks_only"
    )
    assert derivation.resolved_operation_ranking_unchanged is True
    assert derivation.scores_unchanged is True
    assert derivation.parameter_sweep_allowed is False


def test_source_companion_gate_targets_only_cross_cutting_failures() -> None:
    gate = build_phase5_source_companion_rescue_protocol_v1().gate

    assert gate.target_case_ids == (
        "phase4-dev-breaking-version-migration",
        "phase4-dev-troubleshooting-method-and-rate-limit",
    )
    assert gate.targeted_cross_cutting_failure_cases_required_k20 == 2
    assert gate.previously_passing_development_k20_regressions_allowed == 0
    assert gate.tuning_k20_regressions_allowed == 0
    assert gate.fallback_nondeterminism_allowed == 0


def test_source_companion_runtime_boundary_excludes_evaluator_truth() -> None:
    boundary = build_phase5_source_companion_rescue_protocol_v1().runtime_boundary

    assert boundary.runtime_input_fields == (
        "query",
        "current_ranked_retrieval",
        "frozen_chunk_metadata",
    )
    assert "required_evidence_ids" in boundary.forbidden_evaluator_fields
    assert "gold_operation_id" in boundary.forbidden_evaluator_fields

    assert boundary.target_case_ids_available_to_candidate is False
    assert boundary.development_gold_available_to_candidate is False
    assert boundary.tuning_gold_available_to_candidate is False
    assert boundary.post_reject_confirmation_content_allowed is False
    assert boundary.held_out_content_allowed is False


def test_source_companion_protocol_stops_before_composition_or_b0() -> None:
    protocol = build_phase5_source_companion_rescue_protocol_v1()

    assert protocol.candidate_execution_authorized_at_protocol_freeze is False
    assert protocol.candidate_implemented is False
    assert protocol.candidate_executed is False

    assert protocol.composition_authorized is False
    assert protocol.composed_candidate_executed is False

    assert protocol.post_reject_confirmation_inspected is False
    assert protocol.post_reject_confirmation_executed is False
    assert protocol.held_out_case_content_read is False
    assert protocol.held_out_outcomes_exposed is False

    assert protocol.provider_invoked is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False
    assert protocol.release_eligible is False

    assert protocol.gate.automatic_composition_authorized is False
    assert protocol.gate.automatic_successor_experiment_authorized is False
    assert protocol.gate.baseline_readiness_review_required_after_companion is True
