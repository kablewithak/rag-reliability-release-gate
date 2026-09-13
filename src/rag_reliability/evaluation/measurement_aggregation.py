"""Synthetic aggregation validation for the Phase 5 measurement instrument.

This module validates aggregation mechanics before instrument freeze.
It is not a B0 report path, does not authorize baseline execution,
and rejects HELD_OUT records.
"""

from __future__ import annotations

from collections import Counter
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import (
    Criticality,
    EvaluationRole,
    ResponseMode,
)
from rag_reliability.contracts.evaluation import OrchestrationCaseView
from rag_reliability.evaluation.measurement_instrument import (
    MetricAggregation,
    build_phase5_measurement_instrument_v1,
)
from rag_reliability.evaluation.measurement_scoring import Phase5CaseScore


class Phase5AggregationError(ValueError):
    """Synthetic score package cannot be aggregated safely."""


class Phase5RoleExpectation(ContractModel):
    """Expected synthetic case count for one baseline-visible role."""

    role: EvaluationRole
    case_count: int = Field(ge=1)


class Phase5SyntheticAggregationExpectation(ContractModel):
    """Synthetic-only reconciliation contract for aggregation validation."""

    expectation_version: Literal[
        "phase5-synthetic-aggregation-expectation-v1"
    ] = "phase5-synthetic-aggregation-expectation-v1"

    expected_configuration_id: NonEmptyStr

    role_expectations: tuple[
        Phase5RoleExpectation,
        ...,
    ] = Field(min_length=2, max_length=2)

    baseline_execution_authorized: Literal[False] = False
    held_out_execution_allowed: Literal[False] = False

    @model_validator(mode="after")
    def validate_roles(self) -> Self:
        roles = tuple(
            expectation.role
            for expectation in self.role_expectations
        )

        if len(roles) != len(set(roles)):
            raise ValueError(
                "synthetic role expectations must be unique"
            )

        if set(roles) != {
            EvaluationRole.DEVELOPMENT,
            EvaluationRole.TUNING,
        }:
            raise ValueError(
                "synthetic aggregation must exercise "
                "DEVELOPMENT and TUNING only"
            )

        return self

    @property
    def expected_case_count(self) -> int:
        return sum(
            expectation.case_count
            for expectation in self.role_expectations
        )


class Phase5AggregationRecord(ContractModel):
    """One synthetic orchestration/score record presented to aggregation."""

    orchestration: OrchestrationCaseView
    score: Phase5CaseScore
    configuration_id: NonEmptyStr
    evaluator_runtime_boundary_verified: bool

    @model_validator(mode="after")
    def validate_record_binding(self) -> Self:
        if (
            self.orchestration.case_id
            != self.score.case_id
        ):
            raise ValueError(
                "orchestration case_id does not match score case_id"
            )

        expected_critical_contribution = int(
            self.orchestration.criticality
            is Criticality.CRITICAL
            and self.score.primary_failure is not None
        )

        if (
            self.score.critical_failure_count_contribution
            != expected_critical_contribution
        ):
            raise ValueError(
                "critical failure contribution does not reconcile "
                "with orchestration criticality and primary failure"
            )

        return self


class Phase5MetricAggregate(ContractModel):
    """One auditable aggregate with its exact derivation."""

    metric_id: NonEmptyStr
    aggregation: MetricAggregation
    value: float
    numerator: float
    denominator: int | None = Field(
        default=None,
        ge=1,
    )
    applicable_case_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_derivation(self) -> Self:
        if self.aggregation == "count":
            if self.denominator is not None:
                raise ValueError(
                    "count metric cannot carry denominator"
                )

            if abs(self.value - self.numerator) > 1e-12:
                raise ValueError(
                    "count metric value must equal numerator"
                )

            return self

        if self.denominator is None:
            raise ValueError(
                "non-count metric requires denominator"
            )

        expected = self.numerator / self.denominator

        if abs(self.value - expected) > 1e-12:
            raise ValueError(
                "metric value does not reconcile "
                "with numerator and denominator"
            )

        return self


class Phase5RoleCount(ContractModel):
    role: EvaluationRole
    case_count: int = Field(ge=0)


