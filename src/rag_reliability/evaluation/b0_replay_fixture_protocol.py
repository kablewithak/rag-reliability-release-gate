"""Freeze the G5M B0 replay-fixture authoring boundary."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256

_BASELINE_PROTOCOL_SHA256: Sha256 = (
    "20637e8eaa598224c33fe83d223fcc5d031d2bfa577299c8cdff4ccfceb6cc19"
)
_BASELINE_PROTOCOL_FREEZE_SHA256: Sha256 = (
    "a92845181c9fcd3c69b84a191f1288f4391431cae8f82fe6c520b0b2a07bf434"
)
_MEASUREMENT_FREEZE_V2_SHA256: Sha256 = (
    "6249eb30e9c5986bba55b8d5adba22e62ae4df712c08b4e950b544962a19c932"
)
_MEASUREMENT_SOURCE_SHA256: Sha256 = (
    "72a718ef8b282c1c2d3e4e1d143222addcca777bd8ee159f51013a8a231a9a45"
)
_MEASUREMENT_SCORING_SOURCE_SHA256: Sha256 = (
    "0e0e6a334bf1b904fcf67db0852fd23c3cf57f0fd01f53c3e538763a2f59281d"
)
_MEASUREMENT_AGGREGATION_SOURCE_SHA256: Sha256 = (
    "62fce6d52291ec123be9880ae9145b2fff8408ac53c9b912d011b005102a6927"
)
_G5K_QUALIFICATION_SHA256: Sha256 = (
    "678dcb0d6453e11cd8e2b9c71153ed8337d5b8a26fcd36d732d6e8eb05dcbe71"
)
_G5K_RUNTIME_CONFIGURATION_ID: Sha256 = (
    "7399c9ef7cd6612eb8fc363602e9c45c74ca691acde257aa40d07cc4135642a2"
)
_CHUNK_MANIFEST_SHA256: Sha256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)
_DEVELOPMENT_SUITE_SHA256: Sha256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SUITE_SHA256: Sha256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)

_ALLOWED_CASE_FIELDS = ("case_id", "query")

_FORBIDDEN_AUTHORING_FIELDS = (
    "required_source_ids",
    "required_evidence_ids",
    "required_facts",
    "gold_facts",
    "expected_response_mode",
    "expected_response_mode_as_runtime_signal",
    "gold_operation_id",
    "scoring_labels",
    "held_out_outcomes",
    "post_run_evaluator_annotations",
)

_SUPPORTED_REPLAY_CLAIMS = (
    "retrieval_behavior",
    "filtering_behavior",
    "context_selection_behavior",
    "citation_validation_behavior",
    "refusal_control_flow",
    "trace_accounting",
)

_PROHIBITED_REPLAY_CLAIMS = (
    "context_sensitive_generation_improvement",
    "real_provider_robustness",
    "release_readiness",
)


class Phase5B0ReplayFixtureProtocolV1(ContractModel):
    """Preregister deterministic, evaluator-blind B0 replay fixture authoring."""

    protocol_version: Literal[
        "phase5-b0-replay-fixture-protocol-v1"
    ] = "phase5-b0-replay-fixture-protocol-v1"

    protocol_status: Literal["draft_unfrozen"] = "draft_unfrozen"

    baseline_protocol_sha256: Sha256 = _BASELINE_PROTOCOL_SHA256
    baseline_protocol_freeze_sha256: Sha256 = _BASELINE_PROTOCOL_FREEZE_SHA256

    measurement_freeze_v2_sha256: Sha256 = _MEASUREMENT_FREEZE_V2_SHA256
    measurement_source_sha256: Sha256 = _MEASUREMENT_SOURCE_SHA256
    measurement_scoring_source_sha256: Sha256 = _MEASUREMENT_SCORING_SOURCE_SHA256
    measurement_aggregation_source_sha256: Sha256 = _MEASUREMENT_AGGREGATION_SOURCE_SHA256

    g5k_runtime_qualification_sha256: Sha256 = _G5K_QUALIFICATION_SHA256
    g5k_runtime_configuration_id: Sha256 = _G5K_RUNTIME_CONFIGURATION_ID

    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SUITE_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SUITE_SHA256

    authorized_case_count: Literal[42] = 42
    development_case_count: Literal[24] = 24
    tuning_case_count: Literal[18] = 18

    provider_mode: Literal[
        "query_keyed_scripted_response"
    ] = "query_keyed_scripted_response"

    generation_is_context_sensitive: Literal[False] = False

    fixture_generation_policy: Literal[
        "first_eligible_bounded_context_item_verbatim"
    ] = "first_eligible_bounded_context_item_verbatim"

    response_text_rule: Literal[
        "answer_text_equals_first_context_item_content"
    ] = "answer_text_equals_first_context_item_content"

    citation_rule: Literal[
        "cite_exactly_first_context_item_evidence_id"
    ] = "cite_exactly_first_context_item_evidence_id"

    no_eligible_evidence_rule: Literal[
        "record_pre_provider_refusal_and_create_no_provider_entry"
    ] = "record_pre_provider_refusal_and_create_no_provider_entry"

    provider_coverage_rule: Literal[
        "every_authorized_case_that_reaches_provider_has_exactly_one_query_entry"
    ] = "every_authorized_case_that_reaches_provider_has_exactly_one_query_entry"

    duplicate_query_rule: Literal[
        "duplicate_queries_must_resolve_to_identical_scripted_response"
    ] = "duplicate_queries_must_resolve_to_identical_scripted_response"

    selected_retrieval_id: Literal[
        "phase5-operation-aware-rrf-stable-partition-v1"
    ] = "phase5-operation-aware-rrf-stable-partition-v1"

    retrieval_top_k: Literal[20] = 20
    source_policy_id: Literal["github-rest-current-v1"] = "github-rest-current-v1"
    context_builder_id: Literal["bounded-context-v1"] = "bounded-context-v1"
    context_budget_unit_id: Literal["characters"] = "characters"
    context_max_budget: Literal[69663] = 69663
    context_max_evidence_items: Literal[15] = 15

    runtime_projection_fields: tuple[NonEmptyStr, ...] = Field(min_length=2, max_length=2)
    forbidden_authoring_fields: tuple[NonEmptyStr, ...] = Field(min_length=10, max_length=10)
    supported_claim_ids: tuple[NonEmptyStr, ...] = Field(min_length=6, max_length=6)
    prohibited_claim_ids: tuple[NonEmptyStr, ...] = Field(min_length=3, max_length=3)

    evaluator_fields_used_for_fixture_authoring: Literal[False] = False
    expected_modes_used_for_fixture_authoring: Literal[False] = False
    gold_facts_used_for_fixture_authoring: Literal[False] = False
    gold_evidence_used_for_fixture_authoring: Literal[False] = False

    new_live_provider_calls_authorized: Literal[0] = 0
    parameter_sweep_authorized: Literal[False] = False
    post_hoc_response_editing_authorized: Literal[False] = False

    replay_fixture_materialized: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol(self) -> Self:
        if self.runtime_projection_fields != _ALLOWED_CASE_FIELDS:
            raise ValueError("B0 replay-fixture runtime projection drifted")

        if self.forbidden_authoring_fields != _FORBIDDEN_AUTHORING_FIELDS:
            raise ValueError("B0 replay-fixture evaluator boundary drifted")

        if self.supported_claim_ids != _SUPPORTED_REPLAY_CLAIMS:
            raise ValueError("B0 replay supported claims drifted")

        if self.prohibited_claim_ids != _PROHIBITED_REPLAY_CLAIMS:
            raise ValueError("B0 replay prohibited claims drifted")

        if (
            self.evaluator_fields_used_for_fixture_authoring
            or self.expected_modes_used_for_fixture_authoring
            or self.gold_facts_used_for_fixture_authoring
            or self.gold_evidence_used_for_fixture_authoring
        ):
            raise ValueError("B0 replay fixture cannot use evaluator truth")

        if (
            self.new_live_provider_calls_authorized != 0
            or self.parameter_sweep_authorized
            or self.post_hoc_response_editing_authorized
        ):
            raise ValueError("B0 replay fixture protocol authorizes forbidden adaptation")

        if (
            self.replay_fixture_materialized
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.post_reject_confirmation_inspected
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("B0 replay fixture protocol overclaims downstream state")

        return self


def build_phase5_b0_replay_fixture_protocol_v1(
) -> Phase5B0ReplayFixtureProtocolV1:
    return Phase5B0ReplayFixtureProtocolV1(
        runtime_projection_fields=_ALLOWED_CASE_FIELDS,
        forbidden_authoring_fields=_FORBIDDEN_AUTHORING_FIELDS,
        supported_claim_ids=_SUPPORTED_REPLAY_CLAIMS,
        prohibited_claim_ids=_PROHIBITED_REPLAY_CLAIMS,
    )
