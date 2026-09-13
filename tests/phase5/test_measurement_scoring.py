from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CitationValidationStatus,
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    FailureLabel,
    RefusalReason,
    ResponseMode,
    ScenarioClass,
    SourceState,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import (
    EvaluationCase,
)
from rag_reliability.contracts.runtime import (
    AnswerOutcome,
    CitationCheck,
    CitationValidationResult,
    RefusalOutcome,
)
from rag_reliability.contracts.tracing import (
    TraceEvent,
    TraceRecord,
)
from rag_reliability.evaluation.measurement_instrument import (
    Phase5FactAssessmentSet,
    Phase5FactVerdict,
)
from rag_reliability.evaluation.measurement_scoring import (
    Phase5ScoringError,
    score_phase5_case,
)
from rag_reliability.runtime.models import (
    PipelineExecution,
)

_NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _answer_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="synthetic-answer-case",
        case_version="synthetic-v1",
        data_role=EvaluationRole.DEVELOPMENT,
        source_family=EvaluationSourceFamily.ISSUES,
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        criticality=Criticality.CRITICAL,
        query="Synthetic answer query?",
        expected_response_mode=ResponseMode.ANSWER,
        required_fact_ids=("fact-1",),
        required_evidence_ids=("evidence-1",),
        required_source_ids=("source-1",),
        allowed_source_states=(SourceState.CURRENT,),
        required_api_version="2026-03-10",
        required_authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        gold_fact_rubric=("Expected semantic fact.",),
        scoring_notes="Synthetic scorer fixture.",
        authoring_evidence=("synthetic:fixture",),
    )


def _refusal_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="synthetic-refusal-case",
        case_version="synthetic-v1",
        data_role=EvaluationRole.DEVELOPMENT,
        source_family=EvaluationSourceFamily.ISSUES,
        scenario_class=(
            ScenarioClass
            .MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        criticality=Criticality.CRITICAL,
        query="Synthetic unanswerable query?",
        expected_response_mode=ResponseMode.REFUSE,
        allowed_source_states=(SourceState.CURRENT,),
        required_api_version="2026-03-10",
        required_authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        must_refuse_reason=(
            RefusalReason.INSUFFICIENT_EVIDENCE.value
        ),
        scoring_notes="Synthetic refusal fixture.",
        authoring_evidence=("synthetic:fixture",),
    )


def _event(
    case_id: str,
    sequence: int,
    stage: TraceStage,
    status: TraceStatus,
    *,
    evidence_ids: tuple[str, ...] = (),
) -> TraceEvent:
    return TraceEvent(
        event_id=f"{case_id}:{sequence}:{stage.value}",
        stage=stage,
        status=status,
        occurred_at=(
            _NOW + timedelta(milliseconds=sequence)
        ),
        duration_ms=1.0,
        evidence_ids=evidence_ids,
    )


def _execution(
    case_id: str,
    outcome: AnswerOutcome | RefusalOutcome,
    events: tuple[TraceEvent, ...],
    *,
    primary_failure: FailureLabel | None = None,
) -> PipelineExecution:
    return PipelineExecution(
        outcome=outcome,
        trace=TraceRecord(
            trace_id=f"trace:{case_id}",
            case_id=case_id,
            configuration_id="synthetic-config",
            started_at=_NOW,
            ended_at=_NOW + timedelta(seconds=1),
            events=events,
            primary_failure=primary_failure,
        ),
    )


def _supported_answer(
    cited_evidence_id: str,
) -> AnswerOutcome:
    return AnswerOutcome(
        answer_text="Synthetic answer.",
        cited_evidence_ids=(cited_evidence_id,),
        citation_validation=(
            CitationValidationResult(
                checks=(
                    CitationCheck(
                        evidence_id=cited_evidence_id,
                        status=(
                            CitationValidationStatus.SUPPORTED
                        ),
                    ),
                ),
                all_material_claims_supported=True,
            )
        ),
    )


def _satisfied_assessment(
    case_id: str,
) -> Phase5FactAssessmentSet:
    return Phase5FactAssessmentSet(
        case_id=case_id,
        verdicts=(
            Phase5FactVerdict(
                fact_id="fact-1",
                verdict="satisfied",
                supporting_answer_span=(
                    "Synthetic answer."
                ),
            ),
        ),
    )


def _unsatisfied_assessment(
    case_id: str,
) -> Phase5FactAssessmentSet:
    return Phase5FactAssessmentSet(
        case_id=case_id,
        verdicts=(
            Phase5FactVerdict(
                fact_id="fact-1",
                verdict="not_satisfied",
                rationale="Required fact absent.",
            ),
        ),
    )


def test_earliest_supported_failure_wins() -> None:
    case = _answer_case()

    execution = _execution(
        case.case_id,
        _supported_answer("evidence-2"),
        (
            _event(
                case.case_id,
                1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
                evidence_ids=("evidence-2",),
            ),
            _event(
                case.case_id,
                2,
                TraceStage.FILTERING,
                TraceStatus.OK,
                evidence_ids=("evidence-2",),
            ),
            _event(
                case.case_id,
                3,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStatus.OK,
                evidence_ids=("evidence-2",),
            ),
            _event(
                case.case_id,
                4,
                TraceStage.PROVIDER_GENERATION,
                TraceStatus.OK,
                evidence_ids=("evidence-2",),
            ),
        ),
    )

    score = score_phase5_case(
        case,
        execution,
        _unsatisfied_assessment(case.case_id),
    )

    assert (
        score.primary_failure
        is FailureLabel.RETRIEVAL_MISS
    )

    assert score.secondary_failures == (
        FailureLabel.CONTEXT_EXCLUSION,
        FailureLabel.CITATION_MISSING,
        FailureLabel.UNSUPPORTED_ANSWER,
        FailureLabel.TRACE_INCOMPLETE,
    )


