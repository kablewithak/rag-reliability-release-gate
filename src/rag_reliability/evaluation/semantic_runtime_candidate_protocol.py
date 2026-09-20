"""Freeze the Phase 5 semantic-runtime candidate qualification intent."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256

_PROMOTED_RETRIEVAL_SHA256 = "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
_SEMANTIC_ADEQUACY_SHA256 = "e38989477874a20382ba8b6d6bdec468f7b02f56a7c0a56059ad2fcea5e1141b"
_PROVIDER_PROFILE_SHA256 = "4239db3367ef962ccd4eff57cf4eb37fc770cda37f665e0bbbfdb1d0a7acf8e3"
_PROVIDER_FREEZE_SHA256 = "2467146329874ddc02ba6740da90f52a0b53b5d945979fa3e7270c64021d445e"
_BASELINE_FREEZE_SHA256 = "a92845181c9fcd3c69b84a191f1288f4391431cae8f82fe6c520b0b2a07bf434"
_DEVELOPMENT_SHA256 = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
_CHUNK_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"


class SemanticRuntimeCandidateContract(ContractModel):
    candidate_id: Literal["phase5-semantic-runtime-candidate-v1"] = (
        "phase5-semantic-runtime-candidate-v1"
    )

    retrieval_candidate_id: Literal["phase5-operation-aware-rrf-stable-partition-v1"] = (
        "phase5-operation-aware-rrf-stable-partition-v1"
    )

    retrieval_top_k: Literal[20] = 20
    source_policy_id: Literal["github-rest-current-v1"] = "github-rest-current-v1"
    reranker_enabled: Literal[False] = False

    context_builder_id: Literal["bounded-context-v1"] = "bounded-context-v1"
    context_budget_unit_id: Literal["characters"] = "characters"
    context_max_budget: Literal[69663] = 69663
    context_max_evidence_items: Literal[15] = 15

    provider_model_id: Literal["glm-5.2"] = "glm-5.2"
    provider_adapter_id: Literal["openai-compatible-json-v1"] = "openai-compatible-json-v1"
    provider_max_output_tokens: Literal[768] = 768
    provider_max_retries: Literal[0] = 0

    candidate_count: Literal[1] = 1
    parameter_sweep_used: Literal[False] = False
    development_tuning_authorized: Literal[False] = False


class DevelopmentConfirmationGate(ContractModel):
    development_case_count: Literal[24] = 24
    answerable_development_case_count: Literal[20] = 20
    refusal_development_case_count: Literal[4] = 4
    required_evidence_reference_count: Literal[25] = 25

    full_gold_answerable_cases_required: Literal[20] = 20
    micro_gold_recall_required: Literal["1.0"] = "1.0"

    maximum_raw_top_k_allowed: Literal[20] = 20
    maximum_eligible_items_allowed: Literal[15] = 15
    maximum_context_prefix_characters_allowed: Literal[69663] = 69663

    unretrievable_cases_allowed: Literal[0] = 0
    filter_ineligible_cases_allowed: Literal[0] = 0
    fallback_order_mismatch_tolerance: Literal[0] = 0
    nondeterministic_result_tolerance: Literal[0] = 0
    evaluator_leakage_tolerance: Literal[0] = 0

    failure_policy: Literal["stop_without_retuning"] = "stop_without_retuning"


class ProviderCapacityGate(ContractModel):
    exact_endpoint_capacity_live_confirmation_required: Literal[True] = True
    public_capacity_documentation_consistent: Literal[False] = False
    documentation_only_capacity_acceptance_allowed: Literal[False] = False

    active_provider_blocker_code: Literal["ModelArts.81111"] = "ModelArts.81111"

    live_capacity_probe_authorized_now: Literal[False] = False
    live_capacity_qualification_satisfied: Literal[False] = False

    required_live_probe_policy: Literal["single_exact_endpoint_probe_after_blocker_clearance"] = (
        "single_exact_endpoint_probe_after_blocker_clearance"
    )

    retry_or_workaround_authorized: Literal[False] = False


class Phase5SemanticRuntimeCandidateProtocolV1(ContractModel):
    protocol_version: Literal["phase5-semantic-runtime-candidate-protocol-v1"] = (
        "phase5-semantic-runtime-candidate-protocol-v1"
    )

    protocol_status: Literal["draft_unfrozen"] = "draft_unfrozen"

    promoted_retrieval_evidence_sha256: Sha256 = _PROMOTED_RETRIEVAL_SHA256
    semantic_runtime_adequacy_sha256: Sha256 = _SEMANTIC_ADEQUACY_SHA256
    semantic_provider_profile_sha256: Sha256 = _PROVIDER_PROFILE_SHA256
    semantic_provider_profile_freeze_sha256: Sha256 = _PROVIDER_FREEZE_SHA256
    baseline_protocol_freeze_sha256: Sha256 = _BASELINE_FREEZE_SHA256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    candidate: SemanticRuntimeCandidateContract
    development_confirmation: DevelopmentConfirmationGate
    provider_capacity: ProviderCapacityGate

    runtime_projection_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=2,
        max_length=2,
    )
    forbidden_runtime_evaluator_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=8,
        max_length=8,
    )

    development_gold_used_for_confirmation_only: Literal[True] = True
    development_gold_used_for_tuning: Literal[False] = False
    tuning_parameters_mutable_after_failure: Literal[False] = False

    runtime_retriever_integrated: Literal[False] = False
    runtime_configuration_materialized: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    provider_invoked: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        expected_hashes = (
            _PROMOTED_RETRIEVAL_SHA256,
            _SEMANTIC_ADEQUACY_SHA256,
            _PROVIDER_PROFILE_SHA256,
            _PROVIDER_FREEZE_SHA256,
            _BASELINE_FREEZE_SHA256,
            _DEVELOPMENT_SHA256,
            _CHUNK_MANIFEST_SHA256,
        )
        observed_hashes = (
            self.promoted_retrieval_evidence_sha256,
            self.semantic_runtime_adequacy_sha256,
            self.semantic_provider_profile_sha256,
            self.semantic_provider_profile_freeze_sha256,
            self.baseline_protocol_freeze_sha256,
            self.development_suite_sha256,
            self.chunk_manifest_sha256,
        )
        if observed_hashes != expected_hashes:
            raise ValueError("semantic-runtime evidence custody drifted")

        if self.runtime_projection_fields != ("case_id", "query"):
            raise ValueError("semantic-runtime runtime projection drifted")

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
        if self.forbidden_runtime_evaluator_fields != expected_forbidden:
            raise ValueError("semantic-runtime evaluator boundary drifted")

        if self.candidate.candidate_count != 1:
            raise ValueError("semantic-runtime qualification permits one candidate")

        if self.development_gold_used_for_tuning:
            raise ValueError("DEVELOPMENT gold cannot tune the candidate")

        if self.tuning_parameters_mutable_after_failure:
            raise ValueError("candidate values cannot move after DEVELOPMENT failure")

        if self.provider_capacity.live_capacity_probe_authorized_now:
            raise ValueError("provider capacity probe remains blocked by ModelArts.81111")

        if (
            self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
        ):
            raise ValueError("protocol cannot select or freeze semantic runtime configuration")

        if self.baseline_execution_authorized or self.b0_executed:
            raise ValueError("protocol cannot authorize or execute B0")

        return self


def build_phase5_semantic_runtime_candidate_protocol_v1() -> (
    Phase5SemanticRuntimeCandidateProtocolV1
):
    return Phase5SemanticRuntimeCandidateProtocolV1(
        candidate=SemanticRuntimeCandidateContract(),
        development_confirmation=DevelopmentConfirmationGate(),
        provider_capacity=ProviderCapacityGate(),
        runtime_projection_fields=("case_id", "query"),
        forbidden_runtime_evaluator_fields=(
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
