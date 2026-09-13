from __future__ import annotations

import pytest

from rag_reliability.contracts.enums import (
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    FailureLabel,
    ResponseMode,
    RuntimeOutcomeStatus,
    ScenarioClass,
)
from rag_reliability.contracts.evaluation import (
    OrchestrationCaseView,
)
from rag_reliability.evaluation.measurement_aggregation import (
    Phase5AggregationError,
    Phase5AggregationRecord,
    Phase5RoleExpectation,
    Phase5SyntheticAggregationExpectation,
    aggregate_phase5_synthetic_scores,
)
from rag_reliability.evaluation.measurement_scoring import (
    Phase5CaseScore,
)


def _view(
    case_id: str,
    role: EvaluationRole,
    *,
    criticality: Criticality = Criticality.NONCRITICAL,
) -> OrchestrationCaseView:
    return OrchestrationCaseView(
        case_id=case_id,
        case_version="synthetic-v1",
        data_role=role,
        source_family=EvaluationSourceFamily.ISSUES,
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        criticality=criticality,
        query=f"Synthetic query for {case_id}?",
    )


def _answer_score(
    case_id: str,
    *,
    fact_satisfied: int,
    fact_total: int,
    evidence_retrieved: int = 1,
    evidence_total: int = 1,
    context_included: int = 1,
    context_total: int = 1,
    classification_complete: bool = True,
    unresolved_reason: str | None = None,
) -> Phase5CaseScore:
    fact_ratio = fact_satisfied / fact_total
    retrieval_ratio = evidence_retrieved / evidence_total
    context_ratio = context_included / context_total

    primary_failure = (
        None
        if (
            fact_ratio == 1.0
            and retrieval_ratio == 1.0
            and context_ratio == 1.0
        )
        else FailureLabel.UNSUPPORTED_ANSWER
    )

    return Phase5CaseScore(
        case_id=case_id,
        expected_response_mode=ResponseMode.ANSWER,
        actual_status=RuntimeOutcomeStatus.ANSWER,
        strict_answer_success=(
            primary_failure is None
        ),
        required_fact_satisfaction=fact_ratio,
        gold_recall_at_k=retrieval_ratio,
        required_evidence_context_inclusion=(
            context_ratio
        ),
        required_fact_satisfied_count=fact_satisfied,
        required_fact_count=fact_total,
        gold_retrieved_required_evidence_count=(
            evidence_retrieved
        ),
        gold_required_evidence_count=evidence_total,
        context_included_required_evidence_count=(
            context_included
        ),
        context_required_evidence_count=context_total,
        claim_support=True,
        citation_precision=1.0,
        citation_recall=1.0,
        correct_refusal=None,
        over_refusal=False,
        trace_completeness=True,
        latency_ms=10.0,
        provider_attempt_count=1,
        primary_failure=primary_failure,
        classification_complete=classification_complete,
        unresolved_failure_reason=unresolved_reason,
        critical_failure_count_contribution=0,
    )


def _refusal_score(
    case_id: str,
) -> Phase5CaseScore:
    return Phase5CaseScore(
        case_id=case_id,
        expected_response_mode=ResponseMode.REFUSE,
        actual_status=RuntimeOutcomeStatus.REFUSAL,
        strict_answer_success=None,
        required_fact_satisfaction=None,
        gold_recall_at_k=None,
        required_evidence_context_inclusion=None,
        claim_support=None,
        citation_precision=None,
        citation_recall=None,
        correct_refusal=True,
        over_refusal=None,
        trace_completeness=True,
        latency_ms=5.0,
        provider_attempt_count=0,
        primary_failure=None,
        classification_complete=True,
        critical_failure_count_contribution=0,
    )


def _record(
    view: OrchestrationCaseView,
    score: Phase5CaseScore,
    *,
    configuration_id: str = "synthetic-config",
    boundary_verified: bool = True,
) -> Phase5AggregationRecord:
    return Phase5AggregationRecord(
        orchestration=view,
        score=score,
        configuration_id=configuration_id,
        evaluator_runtime_boundary_verified=(
            boundary_verified
        ),
    )


