from __future__ import annotations

from rag_reliability.evaluation.post_reject_intervention_design_protocol import (
    build_phase5_post_reject_intervention_design_protocol_v1,
)


def test_intervention_design_separates_hypotheses() -> None:
    protocol = build_phase5_post_reject_intervention_design_protocol_v1()

    assert protocol.resolver_experiment.candidate_count == 1
    assert protocol.companion_experiment.candidate_count == 1

    assert protocol.resolver_experiment.parameter_sweep_allowed is False
    assert protocol.companion_experiment.parameter_sweep_allowed is False

    assert protocol.resolver_experiment.hard_coded_accept_token_allowed is False
    assert protocol.companion_experiment.resolved_operation_ranking_unchanged is True


def test_resolver_candidate_is_catalog_derived() -> None:
    candidate = build_phase5_post_reject_intervention_design_protocol_v1().resolver_experiment

    assert candidate.action_source == (
        "first_normalized_operation_token_after_namespace_from_runtime_catalog"
    )
    assert candidate.partial_match_requires_namespace is True
    assert candidate.partial_match_requires_catalog_derived_action is True
    assert candidate.false_confident_resolution_count_allowed == 0
    assert candidate.invitation_failure_cases_required_correctly_resolved == 2


def test_companion_candidate_is_bounded() -> None:
    candidate = build_phase5_post_reject_intervention_design_protocol_v1().companion_experiment

    assert candidate.anchor_window == 5
    assert candidate.maximum_anchor_sources == 1
    assert candidate.activation_resolution_states == (
        "ambiguous",
        "unresolved",
    )
    assert candidate.targeted_cross_cutting_failure_cases_required_k20 == 2
    assert candidate.previously_passing_development_k20_regressions_allowed == 0
    assert candidate.tuning_k20_regressions_allowed == 0


def test_fresh_confirmation_remains_one_shot_and_sealed() -> None:
    protocol = build_phase5_post_reject_intervention_design_protocol_v1()
    gate = protocol.composition_gate

    assert gate.composition_allowed_only_after_both_characterizations_pass is True
    assert gate.fresh_confirmation_execution_count_allowed == 1
    assert gate.fresh_confirmation_retuning_after_execution_allowed is False
    assert gate.fresh_confirmation_may_be_opened_before_composed_protocol_freeze is False

    assert protocol.fresh_confirmation_executed is False
    assert protocol.held_out_case_content_read is False
    assert protocol.held_out_outcomes_exposed is False
