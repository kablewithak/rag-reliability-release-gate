"""Preregister the bounded Phase 5 source-companion rescue experiment."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256

_DESIGN_PROTOCOL_SHA256 = (
    "f5a607f0051fe14b417ce41e6d01359d9c686e3f754711a917293369a22f44b8"
)
_DEVELOPMENT_REJECTION_SHA256 = (
    "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
)
_FAILURE_LOCALIZATION_SHA256 = (
    "5ac9f4b6f7e117a1adf699496ae4d8f3a4e0de7874d597f90c75d8a282cc61d6"
)
_A1_REJECTION_SHA256 = (
    "2ad66ffeb2b86c2348789cdf8c19d55492bd8a0001871e0a2566d5829e92de88"
)
_A2_REJECTION_SHA256 = (
    "3a113bc0ac59820e36dc46e9028ace60bdef5f307f6ba76633d36cf25e4f7d13"
)
_PROMOTED_RETRIEVAL_SHA256 = (
    "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
)
_RRF_INCUMBENT_SHA256 = (
    "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
)
_DEVELOPMENT_SHA256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SHA256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)
_POST_REJECT_CONFIRMATION_SHA256 = (
    "fde5b7005d9fa52dffff488b26224ebf90b7fcaaa6b443a55e136e01f397053c"
)
_POST_REJECT_CONFIRMATION_FREEZE_SHA256 = (
    "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"
)
_HELD_OUT_SHA256 = (
    "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
)
_CHUNK_MANIFEST_SHA256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

_TARGET_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)


class SourceCompanionRuntimeBoundaryV1(ContractModel):
    runtime_input_fields: tuple[
        Literal["query"],
        Literal["current_ranked_retrieval"],
        Literal["frozen_chunk_metadata"],
    ] = (
        "query",
        "current_ranked_retrieval",
        "frozen_chunk_metadata",
    )

    forbidden_evaluator_fields: tuple[
        Literal["required_source_ids"],
        Literal["required_evidence_ids"],
        Literal["gold_facts"],
        Literal["expected_response_mode"],
        Literal["gold_operation_id"],
        Literal["scoring_labels"],
        Literal["case_id_as_truth"],
        Literal["post_run_evaluator_annotations"],
    ] = (
        "required_source_ids",
        "required_evidence_ids",
        "gold_facts",
        "expected_response_mode",
        "gold_operation_id",
        "scoring_labels",
        "case_id_as_truth",
        "post_run_evaluator_annotations",
    )

    target_case_ids_available_to_candidate: Literal[False] = False
    development_gold_available_to_candidate: Literal[False] = False
    tuning_gold_available_to_candidate: Literal[False] = False
    post_reject_confirmation_content_allowed: Literal[False] = False
    held_out_content_allowed: Literal[False] = False


class SourceCompanionDerivationContractV1(ContractModel):
    base_ranking: Literal[
        "current_operation_aware_rrf_candidate"
    ] = "current_operation_aware_rrf_candidate"

    activation_resolution_states: tuple[
        Literal["ambiguous"],
        Literal["unresolved"],
    ] = ("ambiguous", "unresolved")

    anchor_window: Literal[5] = 5
    anchor_selection: Literal[
        "highest_ranked_current_authoritative_authored_chunk_in_anchor_window"
    ] = "highest_ranked_current_authoritative_authored_chunk_in_anchor_window"

    maximum_anchor_sources: Literal[1] = 1

    rescue_scope: Literal[
        "same_source_current_authoritative_authored_chunks_only"
    ] = "same_source_current_authoritative_authored_chunks_only"

    ordering: Literal[
        "prefix_before_anchor_then_anchor_then_same_source_siblings_in_existing_order_then_rest"
    ] = (
        "prefix_before_anchor_then_anchor_then_same_source_siblings_in_existing_order_then_rest"
    )

    resolved_operation_ranking_unchanged: Literal[True] = True
    scores_unchanged: Literal[True] = True
    candidate_count: Literal[1] = 1
    parameter_sweep_allowed: Literal[False] = False


class SourceCompanionCharacterizationGateV1(ContractModel):
    characterization_scope: tuple[
        Literal["spent_development_answerable_cases"],
        Literal["tuning_answerable_cases"],
    ] = (
        "spent_development_answerable_cases",
        "tuning_answerable_cases",
    )

    target_case_ids: tuple[NonEmptyStr, NonEmptyStr] = _TARGET_CASE_IDS
    targeted_cross_cutting_failure_cases_required_k20: Literal[2] = 2

    previously_passing_development_k20_regressions_allowed: Literal[0] = 0
    tuning_k20_regressions_allowed: Literal[0] = 0
    fallback_nondeterminism_allowed: Literal[0] = 0
    evaluator_leakage_tolerance: Literal[0] = 0
    provider_calls_allowed: Literal[0] = 0

    stop_after_single_bounded_characterization: Literal[True] = True
    automatic_composition_authorized: Literal[False] = False
    automatic_successor_experiment_authorized: Literal[False] = False
    baseline_readiness_review_required_after_companion: Literal[True] = True

    @model_validator(mode="after")
    def validate_target_scope(self) -> Self:
        if self.target_case_ids != _TARGET_CASE_IDS:
            raise ValueError("source-companion target case identities drifted")
        return self


class Phase5SourceCompanionRescueProtocolV1(ContractModel):
    protocol_version: Literal[
        "phase5-source-companion-rescue-protocol-v1"
    ] = "phase5-source-companion-rescue-protocol-v1"

    experiment_id: Literal[
        "phase5-authored-source-companion-rescue-v1"
    ] = "phase5-authored-source-companion-rescue-v1"

    parent_intervention_design_protocol_sha256: Sha256 = _DESIGN_PROTOCOL_SHA256
    parent_development_rejection_sha256: Sha256 = _DEVELOPMENT_REJECTION_SHA256
    parent_failure_localization_sha256: Sha256 = _FAILURE_LOCALIZATION_SHA256
    parent_a1_rejection_sha256: Sha256 = _A1_REJECTION_SHA256
    parent_a2_rejection_sha256: Sha256 = _A2_REJECTION_SHA256
    promoted_retrieval_evidence_sha256: Sha256 = _PROMOTED_RETRIEVAL_SHA256
    rrf_incumbent_sha256: Sha256 = _RRF_INCUMBENT_SHA256

    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SHA256
    post_reject_confirmation_suite_sha256: Sha256 = _POST_REJECT_CONFIRMATION_SHA256
    post_reject_confirmation_freeze_sha256: Sha256 = (
        _POST_REJECT_CONFIRMATION_FREEZE_SHA256
    )
    held_out_suite_sha256: Sha256 = _HELD_OUT_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    hypothesis: Literal[
        "multi_evidence_guidance_queries_need_bounded_same_source_companion_recall"
    ] = "multi_evidence_guidance_queries_need_bounded_same_source_companion_recall"

    runtime_boundary: SourceCompanionRuntimeBoundaryV1
    derivation: SourceCompanionDerivationContractV1
    gate: SourceCompanionCharacterizationGateV1

    candidate_execution_authorized_at_protocol_freeze: Literal[False] = False
    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False

    composition_authorized: Literal[False] = False
    composed_candidate_executed: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    chaos_executed: Literal[False] = False
    load_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol_state(self) -> Self:
        if (
            self.candidate_execution_authorized_at_protocol_freeze
            or self.candidate_implemented
            or self.candidate_executed
            or self.composition_authorized
            or self.composed_candidate_executed
            or self.post_reject_confirmation_inspected
            or self.post_reject_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.chaos_executed
            or self.load_executed
            or self.release_eligible
        ):
            raise ValueError(
                "source-companion preregistration cannot overclaim downstream state"
            )

        if self.gate.automatic_composition_authorized:
            raise ValueError(
                "source-companion protocol cannot auto-authorize composition"
            )

        if not self.gate.baseline_readiness_review_required_after_companion:
            raise ValueError(
                "source-companion experiment must terminate at review"
            )

        return self


def build_phase5_source_companion_rescue_protocol_v1(
) -> Phase5SourceCompanionRescueProtocolV1:
    return Phase5SourceCompanionRescueProtocolV1(
        runtime_boundary=SourceCompanionRuntimeBoundaryV1(),
        derivation=SourceCompanionDerivationContractV1(),
        gate=SourceCompanionCharacterizationGateV1(),
    )
