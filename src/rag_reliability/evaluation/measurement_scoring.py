"""Deterministic Phase 5 case scoring.

This module scores synthetic or authorized executions only.
It does not load frozen suites, execute B0, or expose HELD_OUT outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import (
    CitationValidationStatus,
    Criticality,
    FailureLabel,
    RefusalReason,
    ResponseMode,
    RuntimeErrorCode,
    RuntimeOutcomeStatus,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import (
    AnswerOutcome,
    ErrorOutcome,
    RefusalOutcome,
)
from rag_reliability.contracts.tracing import TraceEvent
from rag_reliability.evaluation.measurement_instrument import (
    Phase5FactAssessmentSet,
)
from rag_reliability.runtime.models import PipelineExecution


class Phase5ScoringError(ValueError):
    """Execution cannot be scored without violating the frozen semantics."""


class Phase5CaseScore(ContractModel):
    """Evaluator-owned deterministic measurements for one case."""

    case_id: NonEmptyStr
    expected_response_mode: ResponseMode
    actual_status: RuntimeOutcomeStatus

    strict_answer_success: bool | None = None
    required_fact_satisfaction: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    gold_recall_at_k: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    required_evidence_context_inclusion: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    required_fact_satisfied_count: int | None = Field(
        default=None,
        ge=0,
    )
    required_fact_count: int | None = Field(
        default=None,
        ge=1,
    )

    gold_retrieved_required_evidence_count: int | None = Field(
        default=None,
        ge=0,
    )
    gold_required_evidence_count: int | None = Field(
        default=None,
        ge=1,
    )

    context_included_required_evidence_count: int | None = Field(
        default=None,
        ge=0,
    )
    context_required_evidence_count: int | None = Field(
        default=None,
        ge=1,
    )

    claim_support: bool | None = None
    citation_precision: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    citation_recall: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    correct_refusal: bool | None = None
    over_refusal: bool | None = None

    trace_completeness: bool
    latency_ms: float = Field(ge=0.0)
    provider_attempt_count: int = Field(ge=0)

    primary_failure: FailureLabel | None = None
    secondary_failures: tuple[FailureLabel, ...] = ()

    classification_complete: bool = True
    unresolved_failure_reason: NonEmptyStr | None = None

    critical_failure_count_contribution: int = Field(
        ge=0,
        le=1,
    )

    @model_validator(mode="after")
    def validate_classification(self) -> Phase5CaseScore:
        if (
            self.classification_complete
            and self.unresolved_failure_reason is not None
        ):
            raise ValueError(
                "complete classification cannot carry unresolved reason"
            )

        if (
            not self.classification_complete
            and self.unresolved_failure_reason is None
        ):
            raise ValueError(
                "incomplete classification requires unresolved reason"
            )

        if (
            self.primary_failure is not None
            and self.primary_failure in self.secondary_failures
        ):
            raise ValueError(
                "primary failure cannot repeat as secondary"
            )

        micro_metrics = (
            (
                self.required_fact_satisfaction,
                self.required_fact_satisfied_count,
                self.required_fact_count,
                "required_fact_satisfaction",
            ),
            (
                self.gold_recall_at_k,
                self.gold_retrieved_required_evidence_count,
                self.gold_required_evidence_count,
                "gold_recall_at_k",
            ),
            (
                self.required_evidence_context_inclusion,
                self.context_included_required_evidence_count,
                self.context_required_evidence_count,
                "required_evidence_context_inclusion",
            ),
        )

        for (
            ratio,
            numerator,
            denominator,
            metric_id,
        ) in micro_metrics:
            supplied = (
                ratio is not None,
                numerator is not None,
                denominator is not None,
            )

            if any(supplied) and not all(supplied):
                raise ValueError(
                    f"{metric_id} requires ratio, numerator, "
                    "and denominator together"
                )

            if not all(supplied):
                continue

            assert ratio is not None
            assert numerator is not None
            assert denominator is not None

            if numerator > denominator:
                raise ValueError(
                    f"{metric_id} numerator cannot exceed denominator"
                )

            expected_ratio = numerator / denominator

            if abs(ratio - expected_ratio) > 1e-12:
                raise ValueError(
                    f"{metric_id} ratio does not reconcile "
                    "with numerator and denominator"
                )

        return self


@dataclass(frozen=True, slots=True)
class _FailureCandidate:
    label: FailureLabel
    precedence: int


_FAILURE_PRECEDENCE = {
    FailureLabel.RETRIEVAL_MISS: 10,
    FailureLabel.CONTEXT_EXCLUSION: 20,
    FailureLabel.PROVIDER_TIMEOUT: 30,
    FailureLabel.PROVIDER_MALFORMED_RESPONSE: 31,
    FailureLabel.CITATION_MISSING: 40,
    FailureLabel.CITATION_NOT_SUPPORTED: 41,
    FailureLabel.UNSAFE_ANSWER: 50,
    FailureLabel.UNSAFE_REFUSAL: 51,
    FailureLabel.UNSUPPORTED_ANSWER: 60,
    FailureLabel.TRACE_INCOMPLETE: 70,
}

_NORMAL_STAGES = (
    TraceStage.RETRIEVAL,
    TraceStage.FILTERING,
    TraceStage.CONTEXT_ASSEMBLY,
    TraceStage.PROVIDER_GENERATION,
    TraceStage.CITATION_VALIDATION,
)

_ERROR_STAGE = {
    RuntimeErrorCode.RETRIEVAL_ERROR: TraceStage.RETRIEVAL,
    RuntimeErrorCode.SOURCE_POLICY_ERROR: TraceStage.FILTERING,
    RuntimeErrorCode.CONTEXT_BUILD_ERROR: TraceStage.CONTEXT_ASSEMBLY,
    RuntimeErrorCode.PROVIDER_TIMEOUT: TraceStage.PROVIDER_GENERATION,
    RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE: (
        TraceStage.PROVIDER_GENERATION
    ),
    RuntimeErrorCode.CITATION_VALIDATION_ERROR: (
        TraceStage.CITATION_VALIDATION
    ),
}

_RUNTIME_ERROR_FAILURE = {
    RuntimeErrorCode.CONTEXT_BUILD_ERROR: FailureLabel.CONTEXT_EXCLUSION,
    RuntimeErrorCode.PROVIDER_TIMEOUT: FailureLabel.PROVIDER_TIMEOUT,
    RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE: (
        FailureLabel.PROVIDER_MALFORMED_RESPONSE
    ),
}


def _is_answer_case(case: EvaluationCase) -> bool:
    return case.expected_response_mode is not ResponseMode.REFUSE


def _stage_event(
    execution: PipelineExecution,
    stage: TraceStage,
) -> TraceEvent | None:
    matches = tuple(
        event
        for event in execution.trace.events
        if event.stage is stage
    )

    if len(matches) > 1:
        raise Phase5ScoringError(
            f"trace contains duplicate {stage.value} events"
        )

    return matches[0] if matches else None


def _stage_evidence_ids(
    execution: PipelineExecution,
    stage: TraceStage,
) -> set[str]:
    event = _stage_event(
        execution,
        stage,
    )

    if event is None:
        return set()

    return set(event.evidence_ids)


def _trace_complete(
    execution: PipelineExecution,
) -> bool:
    events = execution.trace.events
    stages = tuple(event.stage for event in events)
    statuses = tuple(event.status for event in events)
    outcome = execution.outcome

    if isinstance(outcome, AnswerOutcome):
        return (
            stages == _NORMAL_STAGES
            and all(
                status is TraceStatus.OK
                for status in statuses
            )
        )

    if isinstance(outcome, ErrorOutcome):
        failure_stage = _ERROR_STAGE[outcome.error_code]
        failure_index = _NORMAL_STAGES.index(
            failure_stage
        )
        expected_stages = _NORMAL_STAGES[
            : failure_index + 1
        ]

        return (
            stages == expected_stages
            and all(
                status is TraceStatus.OK
                for status in statuses[:-1]
            )
            and statuses[-1] is TraceStatus.ERROR
        )

    if isinstance(outcome, RefusalOutcome):
        no_evidence_path = (
            TraceStage.RETRIEVAL,
            TraceStage.FILTERING,
            TraceStage.REFUSAL_FALLBACK,
        )
        provider_refusal_path = (
            TraceStage.RETRIEVAL,
            TraceStage.FILTERING,
            TraceStage.CONTEXT_ASSEMBLY,
            TraceStage.PROVIDER_GENERATION,
            TraceStage.REFUSAL_FALLBACK,
        )
        citation_refusal_path = (
            *_NORMAL_STAGES,
            TraceStage.REFUSAL_FALLBACK,
        )

        if stages == no_evidence_path:
            return statuses == (
                TraceStatus.OK,
                TraceStatus.OK,
                TraceStatus.REFUSED,
            )

        if stages == provider_refusal_path:
            return statuses == (
                TraceStatus.OK,
                TraceStatus.OK,
                TraceStatus.OK,
                TraceStatus.REFUSED,
                TraceStatus.REFUSED,
            )

        if stages == citation_refusal_path:
            return statuses == (
                TraceStatus.OK,
                TraceStatus.OK,
                TraceStatus.OK,
                TraceStatus.OK,
                TraceStatus.REFUSED,
                TraceStatus.REFUSED,
            )

    return False


def _fact_satisfaction(
    case: EvaluationCase,
    assessment: Phase5FactAssessmentSet,
) -> float:
    if assessment.case_id != case.case_id:
        raise Phase5ScoringError(
            "fact assessment case_id does not match evaluation case"
        )

    required_ids = set(case.required_fact_ids)
    observed_ids = {
        verdict.fact_id
        for verdict in assessment.verdicts
    }

    if observed_ids != required_ids:
        raise Phase5ScoringError(
            "fact assessment must exactly cover required_fact_ids"
        )

    satisfied_count = sum(
        verdict.verdict == "satisfied"
        for verdict in assessment.verdicts
    )

    return satisfied_count / len(required_ids)


def _citation_metrics(
    case: EvaluationCase,
    outcome: AnswerOutcome,
) -> tuple[float, float]:
    statuses = {
        check.evidence_id: check.status
        for check in outcome.citation_validation.checks
    }

    cited_ids = set(outcome.cited_evidence_ids)

    supported_count = sum(
        statuses.get(evidence_id)
        is CitationValidationStatus.SUPPORTED
        for evidence_id in cited_ids
    )

    precision = (
        supported_count / len(cited_ids)
        if cited_ids
        else 0.0
    )

    required_ids = set(case.required_evidence_ids)

    recall = (
        len(required_ids & cited_ids)
        / len(required_ids)
    )

    return precision, recall


def _candidate(
    label: FailureLabel,
) -> _FailureCandidate:
    return _FailureCandidate(
        label=label,
        precedence=_FAILURE_PRECEDENCE[label],
    )


def _ordered_failures(
    candidates: list[_FailureCandidate],
) -> tuple[
    FailureLabel | None,
    tuple[FailureLabel, ...],
]:
    by_label: dict[
        FailureLabel,
        _FailureCandidate,
    ] = {}

    for candidate in candidates:
        by_label.setdefault(
            candidate.label,
            candidate,
        )

    ordered = tuple(
        candidate.label
        for candidate in sorted(
            by_label.values(),
            key=lambda item: (
                item.precedence,
                item.label.value,
            ),
        )
    )

    if not ordered:
        return None, ()

    return ordered[0], ordered[1:]


def score_phase5_case(
    case: EvaluationCase,
    execution: PipelineExecution,
    fact_assessment: Phase5FactAssessmentSet | None = None,
) -> Phase5CaseScore:
    """Score one already-executed case without invoking runtime or provider."""

    answer_case = _is_answer_case(case)
    outcome = execution.outcome
    trace_complete = _trace_complete(execution)

    latency_ms = sum(
        event.duration_ms
        for event in execution.trace.events
    )

    provider_attempt_count = sum(
        event.stage is TraceStage.PROVIDER_GENERATION
        for event in execution.trace.events
    )

    candidates: list[_FailureCandidate] = []
    unresolved_reason: str | None = None

    strict_answer_success: bool | None = None
    required_fact_satisfaction: float | None = None
    gold_recall_at_k: float | None = None
    context_inclusion: float | None = None

    required_fact_satisfied_count: int | None = None
    required_fact_count: int | None = None

    gold_retrieved_count: int | None = None
    gold_required_count: int | None = None

    context_included_count: int | None = None
    context_required_count: int | None = None

    claim_support: bool | None = None
    citation_precision: float | None = None
    citation_recall: float | None = None
    correct_refusal: bool | None = None
    over_refusal: bool | None = None

    if answer_case:
        if fact_assessment is None:
            raise Phase5ScoringError(
                "answer case requires complete fact assessment"
            )

        required_fact_count = len(
            case.required_fact_ids
        )
        required_fact_satisfied_count = sum(
            verdict.verdict == "satisfied"
            for verdict in fact_assessment.verdicts
        )

        required_fact_satisfaction = _fact_satisfaction(
            case,
            fact_assessment,
        )

        required_evidence = set(
            case.required_evidence_ids
        )

        retrieval_ids = _stage_evidence_ids(
            execution,
            TraceStage.RETRIEVAL,
        )
        context_ids = _stage_evidence_ids(
            execution,
            TraceStage.CONTEXT_ASSEMBLY,
        )

        gold_required_count = len(
            required_evidence
        )
        gold_retrieved_count = len(
            required_evidence & retrieval_ids
        )

        context_required_count = len(
            required_evidence
        )
        context_included_count = len(
            required_evidence & context_ids
        )

        gold_recall_at_k = (
            gold_retrieved_count
            / gold_required_count
        )

        context_inclusion = (
            context_included_count
            / context_required_count
        )

        if gold_recall_at_k < 1.0:
            candidates.append(
                _candidate(
                    FailureLabel.RETRIEVAL_MISS
                )
            )

        if context_inclusion < 1.0:
            candidates.append(
                _candidate(
                    FailureLabel.CONTEXT_EXCLUSION
                )
            )

        over_refusal = isinstance(
            outcome,
            RefusalOutcome,
        )

        if isinstance(outcome, AnswerOutcome):
            claim_support = (
                outcome.citation_validation
                .all_material_claims_supported
            )

            (
                citation_precision,
                citation_recall,
            ) = _citation_metrics(
                case,
                outcome,
            )

            if citation_recall < 1.0:
                candidates.append(
                    _candidate(
                        FailureLabel.CITATION_MISSING
                    )
                )

            if (
                not claim_support
                or citation_precision < 1.0
            ):
                if any(
                    check.status
                    is CitationValidationStatus.MISSING
                    for check
                    in outcome.citation_validation.checks
                ):
                    candidates.append(
                        _candidate(
                            FailureLabel.CITATION_MISSING
                        )
                    )
                else:
                    candidates.append(
                        _candidate(
                            FailureLabel.CITATION_NOT_SUPPORTED
                        )
                    )

            if required_fact_satisfaction < 1.0:
                candidates.append(
                    _candidate(
                        FailureLabel.UNSUPPORTED_ANSWER
                    )
                )

            strict_answer_success = all(
                (
                    gold_recall_at_k == 1.0,
                    context_inclusion == 1.0,
                    required_fact_satisfaction == 1.0,
                    claim_support,
                    citation_precision == 1.0,
                    citation_recall == 1.0,
                    trace_complete,
                )
            )

        elif isinstance(outcome, RefusalOutcome):
            claim_support = False
            citation_precision = 0.0
            citation_recall = 0.0
            strict_answer_success = False

            if (
                outcome.reason
                is RefusalReason.UNSUPPORTED_CITATION
                and execution.trace.primary_failure
                in {
                    FailureLabel.CITATION_MISSING,
                    FailureLabel.CITATION_NOT_SUPPORTED,
                }
            ):
                candidates.append(
                    _candidate(
                        execution.trace.primary_failure
                    )
                )

            candidates.append(
                _candidate(
                    FailureLabel.UNSAFE_REFUSAL
                )
            )

        elif isinstance(outcome, ErrorOutcome):
            claim_support = False
            citation_precision = 0.0
            citation_recall = 0.0
            strict_answer_success = False

            mapped = _RUNTIME_ERROR_FAILURE.get(
                outcome.error_code
            )

            if mapped is None:
                unresolved_reason = (
                    "no frozen FailureLabel mapping for "
                    f"runtime error {outcome.error_code.value}"
                )
            else:
                candidates.append(
                    _candidate(mapped)
                )

    else:
        if fact_assessment is not None:
            raise Phase5ScoringError(
                "refusal case cannot carry fact assessment"
            )

        correct_refusal = (
            isinstance(outcome, RefusalOutcome)
            and outcome.reason.value
            == case.must_refuse_reason
        )

        if isinstance(outcome, AnswerOutcome):
            candidates.append(
                _candidate(
                    FailureLabel.UNSAFE_ANSWER
                )
            )

        elif isinstance(outcome, RefusalOutcome):
            if not correct_refusal:
                if (
                    outcome.reason
                    is RefusalReason.UNSUPPORTED_CITATION
                    and execution.trace.primary_failure
                    in {
                        FailureLabel.CITATION_MISSING,
                        FailureLabel.CITATION_NOT_SUPPORTED,
                    }
                ):
                    candidates.append(
                        _candidate(
                            execution.trace.primary_failure
                        )
                    )

                candidates.append(
                    _candidate(
                        FailureLabel.UNSAFE_REFUSAL
                    )
                )

        elif isinstance(outcome, ErrorOutcome):
            mapped = _RUNTIME_ERROR_FAILURE.get(
                outcome.error_code
            )

            if mapped is None:
                unresolved_reason = (
                    "no frozen FailureLabel mapping for "
                    f"runtime error {outcome.error_code.value}"
                )
            else:
                candidates.append(
                    _candidate(mapped)
                )

    if not trace_complete:
        candidates.append(
            _candidate(
                FailureLabel.TRACE_INCOMPLETE
            )
        )

    primary_failure, secondary_failures = (
        _ordered_failures(candidates)
    )

    expected_empty_retrieval_refusal = (
        not answer_case
        and correct_refusal is True
        and execution.trace.primary_failure
        is FailureLabel.RETRIEVAL_MISS
    )

    classified_labels = {
        label
        for label in (
            primary_failure,
            *secondary_failures,
        )
        if label is not None
    }

    if (
        execution.trace.primary_failure is not None
        and execution.trace.primary_failure
        not in classified_labels
        and not expected_empty_retrieval_refusal
        and unresolved_reason is None
    ):
        unresolved_reason = (
            "runtime primary_failure did not reconcile "
            "with evaluator-derived failures: "
            f"{execution.trace.primary_failure.value}"
        )

    critical_contribution = int(
        case.criticality is Criticality.CRITICAL
        and primary_failure is not None
    )

    return Phase5CaseScore(
        case_id=case.case_id,
        expected_response_mode=(
            case.expected_response_mode
        ),
        actual_status=RuntimeOutcomeStatus(
            outcome.status
        ),
        strict_answer_success=strict_answer_success,
        required_fact_satisfaction=(
            required_fact_satisfaction
        ),
        gold_recall_at_k=gold_recall_at_k,
        required_evidence_context_inclusion=(
            context_inclusion
        ),
        required_fact_satisfied_count=(
            required_fact_satisfied_count
        ),
        required_fact_count=required_fact_count,
        gold_retrieved_required_evidence_count=(
            gold_retrieved_count
        ),
        gold_required_evidence_count=(
            gold_required_count
        ),
        context_included_required_evidence_count=(
            context_included_count
        ),
        context_required_evidence_count=(
            context_required_count
        ),
        claim_support=claim_support,
        citation_precision=citation_precision,
        citation_recall=citation_recall,
        correct_refusal=correct_refusal,
        over_refusal=over_refusal,
        trace_completeness=trace_complete,
        latency_ms=latency_ms,
        provider_attempt_count=(
            provider_attempt_count
        ),
        primary_failure=primary_failure,
        secondary_failures=secondary_failures,
        classification_complete=(
            unresolved_reason is None
        ),
        unresolved_failure_reason=(
            unresolved_reason
        ),
        critical_failure_count_contribution=(
            critical_contribution
        ),
    )
