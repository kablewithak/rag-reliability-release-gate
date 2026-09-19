"""Freeze the single Phase 5 operation-aware RRF intervention intent.

This protocol authorizes one offline TUNING-only ranking experiment. It does
not mutate the runtime retriever, invoke a provider, expose HELD_OUT outcomes,
authorize B0, or freeze a semantic runtime configuration.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr

_RRF_INCUMBENT_SHA256: Literal[
    "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
] = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
_RESOLVER_CHARACTERIZATION_SHA256: Literal[
    "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
] = "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
_RESOLVER_PROTOCOL_SHA256: Literal[
    "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
] = "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
_RESOLVER_FREEZE_SHA256: Literal[
    "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"
] = "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"
_SEMANTIC_ADEQUACY_SHA256: Literal[
    "e38989477874a20382ba8b6d6bdec468f7b02f56a7c0a56059ad2fcea5e1141b"
] = "e38989477874a20382ba8b6d6bdec468f7b02f56a7c0a56059ad2fcea5e1141b"
_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
_TUNING_SUITE_SHA256: Literal[
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
] = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"


class OperationAwareRrfCandidateContract(ContractModel):
    """Exactly one structural candidate with no score or parameter tuning."""

    candidate_id: Literal["phase5-operation-aware-rrf-stable-partition-v1"] = (
        "phase5-operation-aware-rrf-stable-partition-v1"
    )
    base_ranking: Literal["phase5-rrf-hybrid-candidate-v1"] = "phase5-rrf-hybrid-candidate-v1"
    intervention: Literal["stable_partition_by_exact_resolved_operation_lineage"] = (
        "stable_partition_by_exact_resolved_operation_lineage"
    )
    resolved_behavior: Literal["operation_linked_first_preserve_partition_relative_order"] = (
        "operation_linked_first_preserve_partition_relative_order"
    )
    ambiguous_behavior: Literal["preserve_generic_rrf_exactly"] = "preserve_generic_rrf_exactly"
    unresolved_behavior: Literal["preserve_generic_rrf_exactly"] = "preserve_generic_rrf_exactly"
    score_values_changed: Literal[False] = False
    base_rrf_configuration_changed: Literal[False] = False
    candidate_count: Literal[1] = 1
    parameter_sweep_used: Literal[False] = False
    tuning_parameter_optimization_used: Literal[False] = False


class OperationAwareRrfPromotionGate(ContractModel):
    """Predeclared retrieval-candidate gate, not a semantic-runtime gate."""

    answerable_tuning_case_count: Literal[15] = 15
    required_evidence_reference_count: Literal[18] = 18
    full_gold_cases_at_k20_required: Literal[15] = 15
    micro_gold_recall_at_k20_required: Literal["1.0"] = "1.0"
    maximum_raw_top_k_allowed: Literal[20] = 20
    maximum_eligible_items_allowed: Literal[20] = 20
    maximum_context_prefix_characters_allowed: Literal[102463] = 102463
    context_limit_semantics: Literal[
        "not_worse_than_measured_rrf_incumbent_not_runtime_capacity"
    ] = "not_worse_than_measured_rrf_incumbent_not_runtime_capacity"
    unretrievable_cases_allowed: Literal[0] = 0
    filter_ineligible_cases_allowed: Literal[0] = 0
    full_gold_k20_regressions_allowed: Literal[0] = 0
    evaluator_leakage_tolerance: Literal[0] = 0
    fallback_order_mismatch_tolerance: Literal[0] = 0
    nondeterministic_result_tolerance: Literal[0] = 0
    semantic_runtime_capacity_gate_satisfied: Literal[False] = False
    semantic_runtime_promotion_authorized: Literal[False] = False


class Phase5OperationAwareRrfProtocolV1(ContractModel):
    """Frozen intent for the single structural operation-aware RRF candidate."""

    protocol_version: Literal["phase5-operation-aware-rrf-protocol-v1"] = (
        "phase5-operation-aware-rrf-protocol-v1"
    )
    protocol_status: Literal["draft_unfrozen"] = "draft_unfrozen"
    question: Literal[
        "Can exact runtime operation lineage improve the measured RRF ranking "
        "without evaluator leakage or collateral k20 regressions?"
    ] = (
        "Can exact runtime operation lineage improve the measured RRF ranking "
        "without evaluator leakage or collateral k20 regressions?"
    )
    rrf_incumbent_sha256: Literal[
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    ] = _RRF_INCUMBENT_SHA256
    resolver_characterization_sha256: Literal[
        "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
    ] = _RESOLVER_CHARACTERIZATION_SHA256
    resolver_protocol_sha256: Literal[
        "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
    ] = _RESOLVER_PROTOCOL_SHA256
    resolver_freeze_receipt_sha256: Literal[
        "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"
    ] = _RESOLVER_FREEZE_SHA256
    semantic_runtime_adequacy_sha256: Literal[
        "e38989477874a20382ba8b6d6bdec468f7b02f56a7c0a56059ad2fcea5e1141b"
    ] = _SEMANTIC_ADEQUACY_SHA256
    chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = _CHUNK_MANIFEST_SHA256
    tuning_suite_sha256: Literal[
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
    ] = _TUNING_SUITE_SHA256
    candidate: OperationAwareRrfCandidateContract
    promotion_gate: OperationAwareRrfPromotionGate
    allowed_runtime_signal_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=2,
        max_length=2,
    )
    forbidden_evaluator_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=8,
        max_length=8,
    )
    evidence_scope: Literal["tuning_answerable_offline_only"] = "tuning_answerable_offline_only"
    provider_invoked: Literal[False] = False
    development_gold_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False
    stop_after_candidate_failure: Literal[True] = True
    nearby_candidate_execution_authorized_after_failure: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        expected_allowed = (
            "query",
            "phase3d_chunk.linked_operation_ids",
        )
        if self.allowed_runtime_signal_fields != expected_allowed:
            raise ValueError("operation-aware runtime signal boundary drifted")

        expected_forbidden = (
            "required_source_ids",
            "required_evidence_ids",
            "gold_facts",
            "expected_response_mode_as_runtime_signal",
            "gold_operation_id",
            "scoring_labels",
            "held_out_outcomes",
            "post_run_evaluator_annotations",
        )
        if self.forbidden_evaluator_fields != expected_forbidden:
            raise ValueError("operation-aware evaluator boundary drifted")

        if self.candidate.candidate_count != 1:
            raise ValueError("Slice 2 permits exactly one candidate")

        if self.promotion_gate.semantic_runtime_promotion_authorized:
            raise ValueError(
                "retrieval candidate protocol cannot authorize semantic runtime promotion"
            )

        return self


def build_phase5_operation_aware_rrf_protocol_v1() -> Phase5OperationAwareRrfProtocolV1:
    """Build the single-candidate Slice 2 protocol before experiment execution."""

    return Phase5OperationAwareRrfProtocolV1(
        candidate=OperationAwareRrfCandidateContract(),
        promotion_gate=OperationAwareRrfPromotionGate(),
        allowed_runtime_signal_fields=(
            "query",
            "phase3d_chunk.linked_operation_ids",
        ),
        forbidden_evaluator_fields=(
            "required_source_ids",
            "required_evidence_ids",
            "gold_facts",
            "expected_response_mode_as_runtime_signal",
            "gold_operation_id",
            "scoring_labels",
            "held_out_outcomes",
            "post_run_evaluator_annotations",
        ),
    )