class Phase5EvidenceIntegritySummary(ContractModel):
    """Evidence-validity checks required before any observation is trusted."""

    terminal_record_reconciliation_pass: bool
    role_reconciliation_pass: bool
    configuration_identity_pass: bool
    evaluator_leakage_tolerance_pass: bool
    classification_complete_pass: bool
    trace_completeness_pass: bool

    held_out_outcomes_exposed: Literal[False] = False

    all_passed: bool

    @model_validator(mode="after")
    def validate_all_passed(self) -> Self:
        expected = all(
            (
                self.terminal_record_reconciliation_pass,
                self.role_reconciliation_pass,
                self.configuration_identity_pass,
                self.evaluator_leakage_tolerance_pass,
                self.classification_complete_pass,
                self.trace_completeness_pass,
                not self.held_out_outcomes_exposed,
            )
        )

        if self.all_passed != expected:
            raise ValueError(
                "all_passed does not reconcile with integrity checks"
            )

        return self


class Phase5SyntheticAggregationReport(ContractModel):
    """Synthetic-only evidence that aggregation mechanics are coherent."""

    report_version: Literal[
        "phase5-synthetic-aggregation-report-v1"
    ] = "phase5-synthetic-aggregation-report-v1"

    evidence_class: Literal[
        "synthetic_measurement_validation"
    ] = "synthetic_measurement_validation"

    expected_case_count: int = Field(ge=1)
    observed_case_count: int = Field(ge=0)

    expected_role_counts: tuple[
        Phase5RoleCount,
        ...,
    ] = Field(min_length=2, max_length=2)

    observed_role_counts: tuple[
        Phase5RoleCount,
        ...,
    ] = Field(min_length=2, max_length=2)

    metric_aggregates: tuple[
        Phase5MetricAggregate,
        ...,
    ] = Field(min_length=13, max_length=13)

    integrity: Phase5EvidenceIntegritySummary
    evidence_valid: bool

    baseline_execution_authorized: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        expected_metric_ids = tuple(
            definition.metric_id
            for definition
            in build_phase5_measurement_instrument_v1()
            .metric_definitions
        )

        observed_metric_ids = tuple(
            aggregate.metric_id
            for aggregate in self.metric_aggregates
        )

        if observed_metric_ids != expected_metric_ids:
            raise ValueError(
                "aggregate metric IDs drifted from instrument"
            )

        if self.evidence_valid != self.integrity.all_passed:
            raise ValueError(
                "evidence_valid does not reconcile "
                "with integrity summary"
            )

        return self


def _require_value(
    value: float | int | bool | None,
    *,
    field_name: str,
) -> float | int | bool:
    if value is None:
        raise Phase5AggregationError(
            f"{field_name} is missing from an applicable score"
        )
    return value


def _binary_rate(
    metric_id: str,
    values: tuple[bool, ...],
) -> Phase5MetricAggregate:
    if not values:
        raise Phase5AggregationError(
            f"{metric_id} has zero applicable cases"
        )

    numerator = float(sum(values))
    denominator = len(values)

    return Phase5MetricAggregate(
        metric_id=metric_id,
        aggregation="binary_case_rate",
        value=numerator / denominator,
        numerator=numerator,
        denominator=denominator,
        applicable_case_count=denominator,
    )


def _micro_rate(
    metric_id: str,
    numerators: tuple[int, ...],
    denominators: tuple[int, ...],
    *,
    applicable_case_count: int,
) -> Phase5MetricAggregate:
    numerator = sum(numerators)
    denominator = sum(denominators)

    if denominator <= 0:
        raise Phase5AggregationError(
            f"{metric_id} has zero micro denominator"
        )

    return Phase5MetricAggregate(
        metric_id=metric_id,
        aggregation="micro_rate",
        value=numerator / denominator,
        numerator=float(numerator),
        denominator=denominator,
        applicable_case_count=applicable_case_count,
    )


def _macro_ratio(
    metric_id: str,
    values: tuple[float, ...],
) -> Phase5MetricAggregate:
    if not values:
        raise Phase5AggregationError(
            f"{metric_id} has zero applicable cases"
        )

    numerator = sum(values)
    denominator = len(values)

    return Phase5MetricAggregate(
        metric_id=metric_id,
        aggregation="macro_ratio",
        value=numerator / denominator,
        numerator=numerator,
        denominator=denominator,
        applicable_case_count=denominator,
    )


