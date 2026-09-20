"""Freeze Phase 5 post-reject intervention design before candidate execution."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256

_FAILURE_LOCALIZATION_SHA256 = "5ac9f4b6f7e117a1adf699496ae4d8f3a4e0de7874d597f90c75d8a282cc61d6"
_FRESH_CONFIRMATION_FREEZE_SHA256 = (
    "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"
)
_RESOLVER_CHARACTERIZATION_SHA256 = (
    "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
)
_OPERATION_AWARE_CANDIDATE_SHA256 = (
    "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
)
_RRF_INCUMBENT_SHA256 = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
_DEVELOPMENT_SHA256 = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
_TUNING_SHA256 = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
_HELD_OUT_SHA256 = "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
_CHUNK_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"


class ResolverCoverageExperimentV1(ContractModel):
    experiment_id: Literal["phase5-catalog-derived-action-resolver-v3"] = (
        "phase5-catalog-derived-action-resolver-v3"
    )

    hypothesis: Literal["static_action_vocabulary_underresolves_valid_runtime_operations"] = (
        "static_action_vocabulary_underresolves_valid_runtime_operations"
    )

    candidate_count: Literal[1] = 1
    parameter_sweep_allowed: Literal[False] = False

    action_source: Literal[
        "first_normalized_operation_token_after_namespace_from_runtime_catalog"
    ] = "first_normalized_operation_token_after_namespace_from_runtime_catalog"

    exact_operation_match_preserved: Literal[True] = True
    method_path_match_preserved: Literal[True] = True
    full_signature_match_preserved: Literal[True] = True

    partial_match_requires_namespace: Literal[True] = True
    partial_match_requires_catalog_derived_action: Literal[True] = True

    hard_coded_accept_token_allowed: Literal[False] = False
    evaluator_gold_used_as_runtime_input: Literal[False] = False

    characterization_scope: tuple[
        Literal[
            "existing_resolver_fixed_fixtures",
            "spent_development_answerable_cases",
        ],
        Literal[
            "existing_resolver_fixed_fixtures",
            "spent_development_answerable_cases",
        ],
    ] = (
        "existing_resolver_fixed_fixtures",
        "spent_development_answerable_cases",
    )

    invitation_failure_cases_required_correctly_resolved: Literal[2] = 2
    false_confident_resolution_count_allowed: Literal[0] = 0
    nondeterministic_resolution_count_allowed: Literal[0] = 0

    new_candidate_execution_authorized_at_protocol_freeze: Literal[False] = False


class SourceCompanionRescueExperimentV1(ContractModel):
    experiment_id: Literal["phase5-authored-source-companion-rescue-v1"] = (
        "phase5-authored-source-companion-rescue-v1"
    )

    hypothesis: Literal[
        "multi_evidence_guidance_queries_need_bounded_same_source_companion_recall"
    ] = "multi_evidence_guidance_queries_need_bounded_same_source_companion_recall"

    candidate_count: Literal[1] = 1
    parameter_sweep_allowed: Literal[False] = False

    base_ranking: Literal["current_operation_aware_rrf_candidate"] = (
        "current_operation_aware_rrf_candidate"
    )

    activation_resolution_states: tuple[
        Literal["ambiguous", "unresolved"],
        Literal["ambiguous", "unresolved"],
    ] = ("ambiguous", "unresolved")

    anchor_window: Literal[5] = 5
    anchor_selection: Literal[
        "highest_ranked_current_authoritative_authored_chunk_in_anchor_window"
    ] = "highest_ranked_current_authoritative_authored_chunk_in_anchor_window"

    maximum_anchor_sources: Literal[1] = 1

    rescue_scope: Literal["same_source_current_authoritative_authored_chunks_only"] = (
        "same_source_current_authoritative_authored_chunks_only"
    )

    ordering: Literal[
        "prefix_before_anchor_then_anchor_then_same_source_siblings_in_existing_order_then_rest"
    ] = "prefix_before_anchor_then_anchor_then_same_source_siblings_in_existing_order_then_rest"

    resolved_operation_ranking_unchanged: Literal[True] = True
    scores_unchanged: Literal[True] = True

    evaluator_gold_used_as_runtime_input: Literal[False] = False

    characterization_scope: tuple[
        Literal[
            "spent_development_answerable_cases",
            "tuning_answerable_cases",
        ],
        Literal[
            "spent_development_answerable_cases",
            "tuning_answerable_cases",
        ],
    ] = (
        "spent_development_answerable_cases",
        "tuning_answerable_cases",
    )

    targeted_cross_cutting_failure_cases_required_k20: Literal[2] = 2
    previously_passing_development_k20_regressions_allowed: Literal[0] = 0
    tuning_k20_regressions_allowed: Literal[0] = 0
    fallback_nondeterminism_allowed: Literal[0] = 0

    new_candidate_execution_authorized_at_protocol_freeze: Literal[False] = False


class CompositionGateV1(ContractModel):
    composition_allowed_only_after_both_characterizations_pass: Literal[True] = True

    composed_candidate_id: Literal["phase5-resolver-v3-plus-source-companion-rescue-v1"] = (
        "phase5-resolver-v3-plus-source-companion-rescue-v1"
    )

    development_diagnostic_full_gold_k20_required: Literal[20] = 20
    development_diagnostic_micro_gold_recall_required: Literal["1.0"] = "1.0"

    invitation_cases_required_k20: Literal[2] = 2
    cross_cutting_failure_cases_required_k20: Literal[2] = 2

    development_k20_regressions_allowed: Literal[0] = 0
    tuning_k20_regressions_allowed: Literal[0] = 0

    fresh_confirmation_may_be_opened_before_composed_protocol_freeze: Literal[False] = False

    fresh_confirmation_execution_count_allowed: Literal[1] = 1
    fresh_confirmation_retuning_after_execution_allowed: Literal[False] = False


class Phase5PostRejectInterventionDesignProtocolV1(ContractModel):
    protocol_version: Literal["phase5-post-reject-intervention-design-protocol-v1"] = (
        "phase5-post-reject-intervention-design-protocol-v1"
    )

    failure_localization_sha256: Sha256 = _FAILURE_LOCALIZATION_SHA256
    fresh_confirmation_freeze_sha256: Sha256 = _FRESH_CONFIRMATION_FREEZE_SHA256
    resolver_characterization_sha256: Sha256 = _RESOLVER_CHARACTERIZATION_SHA256
    operation_aware_candidate_sha256: Sha256 = _OPERATION_AWARE_CANDIDATE_SHA256
    rrf_incumbent_sha256: Sha256 = _RRF_INCUMBENT_SHA256

    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SHA256
    held_out_suite_sha256: Sha256 = _HELD_OUT_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    resolver_experiment: ResolverCoverageExperimentV1
    companion_experiment: SourceCompanionRescueExperimentV1
    composition_gate: CompositionGateV1

    experiment_order: tuple[
        Literal[
            "resolver_characterization",
            "source_companion_characterization",
            "composed_diagnostic_candidate",
            "fresh_confirmation_once",
        ],
        ...,
    ] = (
        "resolver_characterization",
        "source_companion_characterization",
        "composed_diagnostic_candidate",
        "fresh_confirmation_once",
    )

    development_role: Literal["diagnostic_only_spent_for_future_confirmation"] = (
        "diagnostic_only_spent_for_future_confirmation"
    )

    tuning_role: Literal["intervention_tuning_and_regression_only"] = (
        "intervention_tuning_and_regression_only"
    )

    fresh_confirmation_role: Literal[
        "independent_confirmation_once_after_composed_protocol_freeze"
    ] = "independent_confirmation_once_after_composed_protocol_freeze"

    held_out_role: Literal["sealed_final_evidence"] = "sealed_final_evidence"

    resolver_candidate_executed: Literal[False] = False
    companion_candidate_executed: Literal[False] = False
    composed_candidate_executed: Literal[False] = False
    fresh_confirmation_executed: Literal[False] = False

    next_intervention_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol(self) -> Self:
        if self.experiment_order != (
            "resolver_characterization",
            "source_companion_characterization",
            "composed_diagnostic_candidate",
            "fresh_confirmation_once",
        ):
            raise ValueError("intervention experiment order drifted")

        if (
            self.resolver_candidate_executed
            or self.companion_candidate_executed
            or self.composed_candidate_executed
            or self.fresh_confirmation_executed
            or self.next_intervention_selected
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("design protocol cannot overclaim execution state")

        return self


def build_phase5_post_reject_intervention_design_protocol_v1() -> (
    Phase5PostRejectInterventionDesignProtocolV1
):
    return Phase5PostRejectInterventionDesignProtocolV1(
        resolver_experiment=ResolverCoverageExperimentV1(),
        companion_experiment=SourceCompanionRescueExperimentV1(),
        composition_gate=CompositionGateV1(),
    )