def test_trace_incomplete_does_not_mask_earlier_failure() -> None:
    case = _answer_case()

    execution = _execution(
        case.case_id,
        _supported_answer("evidence-1"),
        (
            _event(
                case.case_id,
                1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                2,
                TraceStage.FILTERING,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                3,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStatus.OK,
                evidence_ids=(),
            ),
            _event(
                case.case_id,
                4,
                TraceStage.PROVIDER_GENERATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
        ),
    )

    score = score_phase5_case(
        case,
        execution,
        _satisfied_assessment(case.case_id),
    )

    assert (
        score.primary_failure
        is FailureLabel.CONTEXT_EXCLUSION
    )
    assert (
        FailureLabel.TRACE_INCOMPLETE
        in score.secondary_failures
    )


def test_expected_empty_retrieval_refusal_is_not_failure() -> None:
    case = _refusal_case()

    execution = _execution(
        case.case_id,
        RefusalOutcome(
            reason=RefusalReason.INSUFFICIENT_EVIDENCE,
            message="No eligible evidence.",
        ),
        (
            _event(
                case.case_id,
                1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
            ),
            _event(
                case.case_id,
                2,
                TraceStage.FILTERING,
                TraceStatus.OK,
            ),
            _event(
                case.case_id,
                3,
                TraceStage.REFUSAL_FALLBACK,
                TraceStatus.REFUSED,
            ),
        ),
        primary_failure=FailureLabel.RETRIEVAL_MISS,
    )

    score = score_phase5_case(
        case,
        execution,
    )

    assert score.correct_refusal is True
    assert score.trace_completeness is True
    assert score.primary_failure is None
    assert score.secondary_failures == ()
    assert score.classification_complete is True
    assert (
        score.critical_failure_count_contribution
        == 0
    )


def test_fact_assessment_requires_exact_fact_ids() -> None:
    case = _answer_case()

    execution = _execution(
        case.case_id,
        _supported_answer("evidence-1"),
        (
            _event(
                case.case_id,
                1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                2,
                TraceStage.FILTERING,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                3,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                4,
                TraceStage.PROVIDER_GENERATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                5,
                TraceStage.CITATION_VALIDATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
        ),
    )

    wrong_assessment = Phase5FactAssessmentSet(
        case_id=case.case_id,
        verdicts=(
            Phase5FactVerdict(
                fact_id="wrong-fact",
                verdict="satisfied",
                supporting_answer_span="Synthetic answer.",
            ),
        ),
    )

    with pytest.raises(
        Phase5ScoringError,
        match="exactly cover required_fact_ids",
    ):
        score_phase5_case(
            case,
            execution,
            wrong_assessment,
        )


def test_clean_answer_has_no_failure() -> None:
    case = _answer_case()

    execution = _execution(
        case.case_id,
        _supported_answer("evidence-1"),
        (
            _event(
                case.case_id,
                1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                2,
                TraceStage.FILTERING,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                3,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                4,
                TraceStage.PROVIDER_GENERATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                5,
                TraceStage.CITATION_VALIDATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
        ),
    )

    score = score_phase5_case(
        case,
        execution,
        _satisfied_assessment(case.case_id),
    )

    assert score.strict_answer_success is True
    assert score.required_fact_satisfaction == 1.0
    assert score.gold_recall_at_k == 1.0
    assert (
        score.required_evidence_context_inclusion
        == 1.0
    )
    assert score.required_fact_satisfied_count == 1
    assert score.required_fact_count == 1
    assert (
        score.gold_retrieved_required_evidence_count
        == 1
    )
    assert score.gold_required_evidence_count == 1
    assert (
        score.context_included_required_evidence_count
        == 1
    )
    assert score.context_required_evidence_count == 1
    assert score.claim_support is True
    assert score.citation_precision == 1.0
    assert score.citation_recall == 1.0
    assert score.over_refusal is False
    assert score.trace_completeness is True
    assert score.provider_attempt_count == 1
    assert score.primary_failure is None
    assert score.secondary_failures == ()


def test_micro_metric_ratio_must_reconcile_with_counts() -> None:
    case = _answer_case()

    execution = _execution(
        case.case_id,
        _supported_answer("evidence-1"),
        (
            _event(
                case.case_id,
                1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                2,
                TraceStage.FILTERING,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                3,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                4,
                TraceStage.PROVIDER_GENERATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
            _event(
                case.case_id,
                5,
                TraceStage.CITATION_VALIDATION,
                TraceStatus.OK,
                evidence_ids=("evidence-1",),
            ),
        ),
    )

    score = score_phase5_case(
        case,
        execution,
        _satisfied_assessment(case.case_id),
    )

    payload = score.model_dump()
    payload["required_fact_satisfaction"] = 0.5

    with pytest.raises(
        ValidationError,
        match="does not reconcile",
    ):
        type(score).model_validate(payload)
