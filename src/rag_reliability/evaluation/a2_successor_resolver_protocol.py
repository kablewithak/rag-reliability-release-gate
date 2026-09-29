"""Preregister the bounded Phase 5 A2 successor resolver experiment."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256

_A1_REJECTION_SHA256 = "2ad66ffeb2b86c2348789cdf8c19d55492bd8a0001871e0a2566d5829e92de88"
_INTERVENTION_DESIGN_PROTOCOL_SHA256 = (
    "f5a607f0051fe14b417ce41e6d01359d9c686e3f754711a917293369a22f44b8"
)
_INTERVENTION_DESIGN_FREEZE_SHA256 = (
    "5596e5f561f5bf19e2583666e9260feaa3ed00eef4a9ca5b2937042c318c2322"
)
_RESOLVER_CHARACTERIZATION_SHA256 = (
    "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
)
_CHUNK_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
_DEVELOPMENT_SHA256 = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
_TUNING_SHA256 = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
_POST_REJECT_CONFIRMATION_SHA256 = (
    "fde5b7005d9fa52dffff488b26224ebf90b7fcaaa6b443a55e136e01f397053c"
)
_POST_REJECT_CONFIRMATION_FREEZE_SHA256 = (
    "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"
)
_HELD_OUT_SHA256 = "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"


class A2RuntimeEvidenceContractV1(ContractModel):
    runtime_input_fields: tuple[
        Literal["query"],
        Literal["runtime_operation_catalog"],
    ] = ("query", "runtime_operation_catalog")

    allowed_catalog_fields: tuple[
        Literal["operation_id"],
        Literal["path"],
        Literal["method"],
        Literal["summary"],
        Literal["semantic_family"],
    ] = (
        "operation_id",
        "path",
        "method",
        "summary",
        "semantic_family",
    )

    forbidden_evaluator_fields: tuple[
        Literal["gold_operation_id"],
        Literal["required_evidence_ids"],
        Literal["required_source_ids"],
        Literal["expected_answer"],
        Literal["case_role_as_truth"],
        Literal["scoring_labels"],
    ] = (
        "gold_operation_id",
        "required_evidence_ids",
        "required_source_ids",
        "expected_answer",
        "case_role_as_truth",
        "scoring_labels",
    )

    post_reject_confirmation_content_allowed: Literal[False] = False
    held_out_content_allowed: Literal[False] = False
    query_specific_exceptions_allowed: Literal[False] = False
    hard_coded_invitation_target_allowed: Literal[False] = False
    gold_operation_ids_allowed: Literal[False] = False


class A2DerivationContractV1(ContractModel):
    runtime_catalog_source: Literal[
        "frozen_phase3d_current_authoritative_openapi_operation_core_chunks"
    ] = "frozen_phase3d_current_authoritative_openapi_operation_core_chunks"

    namespace_derivation: Literal["operation_id_prefix_before_slash"] = (
        "operation_id_prefix_before_slash"
    )

    action_derivation: Literal[
        "first_normalized_operation_token_after_namespace_from_runtime_catalog"
    ] = "first_normalized_operation_token_after_namespace_from_runtime_catalog"

    object_subresource_derivation: Literal[
        "remaining_normalized_operation_id_tokens_after_action_plus_literal_path_segments"
    ] = "remaining_normalized_operation_id_tokens_after_action_plus_literal_path_segments"

    path_parameter_placeholders_contribute_object_evidence: Literal[False] = False

    action_morphology: Literal["reuse_a1_catalog_action_inflection_normalization"] = (
        "reuse_a1_catalog_action_inflection_normalization"
    )

    object_subresource_normalization: Literal[
        "lowercase_separator_folding_without_semantic_synonym_expansion"
    ] = "lowercase_separator_folding_without_semantic_synonym_expansion"

    exact_operation_match_preserved: Literal[True] = True
    method_path_match_preserved: Literal[True] = True
    full_signature_match_preserved: Literal[True] = True

    activation_states: tuple[
        Literal["ambiguous"],
        Literal["unresolved"],
    ] = ("ambiguous", "unresolved")

    already_resolved_baseline_result_preserved: Literal[True] = True

    partial_resolution_requires_namespace_evidence: Literal[True] = True
    partial_resolution_requires_action_evidence: Literal[True] = True
    partial_resolution_requires_object_or_subresource_evidence: Literal[True] = True

    unique_supported_operation_required_for_resolution: Literal[True] = True
    multiple_supported_operations_result: Literal["ambiguous"] = "ambiguous"
    zero_supported_operations_result: Literal["unresolved"] = "unresolved"
    tie_break_by_rank_allowed: Literal[False] = False


class A2CharacterizationGateV1(ContractModel):
    characterization_scope: tuple[
        Literal["existing_resolver_fixed_fixtures"],
        Literal["spent_development_answerable_cases"],
    ] = (
        "existing_resolver_fixed_fixtures",
        "spent_development_answerable_cases",
    )

    fixed_fixture_expectation_mismatches_allowed: Literal[0] = 0
    fixed_fixture_false_confident_resolutions_allowed: Literal[0] = 0
    fixed_fixture_nondeterministic_resolutions_allowed: Literal[0] = 0

    invitation_target_case_count: Literal[2] = 2
    invitation_target_cases_required_correctly_resolved: Literal[2] = 2

    development_false_confident_resolutions_allowed: Literal[0] = 0
    development_nondeterministic_resolutions_allowed: Literal[0] = 0

    provider_calls_allowed: Literal[0] = 0
    parameter_sweep_allowed: Literal[False] = False

    run_validity_states: tuple[
        Literal["VALID"],
        Literal["INVALID"],
    ] = ("VALID", "INVALID")

    scientific_disposition_states: tuple[
        Literal["PASS"],
        Literal["REJECT"],
        Literal["INCONCLUSIVE"],
    ] = ("PASS", "REJECT", "INCONCLUSIVE")

    stop_after_single_bounded_characterization: Literal[True] = True
    automatic_a3_authorized: Literal[False] = False
    baseline_readiness_review_required_after_a2: Literal[True] = True


class Phase5A2SuccessorResolverProtocolV1(ContractModel):
    protocol_version: Literal["phase5-a2-successor-resolver-protocol-v1"] = (
        "phase5-a2-successor-resolver-protocol-v1"
    )

    experiment_id: Literal["phase5-a2-object-subresource-resolver-v1"] = (
        "phase5-a2-object-subresource-resolver-v1"
    )

    parent_a1_rejection_sha256: Sha256 = _A1_REJECTION_SHA256
    parent_intervention_design_protocol_sha256: Sha256 = _INTERVENTION_DESIGN_PROTOCOL_SHA256
    parent_intervention_design_freeze_sha256: Sha256 = _INTERVENTION_DESIGN_FREEZE_SHA256
    resolver_characterization_sha256: Sha256 = _RESOLVER_CHARACTERIZATION_SHA256

    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SHA256
    post_reject_confirmation_suite_sha256: Sha256 = _POST_REJECT_CONFIRMATION_SHA256
    post_reject_confirmation_freeze_sha256: Sha256 = _POST_REJECT_CONFIRMATION_FREEZE_SHA256
    held_out_suite_sha256: Sha256 = _HELD_OUT_SHA256

    hypothesis: Literal[
        "namespace_action_and_generic_object_subresource_evidence_can_safely_disambiguate_operation_identity"
    ] = (
        "namespace_action_and_generic_object_subresource_evidence_can_safely_disambiguate_operation_identity"
    )

    candidate_count: Literal[1] = 1
    runtime_evidence: A2RuntimeEvidenceContractV1
    derivation: A2DerivationContractV1
    gate: A2CharacterizationGateV1

    development_role: Literal["diagnostic_only_spent_for_future_confirmation"] = (
        "diagnostic_only_spent_for_future_confirmation"
    )
    tuning_role: Literal["intervention_tuning_and_regression_only"] = (
        "intervention_tuning_and_regression_only"
    )
    post_reject_confirmation_role: Literal[
        "sealed_independent_confirmation_not_authorized_for_a2_characterization"
    ] = "sealed_independent_confirmation_not_authorized_for_a2_characterization"
    held_out_role: Literal["sealed_final_release_evidence"] = "sealed_final_release_evidence"

    candidate_execution_authorized_at_protocol_freeze: Literal[False] = False
    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
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
            or self.post_reject_confirmation_inspected
            or self.post_reject_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.b0_executed
            or self.chaos_executed
            or self.load_executed
            or self.release_eligible
        ):
            raise ValueError(
                "A2 preregistration cannot overclaim implementation "
                "or execution state"
            )

        if not self.gate.baseline_readiness_review_required_after_a2:
            raise ValueError("A2 must terminate at the baseline-readiness review")

        if self.gate.automatic_a3_authorized:
            raise ValueError("A2 preregistration cannot pre-authorize A3")

        return self


def build_phase5_a2_successor_resolver_protocol_v1() -> Phase5A2SuccessorResolverProtocolV1:
    return Phase5A2SuccessorResolverProtocolV1(
        runtime_evidence=A2RuntimeEvidenceContractV1(),
        derivation=A2DerivationContractV1(),
        gate=A2CharacterizationGateV1(),
    )
