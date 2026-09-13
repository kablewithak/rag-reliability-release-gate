"""Phase 5 measurement-instrument contracts.

This module freezes metric semantics before any B0 execution.
It does not execute cases, expose HELD_OUT outcomes, or authorize baseline runs.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr

MetricScope = Literal[
    "answer_cases",
    "refusal_cases",
    "all_cases",
]

MetricAggregation = Literal[
    "binary_case_rate",
    "micro_rate",
    "macro_ratio",
    "count",
    "mean",
]

MetricDirection = Literal[
    "higher_is_better",
    "lower_is_better",
    "descriptive",
]


class Phase5MetricDefinition(ContractModel):
    """One frozen Phase 5 metric definition."""

    metric_id: NonEmptyStr
    scope: MetricScope
    aggregation: MetricAggregation
    direction: MetricDirection
    numerator_rule: NonEmptyStr
    denominator_rule: NonEmptyStr


class Phase5FactVerdict(ContractModel):
    """Evaluator-owned semantic verdict for one required fact."""

    fact_id: NonEmptyStr

    verdict: Literal[
        "satisfied",
        "not_satisfied",
    ]

    supporting_answer_span: NonEmptyStr | None = None
    rationale: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_audit_evidence(self) -> Self:
        if (
            self.verdict == "satisfied"
            and self.supporting_answer_span is None
        ):
            raise ValueError(
                "satisfied fact verdict requires supporting_answer_span"
            )

        if (
            self.verdict == "not_satisfied"
            and self.rationale is None
        ):
            raise ValueError(
                "not_satisfied fact verdict requires rationale"
            )

        return self


class Phase5FactAssessmentSet(ContractModel):
    """Complete evaluator-owned fact verdicts for one answer case."""

    case_id: NonEmptyStr

    verdicts: tuple[
        Phase5FactVerdict,
        ...,
    ] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_fact_ids(self) -> Self:
        fact_ids = tuple(
            verdict.fact_id
            for verdict in self.verdicts
        )

        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError(
                "fact assessment IDs must be unique"
            )

        return self


class Phase5FactScoringContract(ContractModel):
    """Boundary for semantic required-fact assessment."""

    method_id: Literal[
        "evaluator_owned_fact_verdict_v1"
    ] = "evaluator_owned_fact_verdict_v1"

    runtime_gold_access_allowed: Literal[
        False
    ] = False

    lexical_substring_matching_allowed: Literal[
        False
    ] = False

    verdict_required_for_every_required_fact_id: Literal[
        True
    ] = True

    satisfied_verdict_requires_answer_span: Literal[
        True
    ] = True

    not_satisfied_verdict_requires_rationale: Literal[
        True
    ] = True

    unresolved_verdict_allowed: Literal[
        False
    ] = False

    deterministic_score_rule: Literal[
        "satisfied_verdict_count_divided_by_required_fact_count"
    ] = (
        "satisfied_verdict_count_divided_by_required_fact_count"
    )


_METRIC_DEFINITIONS = (
    Phase5MetricDefinition(
        metric_id="strict_answer_success",
        scope="answer_cases",
        aggregation="binary_case_rate",
        direction="higher_is_better",
        numerator_rule=(
            "answer cases with an answer outcome and every required "
            "answer correctness check passing"
        ),
        denominator_rule="all answer cases",
    ),
    Phase5MetricDefinition(
        metric_id="required_fact_satisfaction",
        scope="answer_cases",
        aggregation="micro_rate",
        direction="higher_is_better",
        numerator_rule=(
            "required fact IDs with evaluator-owned verdict satisfied"
        ),
        denominator_rule=(
            "all required fact IDs across answer cases"
        ),
    ),
    Phase5MetricDefinition(
        metric_id="gold_recall_at_k",
        scope="answer_cases",
        aggregation="micro_rate",
        direction="higher_is_better",
        numerator_rule=(
            "required evidence IDs present in retrieval results "
            "within configured top_k"
        ),
        denominator_rule=(
            "all required evidence IDs across answer cases"
        ),
    ),
    Phase5MetricDefinition(
        metric_id="required_evidence_context_inclusion",
        scope="answer_cases",
        aggregation="micro_rate",
        direction="higher_is_better",
        numerator_rule=(
            "required evidence IDs present in assembled context"
        ),
        denominator_rule=(
            "all required evidence IDs across answer cases"
        ),
    ),
    Phase5MetricDefinition(
        metric_id="claim_support",
        scope="answer_cases",
        aggregation="binary_case_rate",
        direction="higher_is_better",
        numerator_rule=(
            "answer cases whose citation validation reports "
            "all material claims supported"
        ),
        denominator_rule="all answer cases",
    ),
    Phase5MetricDefinition(
        metric_id="citation_precision",
        scope="answer_cases",
        aggregation="macro_ratio",
        direction="higher_is_better",
        numerator_rule=(
            "per case, cited evidence IDs with supported "
            "citation-validation status"
        ),
        denominator_rule=(
            "per case, all cited evidence IDs; zero citations yields "
            "case precision 0.0; macro mean across answer cases"
        ),
    ),
    Phase5MetricDefinition(
        metric_id="citation_recall",
        scope="answer_cases",
        aggregation="macro_ratio",
        direction="higher_is_better",
        numerator_rule=(
            "per case, required evidence IDs also present "
            "in cited evidence IDs"
        ),
        denominator_rule=(
            "per case, required evidence IDs; macro mean "
            "across answer cases"
        ),
    ),
    Phase5MetricDefinition(
        metric_id="correct_refusal",
        scope="refusal_cases",
        aggregation="binary_case_rate",
        direction="higher_is_better",
        numerator_rule=(
            "refusal cases ending in refusal with the expected "
            "must_refuse_reason"
        ),
        denominator_rule="all refusal cases",
    ),
    Phase5MetricDefinition(
        metric_id="over_refusal",
        scope="answer_cases",
        aggregation="binary_case_rate",
        direction="lower_is_better",
        numerator_rule=(
            "answer cases ending in refusal"
        ),
        denominator_rule="all answer cases",
    ),
    Phase5MetricDefinition(
        metric_id="critical_failure_count",
        scope="all_cases",
        aggregation="count",
        direction="lower_is_better",
        numerator_rule=(
            "critical cases with any required correctness or "
            "integrity check failing"
        ),
        denominator_rule="not_applicable",
    ),
    Phase5MetricDefinition(
        metric_id="trace_completeness",
        scope="all_cases",
        aggregation="binary_case_rate",
        direction="higher_is_better",
        numerator_rule=(
            "cases whose required terminal trace is complete"
        ),
        denominator_rule="all executed cases",
    ),
    Phase5MetricDefinition(
        metric_id="latency_ms",
        scope="all_cases",
        aggregation="mean",
        direction="descriptive",
        numerator_rule=(
            "sum of terminal trace elapsed milliseconds"
        ),
        denominator_rule="all executed cases",
    ),
    Phase5MetricDefinition(
        metric_id="provider_attempt_count",
        scope="all_cases",
        aggregation="mean",
        direction="descriptive",
        numerator_rule=(
            "sum of recorded provider-generation attempts"
        ),
        denominator_rule="all executed cases",
    ),
)


class Phase5MeasurementInstrumentV1(ContractModel):
    """Draft Phase 5 instrument preceding freeze and B0 authorization."""

    instrument_version: Literal[
        "phase5-measurement-instrument-v1"
    ] = "phase5-measurement-instrument-v1"

    instrument_status: Literal[
        "draft_unfrozen"
    ] = "draft_unfrozen"

    protocol_version: Literal[
        "phase5-baseline-protocol-v1"
    ] = "phase5-baseline-protocol-v1"

    metric_definitions: tuple[
        Phase5MetricDefinition,
        ...,
    ] = Field(
        min_length=13,
        max_length=13,
    )

    fact_scoring: Phase5FactScoringContract

    phase2_substring_fact_scoring_reused: Literal[
        False
    ] = False

    baseline_execution_authorized: Literal[
        False
    ] = False

    held_out_outcomes_exposed: Literal[
        False
    ] = False

    @model_validator(mode="after")
    def validate_metric_contract(self) -> Self:
        if self.metric_definitions != _METRIC_DEFINITIONS:
            raise ValueError(
                "Phase 5 measurement metric definitions drifted"
            )

        return self


def build_phase5_measurement_instrument_v1(
) -> Phase5MeasurementInstrumentV1:
    """Build the still-unfrozen Phase 5 measurement instrument."""

    return Phase5MeasurementInstrumentV1(
        metric_definitions=_METRIC_DEFINITIONS,
        fact_scoring=Phase5FactScoringContract(),
    )