def _expectation(
    *,
    development_count: int = 2,
    tuning_count: int = 1,
) -> Phase5SyntheticAggregationExpectation:
    return Phase5SyntheticAggregationExpectation(
        expected_configuration_id="synthetic-config",
        role_expectations=(
            Phase5RoleExpectation(
                role=EvaluationRole.DEVELOPMENT,
                case_count=development_count,
            ),
            Phase5RoleExpectation(
                role=EvaluationRole.TUNING,
                case_count=tuning_count,
            ),
        ),
    )


def _valid_records(
) -> tuple[Phase5AggregationRecord, ...]:
    answer_a_view = _view(
        "synthetic-answer-a",
        EvaluationRole.DEVELOPMENT,
    )
    answer_b_view = _view(
        "synthetic-answer-b",
        EvaluationRole.DEVELOPMENT,
    )
    refusal_view = _view(
        "synthetic-refusal",
        EvaluationRole.TUNING,
    )

    return (
        _record(
            answer_a_view,
            _answer_score(
                answer_a_view.case_id,
                fact_satisfied=1,
                fact_total=1,
            ),
        ),
        _record(
            answer_b_view,
            _answer_score(
                answer_b_view.case_id,
                fact_satisfied=1,
                fact_total=3,
            ),
        ),
        _record(
            refusal_view,
            _refusal_score(
                refusal_view.case_id
            ),
        ),
    )


def _metric(
    report: object,
    metric_id: str,
) -> object:
    aggregates = report.metric_aggregates

    return next(
        aggregate
        for aggregate in aggregates
        if aggregate.metric_id == metric_id
    )


def test_micro_fact_rate_uses_counts_not_mean_of_case_ratios() -> None:
    report = aggregate_phase5_synthetic_scores(
        _valid_records(),
        _expectation(),
    )

    metric = _metric(
        report,
        "required_fact_satisfaction",
    )

    assert metric.numerator == 2.0
    assert metric.denominator == 4
    assert metric.value == 0.5

    assert metric.value != (
        (1.0 + (1.0 / 3.0))
        / 2.0
    )


def test_report_contains_all_instrument_metrics_in_order() -> None:
    report = aggregate_phase5_synthetic_scores(
        _valid_records(),
        _expectation(),
    )

    assert tuple(
        aggregate.metric_id
        for aggregate in report.metric_aggregates
    ) == (
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

    assert report.evidence_valid is True
    assert report.integrity.all_passed is True
    assert report.baseline_execution_authorized is False
    assert report.held_out_outcomes_exposed is False


def test_configuration_drift_invalidates_evidence() -> None:
    records = list(_valid_records())

    records[0] = Phase5AggregationRecord(
        orchestration=records[0].orchestration,
        score=records[0].score,
        configuration_id="different-config",
        evaluator_runtime_boundary_verified=True,
    )

    report = aggregate_phase5_synthetic_scores(
        tuple(records),
        _expectation(),
    )

    assert report.evidence_valid is False
    assert (
        report.integrity.configuration_identity_pass
        is False
    )


def test_missing_expected_record_invalidates_reconciliation() -> None:
    records = _valid_records()[1:]

    report = aggregate_phase5_synthetic_scores(
        records,
        _expectation(),
    )

    assert report.evidence_valid is False
    assert (
        report.integrity
        .terminal_record_reconciliation_pass
        is False
    )
    assert (
        report.integrity.role_reconciliation_pass
        is False
    )


def test_unresolved_classification_invalidates_evidence() -> None:
    records = list(_valid_records())
    view = records[0].orchestration

    unresolved_score = _answer_score(
        view.case_id,
        fact_satisfied=1,
        fact_total=1,
        classification_complete=False,
        unresolved_reason="Synthetic unresolved classification.",
    )

    records[0] = _record(
        view,
        unresolved_score,
    )

    report = aggregate_phase5_synthetic_scores(
        tuple(records),
        _expectation(),
    )

    assert report.evidence_valid is False
    assert (
        report.integrity.classification_complete_pass
        is False
    )


def test_held_out_record_is_rejected() -> None:
    records = list(_valid_records())

    held_out_view = _view(
        "synthetic-held-out",
        EvaluationRole.HELD_OUT,
    )

    records[0] = _record(
        held_out_view,
        _answer_score(
            held_out_view.case_id,
            fact_satisfied=1,
            fact_total=1,
        ),
    )

    with pytest.raises(
        Phase5AggregationError,
        match="HELD_OUT records are prohibited",
    ):
        aggregate_phase5_synthetic_scores(
            tuple(records),
            _expectation(),
        )
