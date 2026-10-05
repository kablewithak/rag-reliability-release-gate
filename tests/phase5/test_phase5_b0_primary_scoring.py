from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CitationValidationStatus,
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    RefusalReason,
    ResponseMode,
    ScenarioClass,
    SourceState,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import EvaluationCase
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
from rag_reliability.evaluation.b0_primary_execution import (
    Phase5B0PrimaryExecutionRecordV1,
)
from rag_reliability.evaluation.b0_primary_scoring import (
    Phase5B0PrimaryFactAssessmentPackageV1,
    Phase5B0PrimaryScoringError,
    _validate_fact_assessments,
    build_fact_assessment_template,
)
from rag_reliability.evaluation.measurement_instrument import (
    Phase5FactAssessmentSet,
    Phase5FactVerdict,
)
from rag_reliability.runtime.models import PipelineExecution

_NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _answer_case(
    case_id: str = "synthetic-answer-case",
) -> EvaluationCase:
    return EvaluationCase(
        case_id=case_id,
        case_version="synthetic-v1",
        data_role=EvaluationRole.DEVELOPMENT,
        source_family=EvaluationSourceFamily.ISSUES,
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        criticality=Criticality.NONCRITICAL,
        query="Synthetic answer query?",
        expected_response_mode=ResponseMode.ANSWER,
        required_fact_ids=(f"{case_id}:fact-01",),
        required_evidence_ids=("evidence-1",),
        required_source_ids=("source-1",),
        allowed_source_states=(SourceState.CURRENT,),
        required_api_version="2026-03-10",
        required_authority_level=(AuthorityLevel.AUTHORITATIVE),
        gold_fact_rubric=("Expected semantic fact.",),
        scoring_notes="Synthetic scorer fixture.",
        authoring_evidence=("synthetic:fixture",),
    )


def _refusal_case(
    case_id: str = "synthetic-refusal-case",
) -> EvaluationCase:
    return EvaluationCase(
        case_id=case_id,
        case_version="synthetic-v1",
        data_role=EvaluationRole.TUNING,
        source_family=EvaluationSourceFamily.ISSUES,
        scenario_class=(ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE),
        criticality=Criticality.CRITICAL,
        query="Synthetic unanswerable query?",
        expected_response_mode=ResponseMode.REFUSE,
        allowed_source_states=(SourceState.CURRENT,),
        required_api_version="2026-03-10",
        required_authority_level=(AuthorityLevel.AUTHORITATIVE),
        must_refuse_reason=(RefusalReason.INSUFFICIENT_EVIDENCE.value),
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
        event_id=(f"{case_id}:{sequence}:{stage.value}"),
        stage=stage,
        status=status,
        occurred_at=(_NOW + timedelta(milliseconds=sequence)),
        duration_ms=1.0,
        evidence_ids=evidence_ids,
    )


def _answer_execution(
    case_id: str,
) -> PipelineExecution:
    outcome = AnswerOutcome(
        answer_text="Synthetic answer.",
        cited_evidence_ids=("evidence-1",),
        citation_validation=(
            CitationValidationResult(
                checks=(
                    CitationCheck(
                        evidence_id=("evidence-1"),
                        status=(CitationValidationStatus.SUPPORTED),
                    ),
                ),
                all_material_claims_supported=True,
            )
        ),
    )

    events = (
        _event(
            case_id,
            1,
            TraceStage.RETRIEVAL,
            TraceStatus.OK,
            evidence_ids=("evidence-1",),
        ),
        _event(
            case_id,
            2,
            TraceStage.FILTERING,
            TraceStatus.OK,
            evidence_ids=("evidence-1",),
        ),
        _event(
            case_id,
            3,
            TraceStage.CONTEXT_ASSEMBLY,
            TraceStatus.OK,
            evidence_ids=("evidence-1",),
        ),
        _event(
            case_id,
            4,
            TraceStage.PROVIDER_GENERATION,
            TraceStatus.OK,
            evidence_ids=("evidence-1",),
        ),
        _event(
            case_id,
            5,
            TraceStage.CITATION_VALIDATION,
            TraceStatus.OK,
            evidence_ids=("evidence-1",),
        ),
    )

    return PipelineExecution(
        outcome=outcome,
        trace=TraceRecord(
            trace_id=f"trace:{case_id}",
            case_id=case_id,
            configuration_id="synthetic-config",
            started_at=_NOW,
            ended_at=(_NOW + timedelta(seconds=1)),
            events=events,
        ),
    )


