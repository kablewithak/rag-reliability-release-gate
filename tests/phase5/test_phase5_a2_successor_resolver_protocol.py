from __future__ import annotations

from rag_reliability.evaluation.a2_successor_resolver_protocol import (
    build_phase5_a2_successor_resolver_protocol_v1,
)


def test_a2_is_a_new_successor_bound_to_a1_rejection() -> None:
    protocol = build_phase5_a2_successor_resolver_protocol_v1()

    assert protocol.experiment_id == "phase5-a2-object-subresource-resolver-v1"
    assert protocol.parent_a1_rejection_sha256 == (
        "2ad66ffeb2b86c2348789cdf8c19d55492bd8a0001871e0a2566d5829e92de88"
    )
    assert protocol.candidate_count == 1
    assert protocol.gate.parameter_sweep_allowed is False


def test_a2_runtime_evidence_boundary_remains_query_and_catalog_only() -> None:
    protocol = build_phase5_a2_successor_resolver_protocol_v1()
    evidence = protocol.runtime_evidence

    assert evidence.runtime_input_fields == (
        "query",
        "runtime_operation_catalog",
    )
    assert "gold_operation_id" in evidence.forbidden_evaluator_fields
    assert "required_evidence_ids" in evidence.forbidden_evaluator_fields
    assert evidence.post_reject_confirmation_content_allowed is False
    assert evidence.held_out_content_allowed is False
    assert evidence.query_specific_exceptions_allowed is False
    assert evidence.hard_coded_invitation_target_allowed is False


def test_a2_requires_generic_object_or_subresource_evidence() -> None:
    derivation = build_phase5_a2_successor_resolver_protocol_v1().derivation

    assert derivation.namespace_derivation == "operation_id_prefix_before_slash"
    assert derivation.action_derivation == (
        "first_normalized_operation_token_after_namespace_from_runtime_catalog"
    )
    assert derivation.object_subresource_derivation == (
        "remaining_normalized_operation_id_tokens_after_action_plus_literal_path_segments"
    )
    assert derivation.path_parameter_placeholders_contribute_object_evidence is False

    assert derivation.already_resolved_baseline_result_preserved is True
    assert derivation.partial_resolution_requires_namespace_evidence is True
    assert derivation.partial_resolution_requires_action_evidence is True
    assert derivation.partial_resolution_requires_object_or_subresource_evidence is True

    assert derivation.unique_supported_operation_required_for_resolution is True
    assert derivation.multiple_supported_operations_result == "ambiguous"
    assert derivation.zero_supported_operations_result == "unresolved"
    assert derivation.tie_break_by_rank_allowed is False


def test_a2_gate_preserves_safety_and_forces_baseline_review() -> None:
    gate = build_phase5_a2_successor_resolver_protocol_v1().gate

    assert gate.fixed_fixture_expectation_mismatches_allowed == 0
    assert gate.fixed_fixture_false_confident_resolutions_allowed == 0
    assert gate.fixed_fixture_nondeterministic_resolutions_allowed == 0

    assert gate.invitation_target_case_count == 2
    assert gate.invitation_target_cases_required_correctly_resolved == 2
    assert gate.development_false_confident_resolutions_allowed == 0
    assert gate.development_nondeterministic_resolutions_allowed == 0

    assert gate.stop_after_single_bounded_characterization is True
    assert gate.automatic_a3_authorized is False
    assert gate.baseline_readiness_review_required_after_a2 is True


def test_a2_protocol_preserves_nonexecution_and_sealed_roles() -> None:
    protocol = build_phase5_a2_successor_resolver_protocol_v1()

    assert protocol.candidate_execution_authorized_at_protocol_freeze is False
    assert protocol.candidate_implemented is False
    assert protocol.candidate_executed is False

    assert protocol.post_reject_confirmation_inspected is False
    assert protocol.post_reject_confirmation_executed is False
    assert protocol.held_out_case_content_read is False
    assert protocol.held_out_outcomes_exposed is False

    assert protocol.provider_invoked is False
    assert protocol.retrieval_configuration_selected is False
    assert protocol.semantic_runtime_configuration_selected is False
    assert protocol.semantic_runtime_configuration_frozen is False

    assert protocol.b0_executed is False
    assert protocol.chaos_executed is False
    assert protocol.load_executed is False
    assert protocol.release_eligible is False
