"""Phase 5 baseline measurement protocol contracts.

This module defines the measurement boundary before any B0 execution.
It does not execute cases, expose HELD_OUT outcomes, or authorize baseline runs.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import EvaluationRole

_DEVELOPMENT_CASES_JSON_SHA256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_CASES_JSON_SHA256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)
_HELD_OUT_CASES_JSON_SHA256 = (
    "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
)

_DEVELOPMENT_FREEZE_RECEIPT_SHA256 = (
    "6deecc31195f3acefb0a6a47a650bf20e4f7606bac9131ff882126504dfbc1bc"
)
_TUNING_FREEZE_RECEIPT_SHA256 = (
    "ef0edfee6a71a7f294c22dcc17d9ecb657b200a100175a7ccd2c709a1e3f97f6"
)
_HELD_OUT_FREEZE_RECEIPT_SHA256 = (
    "00428ea72206b7e80b65ff80ed85e100aa0e40de208e03fc5741398e1fb0465c"
)

_REQUIRED_METRIC_IDS = (
    "strict_answer_success",
    "required_fact_satisfaction",
    "gold_recall_at_k",
    "required_evidence_context_inclusion",
    "claim_support",
    "citation_precision",
    "citation_recall",
    "correct_refusal",
    "over_refusal",
    "critical_failure_count",
    "trace_completeness",
    "latency_ms",
    "provider_attempt_count",
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


class BaselineRoleBinding(ContractModel):
    """Custody binding for one frozen Phase 4 evaluation role."""

    role: EvaluationRole
    case_count: int = Field(ge=1)
    cluster_count: int = Field(ge=1)
    suite_json_sha256: Sha256
    freeze_receipt_sha256: Sha256
    included_in_baseline: bool


class BaselineMeasurementContract(ContractModel):
    """Measurement-integrity requirements for a valid B0 evidence package."""

    required_metric_ids: tuple[NonEmptyStr, ...] = Field(
        min_length=len(_REQUIRED_METRIC_IDS),
        max_length=len(_REQUIRED_METRIC_IDS),
    )

    terminal_record_percent_required: Literal[100] = 100
    trace_completeness_percent_required: Literal[100] = 100

    unauthorized_role_execution_tolerance: Literal[0] = 0
    evaluator_leakage_tolerance: Literal[0] = 0
    configuration_identity_mismatch_tolerance: Literal[0] = 0

    failure_taxonomy_contract: Literal[
        "reuse_existing_failure_label_enum"
    ] = "reuse_existing_failure_label_enum"

    failure_assignment_rule: Literal[
        "earliest_supported_failure"
    ] = "earliest_supported_failure"

    unresolved_failure_policy: Literal[
        "diagnosis_required_before_valid_receipt"
    ] = "diagnosis_required_before_valid_receipt"

    quality_threshold_is_baseline_validity_gate: Literal[False] = False

    @model_validator(mode="after")
    def validate_metric_contract(self) -> Self:
        if self.required_metric_ids != _REQUIRED_METRIC_IDS:
            raise ValueError("Phase 5 B0 metric set drifted")
        return self


class BaselineExecutionContract(ContractModel):
    """Execution-budget and evidence-claim boundary for deterministic B0."""

    evidence_lane: Literal[
        "deterministic_replay_control"
    ] = "deterministic_replay_control"

    provider_semantics: Literal[
        "query_keyed_scripted_response"
    ] = "query_keyed_scripted_response"

    generation_is_context_sensitive: Literal[False] = False

    primary_execution_count_per_case: Literal[1] = 1
    deterministic_replication_count_per_case: Literal[1] = 1
    maximum_total_case_executions: Literal[84] = 84

    same_stage_failure_stop_count: Literal[2] = 2

    supported_claim_ids: tuple[NonEmptyStr, ...] = Field(
        min_length=len(_SUPPORTED_REPLAY_CLAIMS),
        max_length=len(_SUPPORTED_REPLAY_CLAIMS),
    )

    prohibited_claim_ids: tuple[NonEmptyStr, ...] = Field(
        min_length=len(_PROHIBITED_REPLAY_CLAIMS),
        max_length=len(_PROHIBITED_REPLAY_CLAIMS),
    )

    @model_validator(mode="after")
    def validate_claim_boundary(self) -> Self:
        if self.supported_claim_ids != _SUPPORTED_REPLAY_CLAIMS:
            raise ValueError("replay-lane supported claims drifted")

        if self.prohibited_claim_ids != _PROHIBITED_REPLAY_CLAIMS:
            raise ValueError("replay-lane prohibited claims drifted")

        return self


class Phase5BaselineProtocolV1(ContractModel):
    """Unfrozen Phase 5 protocol candidate preceding B0 authorization."""

    protocol_version: Literal[
        "phase5-baseline-protocol-v1"
    ] = "phase5-baseline-protocol-v1"

    protocol_status: Literal[
        "draft_unfrozen"
    ] = "draft_unfrozen"

    phase4_evaluation_suite_frozen: Literal[True] = True

    role_bindings: tuple[BaselineRoleBinding, ...] = Field(
        min_length=3,
        max_length=3,
    )

    runtime_projection_fields: tuple[NonEmptyStr, ...] = (
        "case_id",
        "query",
    )

    included_case_count: Literal[42] = 42
    included_cluster_count: Literal[21] = 21

    measurement: BaselineMeasurementContract
    execution: BaselineExecutionContract

    held_out_outcomes_exposed: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    chaos_authorized: Literal[False] = False
    intervention_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol_boundary(self) -> Self:
        bindings = {
            binding.role: binding
            for binding in self.role_bindings
        }

        if set(bindings) != set(EvaluationRole):
            raise ValueError("protocol must bind all frozen evaluation roles")

        development = bindings[EvaluationRole.DEVELOPMENT]
        tuning = bindings[EvaluationRole.TUNING]
        held_out = bindings[EvaluationRole.HELD_OUT]

        expected_development = (
            24,
            12,
            _DEVELOPMENT_CASES_JSON_SHA256,
            _DEVELOPMENT_FREEZE_RECEIPT_SHA256,
            True,
        )
        observed_development = (
            development.case_count,
            development.cluster_count,
            development.suite_json_sha256,
            development.freeze_receipt_sha256,
            development.included_in_baseline,
        )

        if observed_development != expected_development:
            raise ValueError("DEVELOPMENT binding drifted")

        expected_tuning = (
            18,
            9,
            _TUNING_CASES_JSON_SHA256,
            _TUNING_FREEZE_RECEIPT_SHA256,
            True,
        )
        observed_tuning = (
            tuning.case_count,
            tuning.cluster_count,
            tuning.suite_json_sha256,
            tuning.freeze_receipt_sha256,
            tuning.included_in_baseline,
        )

        if observed_tuning != expected_tuning:
            raise ValueError("TUNING binding drifted")

        expected_held_out = (
            18,
            9,
            _HELD_OUT_CASES_JSON_SHA256,
            _HELD_OUT_FREEZE_RECEIPT_SHA256,
            False,
        )
        observed_held_out = (
            held_out.case_count,
            held_out.cluster_count,
            held_out.suite_json_sha256,
            held_out.freeze_receipt_sha256,
            held_out.included_in_baseline,
        )

        if observed_held_out != expected_held_out:
            raise ValueError("HELD_OUT binding drifted")

        if self.runtime_projection_fields != ("case_id", "query"):
            raise ValueError("runtime projection boundary drifted")

        return self


def build_phase5_baseline_protocol_v1() -> Phase5BaselineProtocolV1:
    """Build the deterministic, still-unfrozen Phase 5 B0 protocol candidate."""

    return Phase5BaselineProtocolV1(
        role_bindings=(
            BaselineRoleBinding(
                role=EvaluationRole.DEVELOPMENT,
                case_count=24,
                cluster_count=12,
                suite_json_sha256=_DEVELOPMENT_CASES_JSON_SHA256,
                freeze_receipt_sha256=_DEVELOPMENT_FREEZE_RECEIPT_SHA256,
                included_in_baseline=True,
            ),
            BaselineRoleBinding(
                role=EvaluationRole.TUNING,
                case_count=18,
                cluster_count=9,
                suite_json_sha256=_TUNING_CASES_JSON_SHA256,
                freeze_receipt_sha256=_TUNING_FREEZE_RECEIPT_SHA256,
                included_in_baseline=True,
            ),
            BaselineRoleBinding(
                role=EvaluationRole.HELD_OUT,
                case_count=18,
                cluster_count=9,
                suite_json_sha256=_HELD_OUT_CASES_JSON_SHA256,
                freeze_receipt_sha256=_HELD_OUT_FREEZE_RECEIPT_SHA256,
                included_in_baseline=False,
            ),
        ),
        measurement=BaselineMeasurementContract(
            required_metric_ids=_REQUIRED_METRIC_IDS,
        ),
        execution=BaselineExecutionContract(
            supported_claim_ids=_SUPPORTED_REPLAY_CLAIMS,
            prohibited_claim_ids=_PROHIBITED_REPLAY_CLAIMS,
        ),
    )