def _mean_metric(
    metric_id: str,
    values: tuple[float, ...],
) -> Phase5MetricAggregate:
    if not values:
        raise Phase5AggregationError(
            f"{metric_id} has zero observations"
        )

    numerator = sum(values)
    denominator = len(values)

    return Phase5MetricAggregate(
        metric_id=metric_id,
        aggregation="mean",
        value=numerator / denominator,
        numerator=numerator,
        denominator=denominator,
        applicable_case_count=denominator,
    )


def _role_counts(
    records: tuple[Phase5AggregationRecord, ...],
) -> tuple[Phase5RoleCount, ...]:
    counts = Counter(
        record.orchestration.data_role
        for record in records
    )

    return (
        Phase5RoleCount(
            role=EvaluationRole.DEVELOPMENT,
            case_count=counts[
                EvaluationRole.DEVELOPMENT
            ],
        ),
        Phase5RoleCount(
            role=EvaluationRole.TUNING,
            case_count=counts[
                EvaluationRole.TUNING
            ],
        ),
    )


def _expected_role_counts(
    expectation: Phase5SyntheticAggregationExpectation,
) -> tuple[Phase5RoleCount, ...]:
    by_role = {
        item.role: item.case_count
        for item in expectation.role_expectations
    }

    return (
        Phase5RoleCount(
            role=EvaluationRole.DEVELOPMENT,
            case_count=by_role[
                EvaluationRole.DEVELOPMENT
            ],
        ),
        Phase5RoleCount(
            role=EvaluationRole.TUNING,
            case_count=by_role[
                EvaluationRole.TUNING
            ],
        ),
    )


