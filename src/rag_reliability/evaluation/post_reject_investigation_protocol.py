"""Phase 5 post-reject investigation and evidence-custody protocol."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256

_DEVELOPMENT_REJECTION_SHA256 = "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
_DEVELOPMENT_SUITE_SHA256 = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
_TUNING_SUITE_SHA256 = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
_HELD_OUT_SUITE_SHA256 = "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
_CHUNK_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"


class RejectedCandidateEvidenceContract(ContractModel):
    development_confirmation_sha256: Sha256 = _DEVELOPMENT_REJECTION_SHA256

    candidate_retrieval_top_k: Literal[20] = 20
    candidate_context_max_evidence_items: Literal[15] = 15
    candidate_context_max_budget: Literal[69663] = 69663

    answerable_case_count: Literal[20] = 20
    required_evidence_reference_count: Literal[25] = 25
    full_gold_case_count_at_k20: Literal[16] = 16
    retrieved_required_evidence_count_at_k20: Literal[21] = 21
    worst_required_raw_rank: Literal[49] = 49

    failure_specific_case_ids_opened_for_diagnosis: Literal[False] = False
    failure_specific_gold_opened_for_diagnosis: Literal[False] = False
    candidate_retuning_authorized: Literal[False] = False


class FreshConfirmationReservation(ContractModel):
    role_id: Literal["POST_REJECT_CONFIRMATION"] = "POST_REJECT_CONFIRMATION"
    suite_version: Literal["phase5-post-reject-confirmation-v1"] = (
        "phase5-post-reject-confirmation-v1"
    )

    corpus_boundary: Literal["frozen_phase3d_corpus_only"] = "frozen_phase3d_corpus_only"

    case_count: Literal[24] = 24
    cluster_count: Literal[12] = 12
    answerable_case_count: Literal[20] = 20
    refusal_case_count: Literal[4] = 4

    exact_query_reuse_from_development_allowed: Literal[False] = False
    exact_query_reuse_from_tuning_allowed: Literal[False] = False

    failure_specific_development_evidence_allowed_during_authoring: Literal[False] = False
    intervention_specific_behavior_allowed_during_authoring: Literal[False] = False

    authoring_basis: Literal["corpus_structure_source_family_and_scenario_coverage"] = (
        "corpus_structure_source_family_and_scenario_coverage"
    )

    must_be_materialized_before_failure_localization: Literal[True] = True
    must_be_frozen_before_failure_localization: Literal[True] = True

    evaluator_runtime_projection: Literal["case_id_and_query_only"] = "case_id_and_query_only"

    promotion_use: Literal["independent_confirmation_for_next_semantic_runtime_candidate"] = (
        "independent_confirmation_for_next_semantic_runtime_candidate"
    )


class DevelopmentReuseBoundary(ContractModel):
    state_at_protocol_freeze: Literal[
        "independent_confirmation_complete_rejected_not_failure_localized"
    ] = "independent_confirmation_complete_rejected_not_failure_localized"

    state_after_failure_localization_starts: Literal[
        "diagnostic_only_spent_for_future_confirmation"
    ] = "diagnostic_only_spent_for_future_confirmation"

    may_inform_failure_taxonomy_after_reservation: Literal[True] = True
    may_inform_next_intervention_after_reservation: Literal[True] = True

    may_confirm_intervention_informed_by_its_failures: Literal[False] = False
    may_be_relabelled_as_independent_later: Literal[False] = False


class HeldOutBoundary(ContractModel):
    suite_sha256: Sha256 = _HELD_OUT_SUITE_SHA256
    outcomes_exposed: Literal[False] = False
    case_content_allowed_for_post_reject_authoring: Literal[False] = False
    case_content_allowed_for_failure_localization: Literal[False] = False
    intervention_design_allowed_to_use_held_out: Literal[False] = False

    may_execute_before_semantic_runtime_freeze: Literal[False] = False
    may_execute_before_provider_capacity_gate: Literal[False] = False


class FailureLocalizationBoundary(ContractModel):
    localization_authorized_at_protocol_freeze: Literal[False] = False

    activation_condition: Literal["fresh_confirmation_suite_materialized_and_frozen"] = (
        "fresh_confirmation_suite_materialized_and_frozen"
    )

    scope_after_activation: Literal[
        "development_rejection_cases_and_candidate_trace_evidence_only"
    ] = "development_rejection_cases_and_candidate_trace_evidence_only"

    permitted_questions: tuple[str, ...] = (
        "which_required_evidence_missed_top20",
        "whether_misses_are_resolved_or_fallback_cases",
        "whether_gold_lineage_matches_resolved_operation",
        "lexical_vs_bm25_vs_rrf_rank_contribution",
        "source_family_and_chunk_kind_pattern",
        "whether_failure_is_retrieval_filter_or_context_primary",
    )

    parameter_sweep_during_localization_allowed: Literal[False] = False
    new_candidate_execution_during_localization_allowed: Literal[False] = False
    provider_invocation_allowed: Literal[False] = False


class Phase5PostRejectInvestigationProtocolV1(ContractModel):
    protocol_version: Literal["phase5-post-reject-investigation-protocol-v1"] = (
        "phase5-post-reject-investigation-protocol-v1"
    )

    protocol_status: Literal["draft_unfrozen"] = "draft_unfrozen"

    development_suite_sha256: Sha256 = _DEVELOPMENT_SUITE_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SUITE_SHA256
    held_out_suite_sha256: Sha256 = _HELD_OUT_SUITE_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    rejected_candidate: RejectedCandidateEvidenceContract
    fresh_confirmation: FreshConfirmationReservation
    development_reuse: DevelopmentReuseBoundary
    held_out: HeldOutBoundary
    failure_localization: FailureLocalizationBoundary

    fresh_confirmation_materialized: Literal[False] = False
    fresh_confirmation_frozen: Literal[False] = False
    failure_localization_started: Literal[False] = False
    development_spent_for_future_confirmation: Literal[False] = False

    next_intervention_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    provider_invoked: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        expected_hashes = (
            _DEVELOPMENT_SUITE_SHA256,
            _TUNING_SUITE_SHA256,
            _HELD_OUT_SUITE_SHA256,
            _CHUNK_MANIFEST_SHA256,
        )
        observed_hashes = (
            self.development_suite_sha256,
            self.tuning_suite_sha256,
            self.held_out_suite_sha256,
            self.chunk_manifest_sha256,
        )
        if observed_hashes != expected_hashes:
            raise ValueError("post-reject evidence custody drifted")

        reservation = self.fresh_confirmation
        if (
            reservation.answerable_case_count + reservation.refusal_case_count
            != reservation.case_count
        ):
            raise ValueError("fresh confirmation case counts do not reconcile")

        if self.failure_localization_started:
            if not (self.fresh_confirmation_materialized and self.fresh_confirmation_frozen):
                raise ValueError("failure localization requires frozen fresh confirmation")
            if not self.development_spent_for_future_confirmation:
                raise ValueError("localized DEVELOPMENT must be marked spent")

        if self.development_spent_for_future_confirmation:
            if not self.failure_localization_started:
                raise ValueError("DEVELOPMENT cannot be spent before localization starts")

        if self.held_out.outcomes_exposed:
            raise ValueError("HELD_OUT outcomes must remain sealed")

        if (
            self.next_intervention_selected
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.provider_invoked
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("protocol freeze cannot overclaim later state")

        return self


def build_phase5_post_reject_investigation_protocol_v1() -> Phase5PostRejectInvestigationProtocolV1:
    return Phase5PostRejectInvestigationProtocolV1(
        rejected_candidate=RejectedCandidateEvidenceContract(),
        fresh_confirmation=FreshConfirmationReservation(),
        development_reuse=DevelopmentReuseBoundary(),
        held_out=HeldOutBoundary(),
        failure_localization=FailureLocalizationBoundary(),
    )
