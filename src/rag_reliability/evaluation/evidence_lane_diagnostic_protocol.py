"""Preregister the Phase 5 evidence-lane retrieval diagnostic."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256

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
_COMPANION_REJECTION_SHA256 = (
    "4997bb745e018ed69b24daad0062ccdb00b218bf66eabf33c1610a39f94e8f1b"
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

_FAILED_DEVELOPMENT_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-repos-accept-invitation-current",
    "phase4-dev-repos-accept-invitation-success",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)

_AUTHORED_FAILURE_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)

_OPERATION_CORE_FAILURE_CASE_IDS = (
    "phase4-dev-repos-accept-invitation-current",
    "phase4-dev-repos-accept-invitation-success",
)


class EvidenceLaneDiagnosticBoundaryV1(ContractModel):
    diagnostic_query_inputs: tuple[
        Literal["query"],
        Literal["frozen_chunk_corpus"],
        Literal["frozen_chunk_metadata"],
    ] = (
        "query",
        "frozen_chunk_corpus",
        "frozen_chunk_metadata",
    )

    lanes_executed_for_every_query: tuple[
        Literal["authored_section"],
        Literal["openapi_operation_core"],
        Literal["openapi_component"],
    ] = (
        "authored_section",
        "openapi_operation_core",
        "openapi_component",
    )

    retrieval_algorithm: Literal[
        "existing_phase5_bm25_candidate_scoring"
    ] = "existing_phase5_bm25_candidate_scoring"

    lane_partition_field: Literal["chunk_kind"] = "chunk_kind"

    evaluator_fields_allowed_only_after_all_lane_rankings_exist: tuple[
        Literal["required_evidence_ids"],
        Literal["expected_response_mode"],
        Literal["case_id"],
        Literal["data_role"],
    ] = (
        "required_evidence_ids",
        "expected_response_mode",
        "case_id",
        "data_role",
    )

    evaluator_fields_passed_to_lane_retrievers: Literal[False] = False
    case_ids_used_for_runtime_routing: Literal[False] = False
    required_evidence_ids_used_for_runtime_routing: Literal[False] = False
    lane_selected_from_gold: Literal[False] = False

    development_gold_used_for_diagnostic_scoring_only: Literal[True] = True
    tuning_gold_used_for_diagnostic_scoring_only: Literal[True] = True

    post_reject_confirmation_content_allowed: Literal[False] = False
    held_out_content_allowed: Literal[False] = False


class EvidenceLaneDiagnosticMeasurementV1(ContractModel):
    characterization_scope: tuple[
        Literal["spent_development_answerable_cases"],
        Literal["tuning_answerable_cases"],
    ] = (
        "spent_development_answerable_cases",
        "tuning_answerable_cases",
    )

    compare_rank_surfaces: tuple[
        Literal["global_bm25"],
        Literal["global_operation_aware_rrf_incumbent"],
        Literal["native_lane_bm25"],
    ] = (
        "global_bm25",
        "global_operation_aware_rrf_incumbent",
        "native_lane_bm25",
    )

    required_per_evidence_measurements: tuple[
        Literal["chunk_kind"],
        Literal["global_bm25_rank"],
        Literal["global_incumbent_rank"],
        Literal["native_lane_bm25_rank"],
        Literal["global_to_native_lane_rank_delta"],
    ] = (
        "chunk_kind",
        "global_bm25_rank",
        "global_incumbent_rank",
        "native_lane_bm25_rank",
        "global_to_native_lane_rank_delta",
    )

    required_per_case_measurements: tuple[
        Literal["full_gold_global_incumbent_k20"],
        Literal["full_gold_native_lane_k20"],
    ] = (
        "full_gold_global_incumbent_k20",
        "full_gold_native_lane_k20",
    )

    deterministic_repeat_count: Literal[3] = 3
    native_lane_top_k_threshold: Literal[20] = 20

    candidate_ranking_emitted: Literal[False] = False
    lane_fusion_emitted: Literal[False] = False
    lane_quota_emitted: Literal[False] = False
    parameter_sweep_allowed: Literal[False] = False


class EvidenceLaneDiagnosticDecisionForkV1(ContractModel):
    failed_development_case_ids: tuple[
        NonEmptyStr,
        NonEmptyStr,
        NonEmptyStr,
        NonEmptyStr,
    ] = _FAILED_DEVELOPMENT_CASE_IDS

    authored_failure_case_ids: tuple[
        NonEmptyStr,
        NonEmptyStr,
    ] = _AUTHORED_FAILURE_CASE_IDS

    operation_core_failure_case_ids: tuple[
        NonEmptyStr,
        NonEmptyStr,
    ] = _OPERATION_CORE_FAILURE_CASE_IDS

    stratified_retrieval_candidate_hypothesis_supported_when: Literal[
        "all_four_failed_development_cases_are_full_gold_within_native_lane_top20"
    ] = (
        "all_four_failed_development_cases_are_full_gold_within_native_lane_top20"
    )

    authored_granularity_review_supported_when: Literal[
        "one_or_more_authored_failure_cases_remain_outside_native_lane_top20"
    ] = (
        "one_or_more_authored_failure_cases_remain_outside_native_lane_top20"
    )

    operation_representation_review_supported_when: Literal[
        "one_or_more_operation_core_failure_cases_remain_outside_native_lane_top20"
    ] = (
        "one_or_more_operation_core_failure_cases_remain_outside_native_lane_top20"
    )

    diagnostic_may_authorize_candidate_implementation: Literal[False] = False
    diagnostic_may_select_runtime_configuration: Literal[False] = False
    baseline_readiness_review_required_after_diagnostic: Literal[True] = True

    @model_validator(mode="after")
    def validate_failure_families(self) -> Self:
        if self.failed_development_case_ids != _FAILED_DEVELOPMENT_CASE_IDS:
            raise ValueError("failed DEVELOPMENT case identities drifted")

        if self.authored_failure_case_ids != _AUTHORED_FAILURE_CASE_IDS:
            raise ValueError("authored failure case identities drifted")

        if (
            self.operation_core_failure_case_ids
            != _OPERATION_CORE_FAILURE_CASE_IDS
        ):
            raise ValueError("operation-core failure case identities drifted")

        if set(self.authored_failure_case_ids) | set(
            self.operation_core_failure_case_ids
        ) != set(self.failed_development_case_ids):
            raise ValueError("diagnostic failure families do not reconcile")

        return self


class Phase5EvidenceLaneDiagnosticProtocolV1(ContractModel):
    protocol_version: Literal[
        "phase5-evidence-lane-diagnostic-protocol-v1"
    ] = "phase5-evidence-lane-diagnostic-protocol-v1"

    diagnostic_id: Literal[
        "phase5-evidence-lane-native-bm25-diagnostic-v1"
    ] = "phase5-evidence-lane-native-bm25-diagnostic-v1"

    hypothesis: Literal[
        "cross_evidence_class_competition_contributes_to_remaining_retrieval_misses"
    ] = (
        "cross_evidence_class_competition_contributes_to_remaining_retrieval_misses"
    )

    parent_development_rejection_sha256: Sha256 = (
        _DEVELOPMENT_REJECTION_SHA256
    )
    parent_failure_localization_sha256: Sha256 = (
        _FAILURE_LOCALIZATION_SHA256
    )
    parent_a1_rejection_sha256: Sha256 = _A1_REJECTION_SHA256
    parent_a2_rejection_sha256: Sha256 = _A2_REJECTION_SHA256
    parent_companion_rejection_sha256: Sha256 = (
        _COMPANION_REJECTION_SHA256
    )

    promoted_retrieval_evidence_sha256: Sha256 = _PROMOTED_RETRIEVAL_SHA256
    rrf_incumbent_sha256: Sha256 = _RRF_INCUMBENT_SHA256

    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SHA256
    post_reject_confirmation_suite_sha256: Sha256 = (
        _POST_REJECT_CONFIRMATION_SHA256
    )
    post_reject_confirmation_freeze_sha256: Sha256 = (
        _POST_REJECT_CONFIRMATION_FREEZE_SHA256
    )
    held_out_suite_sha256: Sha256 = _HELD_OUT_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    boundary: EvidenceLaneDiagnosticBoundaryV1
    measurement: EvidenceLaneDiagnosticMeasurementV1
    decision_fork: EvidenceLaneDiagnosticDecisionForkV1

    diagnostic_implemented: Literal[False] = False
    diagnostic_executed: Literal[False] = False

    runtime_retriever_changed: Literal[False] = False
    corpus_mutated: Literal[False] = False
    chunking_policy_changed: Literal[False] = False
    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False
    composition_authorized: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    chaos_executed: Literal[False] = False
    load_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol_state(self) -> Self:
        forbidden_claims = (
            self.diagnostic_implemented,
            self.diagnostic_executed,
            self.runtime_retriever_changed,
            self.corpus_mutated,
            self.chunking_policy_changed,
            self.candidate_implemented,
            self.candidate_executed,
            self.composition_authorized,
            self.post_reject_confirmation_inspected,
            self.post_reject_confirmation_executed,
            self.held_out_case_content_read,
            self.held_out_outcomes_exposed,
            self.provider_invoked,
            self.retrieval_configuration_selected,
            self.semantic_runtime_configuration_selected,
            self.semantic_runtime_configuration_frozen,
            self.baseline_execution_authorized,
            self.b0_executed,
            self.chaos_executed,
            self.load_executed,
            self.release_eligible,
        )

        if any(forbidden_claims):
            raise ValueError(
                "evidence-lane diagnostic protocol overclaims downstream state"
            )

        if self.decision_fork.diagnostic_may_authorize_candidate_implementation:
            raise ValueError(
                "diagnostic cannot directly authorize candidate implementation"
            )

        if not (
            self.decision_fork
            .baseline_readiness_review_required_after_diagnostic
        ):
            raise ValueError(
                "evidence-lane diagnostic must terminate at readiness review"
            )

        return self


def build_phase5_evidence_lane_diagnostic_protocol_v1(
) -> Phase5EvidenceLaneDiagnosticProtocolV1:
    return Phase5EvidenceLaneDiagnosticProtocolV1(
        boundary=EvidenceLaneDiagnosticBoundaryV1(),
        measurement=EvidenceLaneDiagnosticMeasurementV1(),
        decision_fork=EvidenceLaneDiagnosticDecisionForkV1(),
    )