def _refusal_execution(
    case_id: str,
) -> PipelineExecution:
    outcome = RefusalOutcome(
        reason=(RefusalReason.INSUFFICIENT_EVIDENCE),
        message="No eligible evidence.",
    )

    events = (
        _event(
            case_id,
            1,
            TraceStage.RETRIEVAL,
            TraceStatus.OK,
        ),
        _event(
            case_id,
            2,
            TraceStage.FILTERING,
            TraceStatus.OK,
        ),
        _event(
            case_id,
            3,
            TraceStage.REFUSAL_FALLBACK,
            TraceStatus.REFUSED,
        ),
    )

    return PipelineExecution(
        outcome=outcome,
        trace=TraceRecord(
            trace_id=f"trace:{case_id}",
            case_id=case_id,
            configuration_id="synthetic-config",
            started_at=_NOW,
            ended_at=(_NOW + timedelta(seconds=1)),
            events=events,
        ),
    )


def _record(
    *,
    slot_id: str,
    ordinal: int,
    case: EvaluationCase,
    execution: PipelineExecution,
) -> Phase5B0PrimaryExecutionRecordV1:
    role = (
        "evaluation_development_case"
        if (case.data_role is EvaluationRole.DEVELOPMENT)
        else "intervention_tuning_case"
    )

    return Phase5B0PrimaryExecutionRecordV1(
        slot_id=slot_id,
        ordinal=ordinal,
        case_id=case.case_id,
        role=role,
        query_sha256=(hashlib.sha256(case.query.encode()).hexdigest()),
        execution=execution,
    )


def _satisfied_assessment(
    case: EvaluationCase,
) -> Phase5FactAssessmentSet:
    return Phase5FactAssessmentSet(
        case_id=case.case_id,
        verdicts=(
            Phase5FactVerdict(
                fact_id=(case.required_fact_ids[0]),
                verdict="satisfied",
                supporting_answer_span=("Synthetic answer."),
            ),
        ),
    )


def test_fact_template_contains_answer_cases_only() -> None:
    answer_case = _answer_case()
    refusal_case = _refusal_case()

    template = build_fact_assessment_template(
        raw_batch_sha256="a" * 64,
        cases=(
            answer_case,
            refusal_case,
        ),
        records=(
            _record(
                slot_id="slot-1",
                ordinal=1,
                case=answer_case,
                execution=(_answer_execution(answer_case.case_id)),
            ),
            _record(
                slot_id="slot-2",
                ordinal=2,
                case=refusal_case,
                execution=(_refusal_execution(refusal_case.case_id)),
            ),
        ),
    )

    assert template.answer_case_count == 1
    assert len(template.cases) == 1

    item = template.cases[0]

    assert item.case_id == answer_case.case_id
    assert item.actual_status == "answer"
    assert item.answer_text == "Synthetic answer."
    assert item.outcome_message is None
    assert item.facts[0].fact_id == (answer_case.required_fact_ids[0])
    assert item.facts[0].rubric == ("Expected semantic fact.")


def test_fact_template_preserves_nonanswer_outcome() -> None:
    case = _answer_case("synthetic-answer-refused")

    template = build_fact_assessment_template(
        raw_batch_sha256="b" * 64,
        cases=(case,),
        records=(
            _record(
                slot_id="slot-1",
                ordinal=1,
                case=case,
                execution=(_refusal_execution(case.case_id)),
            ),
        ),
    )

    item = template.cases[0]

    assert item.actual_status == "refusal"
    assert item.answer_text is None
    assert item.outcome_message == ("No eligible evidence.")


def test_fact_assessment_requires_raw_batch_binding() -> None:
    case = _answer_case()

    package = Phase5B0PrimaryFactAssessmentPackageV1(
        primary_raw_batch_sha256=("c" * 64),
        evaluator_provenance=("synthetic-test"),
        assessments=(_satisfied_assessment(case),),
    )

    with pytest.raises(
        Phase5B0PrimaryScoringError,
        match="not bound",
    ):
        _validate_fact_assessments(
            package=package,
            raw_batch_sha256=("d" * 64),
            cases=(case,),
        )


def test_fact_assessment_requires_exact_answer_case_set() -> None:
    first = _answer_case("synthetic-answer-one")
    second = _answer_case("synthetic-answer-two")

    package = Phase5B0PrimaryFactAssessmentPackageV1(
        primary_raw_batch_sha256=("e" * 64),
        evaluator_provenance=("synthetic-test"),
        assessments=(_satisfied_assessment(first),),
    )

    with pytest.raises(
        Phase5B0PrimaryScoringError,
        match="exactly cover",
    ):
        _validate_fact_assessments(
            package=package,
            raw_batch_sha256=("e" * 64),
            cases=(
                first,
                second,
            ),
        )