def aggregate_phase5_synthetic_scores(
    records: tuple[Phase5AggregationRecord, ...],
    expectation: Phase5SyntheticAggregationExpectation,
) -> Phase5SyntheticAggregationReport:
    """Aggregate synthetic scores and reconcile evidence integrity."""

    case_ids = tuple(
        record.score.case_id
        for record in records
    )

    if len(case_ids) != len(set(case_ids)):
        raise Phase5AggregationError(
            "aggregation records must have unique case IDs"
        )

    if any(
        record.orchestration.data_role
        is EvaluationRole.HELD_OUT
        for record in records
    ):
        raise Phase5AggregationError(
            "HELD_OUT records are prohibited "
            "from synthetic aggregation validation"
        )

    answer_scores = tuple(
        record.score
        for record in records
        if record.score.expected_response_mode
        is not ResponseMode.REFUSE
    )

    refusal_scores = tuple(
        record.score
        for record in records
        if record.score.expected_response_mode
        is ResponseMode.REFUSE
    )

    if not answer_scores:
        raise Phase5AggregationError(
            "synthetic aggregation requires answer cases"
        )

    if not refusal_scores:
        raise Phase5AggregationError(
            "synthetic aggregation requires refusal cases"
        )

    metric_aggregates = (
        _binary_rate(
            "strict_answer_success",
            tuple(
                bool(
                    _require_value(
                        score.strict_answer_success,
                        field_name="strict_answer_success",
                    )
                )
                for score in answer_scores
            ),
        ),
        _micro_rate(
            "required_fact_satisfaction",
            tuple(
                int(
                    _require_value(
                        score.required_fact_satisfied_count,
                        field_name="required_fact_satisfied_count",
                    )
                )
                for score in answer_scores
            ),
            tuple(
                int(
                    _require_value(
                        score.required_fact_count,
                        field_name="required_fact_count",
                    )
                )
                for score in answer_scores
            ),
            applicable_case_count=len(answer_scores),
        ),
        _micro_rate(
            "gold_recall_at_k",
            tuple(
                int(
                    _require_value(
                        score.gold_retrieved_required_evidence_count,
                        field_name=(
                            "gold_retrieved_required_evidence_count"
                        ),
                    )
                )
                for score in answer_scores
            ),
            tuple(
                int(
                    _require_value(
                        score.gold_required_evidence_count,
                        field_name="gold_required_evidence_count",
                    )
                )
                for score in answer_scores
            ),
            applicable_case_count=len(answer_scores),
        ),
        _micro_rate(
            "required_evidence_context_inclusion",
            tuple(
                int(
                    _require_value(
                        score.context_included_required_evidence_count,
                        field_name=(
                            "context_included_required_evidence_count"
                        ),
                    )
                )
                for score in answer_scores
            ),
            tuple(
                int(
                    _require_value(
                        score.context_required_evidence_count,
                        field_name="context_required_evidence_count",
                    )
                )
                for score in answer_scores
            ),
            applicable_case_count=len(answer_scores),
        ),
        _binary_rate(
            "claim_support",
            tuple(
                bool(
                    _require_value(
                        score.claim_support,
                        field_name="claim_support",
                    )
                )
                for score in answer_scores
            ),
        ),
        _macro_ratio(
            "citation_precision",
            tuple(
                float(
                    _require_value(
                        score.citation_precision,
                        field_name="citation_precision",
                    )
                )
                for score in answer_scores
            ),
        ),
        _macro_ratio(
            "citation_recall",
            tuple(
                float(
                    _require_value(
                        score.citation_recall,
                        field_name="citation_recall",
                    )
                )
                for score in answer_scores
            ),
        ),
        _binary_rate(
            "correct_refusal",
            tuple(
                bool(
                    _require_value(
                        score.correct_refusal,
                        field_name="correct_refusal",
                    )
                )
                for score in refusal_scores
            ),
        ),
        _binary_rate(
            "over_refusal",
            tuple(
                bool(
                    _require_value(
                        score.over_refusal,
                        field_name="over_refusal",
                    )
                )
                for score in answer_scores
            ),
        ),
        Phase5MetricAggregate(
            metric_id="critical_failure_count",
            aggregation="count",
            value=float(
                sum(
                    score.critical_failure_count_contribution
                    for score in (
                        record.score
                        for record in records
                    )
                )
            ),
            numerator=float(
                sum(
                    score.critical_failure_count_contribution
                    for score in (
                        record.score
                        for record in records
                    )
                )
            ),
            denominator=None,
            applicable_case_count=len(records),
        ),
        _binary_rate(
            "trace_completeness",
            tuple(
                record.score.trace_completeness
                for record in records
            ),
        ),
        _mean_metric(
            "latency_ms",
            tuple(
                record.score.latency_ms
                for record in records
            ),
        ),
        _mean_metric(
            "provider_attempt_count",
            tuple(
                float(
                    record.score.provider_attempt_count
                )
                for record in records
            ),
        ),
    )

    expected_role_counts = _expected_role_counts(
        expectation
    )
    observed_role_counts = _role_counts(records)

    terminal_record_reconciliation_pass = (
        len(records)
        == expectation.expected_case_count
    )

    role_reconciliation_pass = (
        observed_role_counts
        == expected_role_counts
    )

    configuration_identity_pass = all(
        record.configuration_id
        == expectation.expected_configuration_id
        for record in records
    )

    evaluator_leakage_tolerance_pass = all(
        record.evaluator_runtime_boundary_verified
        for record in records
    )

    classification_complete_pass = all(
        record.score.classification_complete
        for record in records
    )

    trace_completeness_pass = all(
        record.score.trace_completeness
        for record in records
    )

    all_passed = all(
        (
            terminal_record_reconciliation_pass,
            role_reconciliation_pass,
            configuration_identity_pass,
            evaluator_leakage_tolerance_pass,
            classification_complete_pass,
            trace_completeness_pass,
        )
    )

    integrity = Phase5EvidenceIntegritySummary(
        terminal_record_reconciliation_pass=(
            terminal_record_reconciliation_pass
        ),
        role_reconciliation_pass=(
            role_reconciliation_pass
        ),
        configuration_identity_pass=(
            configuration_identity_pass
        ),
        evaluator_leakage_tolerance_pass=(
            evaluator_leakage_tolerance_pass
        ),
        classification_complete_pass=(
            classification_complete_pass
        ),
        trace_completeness_pass=(
            trace_completeness_pass
        ),
        all_passed=all_passed,
    )

    return Phase5SyntheticAggregationReport(
        expected_case_count=(
            expectation.expected_case_count
        ),
        observed_case_count=len(records),
        expected_role_counts=expected_role_counts,
        observed_role_counts=observed_role_counts,
        metric_aggregates=metric_aggregates,
        integrity=integrity,
        evidence_valid=integrity.all_passed,
    )
