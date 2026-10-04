"""Freeze G5K runtime/control-lane qualification intent."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256

_POST_STRATIFIED_READINESS_SHA256: Sha256 = (
    "2b7c316d532f27c852706944121ffa8bd35a45f6a395dd148094c65f265c18e9"
)
_OPERATION_AWARE_RRF_SHA256: Sha256 = (
    "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
)
_BASELINE_PROTOCOL_FREEZE_SHA256: Sha256 = (
    "a92845181c9fcd3c69b84a191f1288f4391431cae8f82fe6c520b0b2a07bf434"
)
_MEASUREMENT_FREEZE_V2_SHA256: Sha256 = (
    "6249eb30e9c5986bba55b8d5adba22e62ae4df712c08b4e950b544962a19c932"
)
_PROVIDER_PROFILE_FREEZE_SHA256: Sha256 = (
    "2467146329874ddc02ba6740da90f52a0b53b5d945979fa3e7270c64021d445e"
)
_PROVIDER_LIVE_QUALIFICATION_SHA256: Sha256 = (
    "44b115c8ad7d079daa224485e0a9ec73cf6b9f59312cc7493aaad0075d156963"
)
_CHUNK_MANIFEST_SHA256: Sha256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

_EXPECTED_IMPLEMENTATION_CHANGES = (
    "runtime_operation_aware_rrf_retriever_v1",
    "pipeline_provider_timeout_terminalization",
    "pipeline_provider_malformed_response_terminalization",
)

_EXPECTED_RUNTIME_FIELDS = (
    "case_id",
    "query",
)

_EXPECTED_FORBIDDEN_EVALUATOR_FIELDS = (
    "required_source_ids",
    "required_evidence_ids",
    "gold_facts",
    "expected_response_mode_as_runtime_signal",
    "gold_operation_id",
    "scoring_labels",
    "held_out_outcomes",
    "post_run_evaluator_annotations",
)

_EXPECTED_CONTROL_CHECKS = (
    "selected_retriever_reference_parity_on_development_and_tuning_queries",
    "supported_answer_full_path",
    "source_policy_refusal_full_path",
    "unsupported_citation_safe_refusal",
    "provider_timeout_terminal_error",
    "provider_malformed_response_terminal_error",
)

_EXPECTED_LANE_A_CLAIMS = (
    "retrieval_behavior",
    "filtering_behavior",
    "context_selection_behavior",
    "citation_validation_behavior",
    "refusal_control_flow",
    "trace_accounting",
)

_EXPECTED_LANE_A_NONCLAIMS = (
    "context_sensitive_generation",
    "learned_model_reasoning_quality",
    "glm_5_2_robustness_under_load",
    "release_readiness",
)


class Phase5G5kRuntimeQualificationProtocolV1(ContractModel):
    """One bounded protocol for completing G5K without consuming B0."""

    protocol_version: Literal[
        "phase5-g5k-runtime-qualification-protocol-v1"
    ] = "phase5-g5k-runtime-qualification-protocol-v1"

    protocol_status: Literal["draft_unfrozen"] = "draft_unfrozen"

    post_stratified_readiness_sha256: Sha256 = _POST_STRATIFIED_READINESS_SHA256
    selected_retrieval_evidence_sha256: Sha256 = _OPERATION_AWARE_RRF_SHA256
    baseline_protocol_freeze_sha256: Sha256 = _BASELINE_PROTOCOL_FREEZE_SHA256
    measurement_freeze_v2_sha256: Sha256 = _MEASUREMENT_FREEZE_V2_SHA256
    semantic_provider_profile_freeze_sha256: Sha256 = _PROVIDER_PROFILE_FREEZE_SHA256
    semantic_provider_live_qualification_sha256: Sha256 = (
        _PROVIDER_LIVE_QUALIFICATION_SHA256
    )
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    selected_retrieval_id: Literal[
        "phase5-operation-aware-rrf-stable-partition-v1"
    ] = "phase5-operation-aware-rrf-stable-partition-v1"

    selected_retrieval_top_k: Literal[20] = 20
    source_policy_id: Literal["github-rest-current-v1"] = "github-rest-current-v1"
    reranker_enabled: Literal[False] = False
    context_builder_id: Literal["bounded-context-v1"] = "bounded-context-v1"
    context_budget_unit_id: Literal["characters"] = "characters"
    context_max_budget: Literal[69663] = 69663
    context_max_evidence_items: Literal[15] = 15

    lane_a_provider_mode: Literal[
        "query_keyed_scripted_response"
    ] = "query_keyed_scripted_response"
    lane_a_generation_is_context_sensitive: Literal[False] = False

    lane_b_provider_model_id: Literal["glm-5.2"] = "glm-5.2"
    lane_b_provider_adapter_id: Literal[
        "openai-compatible-json-v1"
    ] = "openai-compatible-json-v1"
    lane_b_live_qualification_satisfied: Literal[True] = True
    lane_b_new_live_calls_authorized: Literal[0] = 0

    authorized_implementation_changes: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=3, max_length=3)

    runtime_projection_fields: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=2, max_length=2)

    forbidden_runtime_evaluator_fields: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=8, max_length=8)

    required_control_checks: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=6, max_length=6)

    lane_a_supported_claim_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=6, max_length=6)

    lane_a_prohibited_claim_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=4, max_length=4)

    query_only_parity_scope: Literal[
        "development_and_tuning_case_id_query_projection"
    ] = "development_and_tuning_case_id_query_projection"

    retrieval_parity_mismatch_tolerance: Literal[0] = 0
    control_failure_tolerance: Literal[0] = 0
    evaluator_leakage_tolerance: Literal[0] = 0
    automatic_retry_tolerance: Literal[0] = 0

    measurement_metric_count: Literal[13] = 13
    scorer_applicability_matrix_required: Literal[True] = True

    protected_confirmation_authorized: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol(self) -> Self:
        expected_hashes = (
            _POST_STRATIFIED_READINESS_SHA256,
            _OPERATION_AWARE_RRF_SHA256,
            _BASELINE_PROTOCOL_FREEZE_SHA256,
            _MEASUREMENT_FREEZE_V2_SHA256,
            _PROVIDER_PROFILE_FREEZE_SHA256,
            _PROVIDER_LIVE_QUALIFICATION_SHA256,
            _CHUNK_MANIFEST_SHA256,
        )
        observed_hashes = (
            self.post_stratified_readiness_sha256,
            self.selected_retrieval_evidence_sha256,
            self.baseline_protocol_freeze_sha256,
            self.measurement_freeze_v2_sha256,
            self.semantic_provider_profile_freeze_sha256,
            self.semantic_provider_live_qualification_sha256,
            self.chunk_manifest_sha256,
        )
        if observed_hashes != expected_hashes:
            raise ValueError("G5K evidence custody drifted")

        if self.authorized_implementation_changes != _EXPECTED_IMPLEMENTATION_CHANGES:
            raise ValueError("G5K implementation scope drifted")

        if self.runtime_projection_fields != _EXPECTED_RUNTIME_FIELDS:
            raise ValueError("G5K runtime projection drifted")

        if self.forbidden_runtime_evaluator_fields != _EXPECTED_FORBIDDEN_EVALUATOR_FIELDS:
            raise ValueError("G5K evaluator boundary drifted")

        if self.required_control_checks != _EXPECTED_CONTROL_CHECKS:
            raise ValueError("G5K control-check set drifted")

        if self.lane_a_supported_claim_ids != _EXPECTED_LANE_A_CLAIMS:
            raise ValueError("Lane A supported claims drifted")

        if self.lane_a_prohibited_claim_ids != _EXPECTED_LANE_A_NONCLAIMS:
            raise ValueError("Lane A non-claims drifted")

        if not self.lane_b_live_qualification_satisfied:
            raise ValueError("Lane B must bind the accepted live qualification")

        if self.lane_b_new_live_calls_authorized != 0:
            raise ValueError("G5K integration protocol does not authorize new live calls")

        if (
            self.protected_confirmation_authorized
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("G5K protocol overclaims downstream state")

        return self


def build_phase5_g5k_runtime_qualification_protocol_v1(
) -> Phase5G5kRuntimeQualificationProtocolV1:
    return Phase5G5kRuntimeQualificationProtocolV1(
        authorized_implementation_changes=_EXPECTED_IMPLEMENTATION_CHANGES,
        runtime_projection_fields=_EXPECTED_RUNTIME_FIELDS,
        forbidden_runtime_evaluator_fields=_EXPECTED_FORBIDDEN_EVALUATOR_FIELDS,
        required_control_checks=_EXPECTED_CONTROL_CHECKS,
        lane_a_supported_claim_ids=_EXPECTED_LANE_A_CLAIMS,
        lane_a_prohibited_claim_ids=_EXPECTED_LANE_A_NONCLAIMS,
    )
