"""Freeze the single Phase 5 incumbent-preserving stratified retrieval intent.

This protocol authorizes one DEVELOPMENT+TUNING offline characterization of a
runtime-safe retrieval candidate. It does not inspect protected cases, invoke a
provider, execute B0, or select/freeze a semantic runtime configuration.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256

_EVIDENCE_LANE_DIAGNOSTIC_SHA256: Sha256 = (
    "bd3aa5893b7447fb91cf586dd2f2568e18fe6915d162bf2f04e43fad2c433b8e"
)
_EVIDENCE_LANE_PROTOCOL_SHA256: Sha256 = (
    "b7b82810e224af452eaa9d8c23b4db8330857c2b1acc01eedbecc429bc458992"
)
_EVIDENCE_LANE_FREEZE_SHA256: Sha256 = (
    "80a1fd5fa970d3bd1d8a8ada8d77eed1f25349c95769d7f1932d81d47c237081"
)
_DEVELOPMENT_REJECTION_SHA256: Sha256 = (
    "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
)
_PROMOTED_RETRIEVAL_SHA256: Sha256 = (
    "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
)
_RRF_INCUMBENT_SHA256: Sha256 = (
    "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
)
_CHUNK_MANIFEST_SHA256: Sha256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)
_DEVELOPMENT_SHA256: Sha256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SHA256: Sha256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)
_POST_REJECT_CONFIRMATION_SHA256: Sha256 = (
    "fde5b7005d9fa52dffff488b26224ebf90b7fcaaa6b443a55e136e01f397053c"
)
_POST_REJECT_CONFIRMATION_FREEZE_SHA256: Sha256 = (
    "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"
)
_HELD_OUT_SHA256: Sha256 = (
    "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
)

_FAILED_DEVELOPMENT_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-repos-accept-invitation-current",
    "phase4-dev-repos-accept-invitation-success",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)


class StratifiedRetrievalCandidateContractV1(ContractModel):
    """Exactly one rank-based candidate with no case-specific routing."""

    candidate_id: Literal[
        "phase5-incumbent-preserving-stratified-rrf-v1"
    ] = "phase5-incumbent-preserving-stratified-rrf-v1"

    base_ranking: Literal[
        "global_operation_aware_rrf_incumbent"
    ] = "global_operation_aware_rrf_incumbent"

    lane_scoring: Literal[
        "existing_phase5_bm25_candidate_scoring"
    ] = "existing_phase5_bm25_candidate_scoring"

    lanes: tuple[
        Literal["authored_section"],
        Literal["openapi_operation_core"],
        Literal["openapi_component"],
    ] = (
        "authored_section",
        "openapi_operation_core",
        "openapi_component",
    )

    lane_partition_field: Literal["chunk_kind"] = "chunk_kind"
    lanes_executed_for_every_query: Literal[True] = True

    merge_method: Literal[
        "equal_weight_rrf_incumbent_rank_plus_native_lane_rank"
    ] = "equal_weight_rrf_incumbent_rank_plus_native_lane_rank"

    fusion_constant: Literal[60] = 60
    incumbent_rank_weight: Literal[1] = 1
    native_lane_rank_weight: Literal[1] = 1

    lane_premerge_truncation: Literal[
        "none_all_nonzero_ranked_items_eligible_for_merge"
    ] = "none_all_nonzero_ranked_items_eligible_for_merge"

    merge_population: Literal[
        "union_of_incumbent_and_all_native_lane_rankings"
    ] = "union_of_incumbent_and_all_native_lane_rankings"

    missing_surface_behavior: Literal[
        "missing_rank_contributes_zero_to_rrf_score"
    ] = "missing_rank_contributes_zero_to_rrf_score"

    deduplication_key: Literal["evidence_id"] = "evidence_id"
    stable_tie_breaker: Literal["evidence_id_ascending"] = "evidence_id_ascending"

    empty_lane_behavior: Literal[
        "empty_lane_contributes_no_items_other_surfaces_continue"
    ] = "empty_lane_contributes_no_items_other_surfaces_continue"

    post_merge_operation_partition: Literal[False] = False
    operation_awareness_source: Literal[
        "already_encoded_in_incumbent_rank_surface"
    ] = "already_encoded_in_incumbent_rank_surface"

    raw_cross_lane_score_comparison_used: Literal[False] = False
    fixed_lane_quota_used: Literal[False] = False
    round_robin_merge_used: Literal[False] = False

    final_retrieval_top_k: Literal[20] = 20
    context_max_evidence_items: Literal[15] = 15
    context_max_budget_characters: Literal[69663] = 69663

    corpus_changed: Literal[False] = False
    chunking_changed: Literal[False] = False
    source_policy_changed: Literal[False] = False
    context_policy_changed: Literal[False] = False

    candidate_count: Literal[1] = 1
    parameter_sweep_used: Literal[False] = False
    tuning_parameter_optimization_used: Literal[False] = False


class StratifiedRetrievalPromotionGateV1(ContractModel):
    """Predeclared retrieval gate for DEVELOPMENT+TUNING characterization."""

    development_answerable_case_count: Literal[20] = 20
    tuning_answerable_case_count: Literal[15] = 15
    total_answerable_case_count: Literal[35] = 35
    required_evidence_reference_count: Literal[43] = 43

    failed_development_case_count: Literal[4] = 4
    failed_development_cases_required_recovered: Literal[4] = 4

    full_gold_cases_at_k20_required: Literal[35] = 35
    micro_gold_recall_at_k20_required: Literal["1.0"] = "1.0"

    maximum_raw_top_k_allowed: Literal[20] = 20
    maximum_eligible_items_allowed: Literal[15] = 15
    maximum_context_prefix_characters_allowed: Literal[69663] = 69663

    previously_passing_full_gold_k20_regressions_allowed: Literal[0] = 0
    source_filter_regressions_allowed: Literal[0] = 0
    context_inclusion_regressions_allowed: Literal[0] = 0
    refusal_or_fallback_regressions_allowed: Literal[0] = 0

    evaluator_leakage_tolerance: Literal[0] = 0
    nondeterministic_result_tolerance: Literal[0] = 0

    deterministic_repeat_count: Literal[3] = 3
    provider_calls_allowed: Literal[0] = 0

    protected_confirmation_authorized_by_this_gate: Literal[False] = False
    baseline_execution_authorized_by_this_gate: Literal[False] = False
    semantic_runtime_promotion_authorized: Literal[False] = False


class Phase5StratifiedRetrievalCandidateProtocolV1(ContractModel):
    """Frozen intent for one incumbent-preserving stratified retrieval candidate."""

    protocol_version: Literal[
        "phase5-stratified-retrieval-candidate-protocol-v1"
    ] = "phase5-stratified-retrieval-candidate-protocol-v1"

    protocol_status: Literal["draft_unfrozen"] = "draft_unfrozen"

    question: Literal[
        "Can deterministic native-lane BM25 evidence preservation recover all "
        "four remaining DEVELOPMENT retrieval failures when fused with the "
        "operation-aware incumbent, without collateral DEVELOPMENT or TUNING "
        "regressions, evaluator leakage, or context-budget regressions?"
    ] = (
        "Can deterministic native-lane BM25 evidence preservation recover all "
        "four remaining DEVELOPMENT retrieval failures when fused with the "
        "operation-aware incumbent, without collateral DEVELOPMENT or TUNING "
        "regressions, evaluator leakage, or context-budget regressions?"
    )

    evidence_lane_diagnostic_sha256: Sha256 = _EVIDENCE_LANE_DIAGNOSTIC_SHA256
    evidence_lane_protocol_sha256: Sha256 = _EVIDENCE_LANE_PROTOCOL_SHA256
    evidence_lane_protocol_freeze_sha256: Sha256 = _EVIDENCE_LANE_FREEZE_SHA256
    development_rejection_sha256: Sha256 = _DEVELOPMENT_REJECTION_SHA256
    promoted_retrieval_evidence_sha256: Sha256 = _PROMOTED_RETRIEVAL_SHA256
    rrf_incumbent_sha256: Sha256 = _RRF_INCUMBENT_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SHA256
    post_reject_confirmation_suite_sha256: Sha256 = _POST_REJECT_CONFIRMATION_SHA256
    post_reject_confirmation_freeze_sha256: Sha256 = (
        _POST_REJECT_CONFIRMATION_FREEZE_SHA256
    )
    held_out_suite_sha256: Sha256 = _HELD_OUT_SHA256

    candidate: StratifiedRetrievalCandidateContractV1
    promotion_gate: StratifiedRetrievalPromotionGateV1

    failed_development_case_ids: tuple[
        NonEmptyStr,
        NonEmptyStr,
        NonEmptyStr,
        NonEmptyStr,
    ] = _FAILED_DEVELOPMENT_CASE_IDS

    allowed_runtime_signal_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=4,
        max_length=4,
    )
    forbidden_evaluator_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=10,
        max_length=10,
    )

    evidence_scope: Literal[
        "spent_development_answerable_plus_tuning_answerable_offline_only"
    ] = "spent_development_answerable_plus_tuning_answerable_offline_only"

    development_gold_used_for_scoring_only: Literal[True] = True
    tuning_gold_used_for_scoring_only: Literal[True] = True

    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False

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

    stop_after_candidate_failure: Literal[True] = True
    nearby_candidate_execution_authorized_after_failure: Literal[False] = False
    baseline_readiness_review_required_after_result: Literal[True] = True

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        expected_allowed = (
            "query",
            "frozen_chunk_corpus",
            "phase3d_chunk.chunk_kind",
            "phase3d_chunk.linked_operation_ids",
        )
        if self.allowed_runtime_signal_fields != expected_allowed:
            raise ValueError("stratified candidate runtime signal boundary drifted")

        expected_forbidden = (
            "required_source_ids",
            "required_evidence_ids",
            "gold_facts",
            "expected_response_mode_as_runtime_signal",
            "case_id_as_runtime_signal",
            "data_role_as_runtime_signal",
            "gold_operation_id",
            "scoring_labels",
            "held_out_outcomes",
            "post_run_evaluator_annotations",
        )
        if self.forbidden_evaluator_fields != expected_forbidden:
            raise ValueError("stratified candidate evaluator boundary drifted")

        if self.failed_development_case_ids != _FAILED_DEVELOPMENT_CASE_IDS:
            raise ValueError("stratified candidate failed-case identities drifted")

        if self.candidate.candidate_count != 1:
            raise ValueError("stratified protocol permits exactly one candidate")

        if self.candidate.post_merge_operation_partition:
            raise ValueError(
                "operation-aware ordering must enter through the frozen incumbent only"
            )

        if (
            self.candidate.raw_cross_lane_score_comparison_used
            or self.candidate.fixed_lane_quota_used
            or self.candidate.round_robin_merge_used
        ):
            raise ValueError("stratified candidate merge semantics drifted")

        if self.promotion_gate.semantic_runtime_promotion_authorized:
            raise ValueError(
                "retrieval candidate protocol cannot authorize semantic runtime promotion"
            )

        if self.promotion_gate.protected_confirmation_authorized_by_this_gate:
            raise ValueError(
                "retrieval candidate protocol cannot authorize protected confirmation"
            )

        if self.promotion_gate.baseline_execution_authorized_by_this_gate:
            raise ValueError(
                "retrieval candidate protocol cannot authorize B0"
            )

        if not self.baseline_readiness_review_required_after_result:
            raise ValueError(
                "candidate result must terminate at baseline readiness review"
            )

        return self


def build_phase5_stratified_retrieval_candidate_protocol_v1(
) -> Phase5StratifiedRetrievalCandidateProtocolV1:
    """Build the single G5G candidate protocol before implementation/execution."""

    return Phase5StratifiedRetrievalCandidateProtocolV1(
        candidate=StratifiedRetrievalCandidateContractV1(),
        promotion_gate=StratifiedRetrievalPromotionGateV1(),
        allowed_runtime_signal_fields=(
            "query",
            "frozen_chunk_corpus",
            "phase3d_chunk.chunk_kind",
            "phase3d_chunk.linked_operation_ids",
        ),
        forbidden_evaluator_fields=(
            "required_source_ids",
            "required_evidence_ids",
            "gold_facts",
            "expected_response_mode_as_runtime_signal",
            "case_id_as_runtime_signal",
            "data_role_as_runtime_signal",
            "gold_operation_id",
            "scoring_labels",
            "held_out_outcomes",
            "post_run_evaluator_annotations",
        ),
    )
