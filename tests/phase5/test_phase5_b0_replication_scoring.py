from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import (
    CitationValidationStatus,
    EvaluationRole,
    ResponseMode,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import (
    AnswerOutcome,
    CitationCheck,
    CitationValidationResult,
)
from rag_reliability.contracts.tracing import TraceEvent, TraceRecord
from rag_reliability.evaluation.b0_authorization_models import (
    Phase5B0SpecimenV1,
    stable_model_bytes,
)
from rag_reliability.evaluation.b0_replication_execution import (
    Phase5B0ReplicationExecutionRecordV1,
    Phase5B0ReplicationRawBatchV1,
)
from rag_reliability.evaluation.b0_replication_scoring import (
    Phase5B0ReplicationFactAssessmentPackageV1,
    Phase5B0ReplicationScoringError,
    Phase5B0ReplicationScoringReceiptV1,
    _ordered_cases_and_clusters,
    _validate_fact_assessments,
    _validate_scoring_population,
    build_fact_assessment_template,
    score_replication_with_objects,
)
from rag_reliability.evaluation.development_cases import Phase4DevelopmentCaseSuite
from rag_reliability.evaluation.measurement_instrument import (
    Phase5FactAssessmentSet,
    Phase5FactVerdict,
)
from rag_reliability.evaluation.tuning_cases import Phase4TuningCaseSuite
from rag_reliability.runtime.models import PipelineExecution

ROOT = Path(__file__).resolve().parents[2]
_NOW = datetime(2026, 1, 1, tzinfo=UTC)


@lru_cache(maxsize=1)
def _public_objects() -> tuple[
    Phase5B0SpecimenV1,
    tuple[EvaluationCase, ...],
    dict[str, str],
]:
    specimen = Phase5B0SpecimenV1.model_validate_json(
        (ROOT / "artifacts" / "development" / "phase5_b0_specimen_v1.json").read_bytes()
    )
    development = Phase4DevelopmentCaseSuite.model_validate_json(
        (ROOT / "artifacts" / "development" / "phase4c_development_cases_v1.json").read_bytes()
    )
    tuning = Phase4TuningCaseSuite.model_validate_json(
        (ROOT / "artifacts" / "development" / "phase4c_tuning_cases_v1.json").read_bytes()
    )
    cases, clusters = _ordered_cases_and_clusters(
        specimen,
        development,
        tuning,
    )
    return specimen, cases, clusters


def _event(
    case_id: str,
    sequence: int,
    stage: TraceStage,
    *,
    evidence_ids: tuple[str, ...],
) -> TraceEvent:
    return TraceEvent(
        event_id=f"{case_id}:{sequence}:{stage.value}",
        stage=stage,
        status=TraceStatus.OK,
        occurred_at=_NOW + timedelta(milliseconds=sequence),
        duration_ms=1.0,
        evidence_ids=evidence_ids,
    )


def _answer_execution(
    *,
    case_id: str,
    configuration_id: str,
    cited_evidence_ids: tuple[str, ...],
) -> PipelineExecution:
    checks = tuple(
        CitationCheck(
            evidence_id=evidence_id,
            status=CitationValidationStatus.SUPPORTED,
        )
        for evidence_id in cited_evidence_ids
    )
    outcome = AnswerOutcome(
        answer_text="Synthetic answer.",
        cited_evidence_ids=cited_evidence_ids,
        citation_validation=CitationValidationResult(
            checks=checks,
            all_material_claims_supported=True,
        ),
    )

    events = tuple(
        _event(
            case_id,
            sequence,
            stage,
            evidence_ids=cited_evidence_ids,
        )
        for sequence, stage in enumerate(
            (
                TraceStage.RETRIEVAL,
                TraceStage.FILTERING,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStage.PROVIDER_GENERATION,
                TraceStage.CITATION_VALIDATION,
            ),
            start=1,
        )
    )

    return PipelineExecution(
        outcome=outcome,
        trace=TraceRecord(
            trace_id=f"trace:{case_id}",
            case_id=case_id,
            configuration_id=configuration_id,
            started_at=_NOW,
            ended_at=_NOW + timedelta(seconds=1),
            events=events,
        ),
    )


def _synthetic_records(
    specimen: Phase5B0SpecimenV1,
    cases: tuple[EvaluationCase, ...],
) -> tuple[Phase5B0ReplicationExecutionRecordV1, ...]:
    records: list[Phase5B0ReplicationExecutionRecordV1] = []

    for ordinal, case in enumerate(cases, start=1):
        role = case.data_role.value
        records.append(
            Phase5B0ReplicationExecutionRecordV1(
                slot_id=f"replication:{case.case_id}",
                ordinal=ordinal,
                case_id=case.case_id,
                role=role,
                query_sha256=hashlib.sha256(case.query.encode()).hexdigest(),
                execution=_answer_execution(
                    case_id=case.case_id,
                    configuration_id=specimen.runtime_configuration_id,
                    cited_evidence_ids=tuple(case.required_evidence_ids),
                ),
            )
        )

    return tuple(records)


def _fact_package(
    *,
    raw_batch_sha256: str,
    cases: tuple[EvaluationCase, ...],
) -> Phase5B0ReplicationFactAssessmentPackageV1:
    assessments = tuple(
        Phase5FactAssessmentSet(
            case_id=case.case_id,
            verdicts=tuple(
                Phase5FactVerdict(
                    fact_id=fact_id,
                    verdict="satisfied",
                    supporting_answer_span="Synthetic answer.",
                )
                for fact_id in case.required_fact_ids
            ),
        )
        for case in cases
        if case.expected_response_mode is not ResponseMode.REFUSE
    )

    return Phase5B0ReplicationFactAssessmentPackageV1(
        replication_raw_batch_sha256=raw_batch_sha256,
        evaluator_provenance="synthetic-public-safe-qualification",
        assessments=assessments,
    )


def _synthetic_raw_batch(
    specimen: Phase5B0SpecimenV1,
    cases: tuple[EvaluationCase, ...],
) -> Phase5B0ReplicationRawBatchV1:
    records = _synthetic_records(specimen, cases)

    return Phase5B0ReplicationRawBatchV1(
        execution_commit_sha="a" * 40,
        runner_source_sha256="b" * 64,
        index_loader_source_sha256="c" * 64,
        started_slot_count=42,
        terminal_record_count=42,
        unreconciled_started_slot_count=0,
        records=records,
        stop_triggered=False,
        batch_decision="COMPLETE",
        batch_complete=True,
    )


def test_fact_template_is_replication_bound_and_fresh_only() -> None:
    specimen, cases, _clusters = _public_objects()
    raw = _synthetic_raw_batch(specimen, cases)
    raw_sha = hashlib.sha256(stable_model_bytes(raw)).hexdigest()

    template = build_fact_assessment_template(
        raw_batch_sha256=raw_sha,
        cases=cases,
        records=raw.records,
    )

    expected_answer_count = sum(
        case.expected_response_mode is not ResponseMode.REFUSE for case in cases
    )

    assert template.replication_raw_batch_sha256 == raw_sha
    assert template.answer_case_count == expected_answer_count
    assert len(template.cases) == expected_answer_count
    assert template.semantic_assessment_origin == "fresh_replication_adjudication"
    assert template.primary_semantic_verdicts_reused is False
    assert template.private_evidence_only is True
    assert template.held_out_outcomes_exposed is False


def test_fact_assessment_requires_replication_raw_batch_binding() -> None:
    _specimen, cases, _clusters = _public_objects()

    package = _fact_package(
        raw_batch_sha256="d" * 64,
        cases=cases,
    )

    with pytest.raises(
        Phase5B0ReplicationScoringError,
        match="not bound",
    ):
        _validate_fact_assessments(
            package=package,
            raw_batch_sha256="e" * 64,
            cases=cases,
        )


def test_fact_assessment_requires_exact_answer_case_set() -> None:
    _specimen, cases, _clusters = _public_objects()
    package = _fact_package(
        raw_batch_sha256="f" * 64,
        cases=cases,
    )

    truncated = package.model_copy(
        update={"assessments": package.assessments[:-1]},
    )

    with pytest.raises(
        Phase5B0ReplicationScoringError,
        match="exactly cover",
    ):
        _validate_fact_assessments(
            package=truncated,
            raw_batch_sha256="f" * 64,
            cases=cases,
        )


def test_primary_semantic_verdict_reuse_is_not_admitted_by_v1_contract() -> None:
    _specimen, cases, _clusters = _public_objects()
    package = _fact_package(
        raw_batch_sha256="1" * 64,
        cases=cases,
    )

    payload = package.model_dump(mode="json")
    payload["semantic_assessment_origin"] = "primary_semantic_input_equivalence_reuse"
    payload["primary_semantic_verdicts_reused"] = True

    with pytest.raises(ValidationError):
        Phase5B0ReplicationFactAssessmentPackageV1.model_validate(payload)


def test_protected_role_is_rejected_before_scoring() -> None:
    _specimen, cases, _clusters = _public_objects()
    protected = cases[0].model_copy(
        update={"data_role": EvaluationRole.HELD_OUT},
    )
    changed = (protected, *cases[1:])

    with pytest.raises(
        Phase5B0ReplicationScoringError,
        match="protected role",
    ):
        _validate_scoring_population(changed)


def test_synthetic_public_safe_qualification_scores_exactly_13_metrics() -> None:
    specimen, cases, clusters = _public_objects()
    raw = _synthetic_raw_batch(specimen, cases)
    raw_sha = hashlib.sha256(stable_model_bytes(raw)).hexdigest()
    package = _fact_package(
        raw_batch_sha256=raw_sha,
        cases=cases,
    )
    fact_sha = hashlib.sha256(stable_model_bytes(package)).hexdigest()

    report = score_replication_with_objects(
        specimen=specimen,
        cases=cases,
        cluster_by_case=clusters,
        raw_batch=raw,
        fact_assessments=package,
        fact_assessment_sha256=fact_sha,
        scoring_commit_sha="d" * 40,
        scoring_runner_source_sha256="e" * 64,
    )

    assert report.observed_case_count == 42
    assert len(report.records) == 42
    assert len(report.metric_aggregates) == 13
    assert report.integrity.all_passed is True
    assert report.evidence_valid is True
    assert report.reconciliation_eligible is True
    assert report.quality_threshold_used_for_validity is False
    assert report.runtime_reexecuted is False
    assert report.live_provider_call_count == 0
    assert report.evaluator_truth_joined_after_execution is True
    assert report.primary_semantic_verdicts_reused is False
    assert report.protected_roles_accessed is False
    assert report.held_out_outcomes_exposed is False
    assert report.release_eligible is False


def test_public_scoring_receipt_contains_no_raw_answer_or_query() -> None:
    specimen, cases, clusters = _public_objects()
    raw = _synthetic_raw_batch(specimen, cases)
    raw_sha = hashlib.sha256(stable_model_bytes(raw)).hexdigest()
    package = _fact_package(
        raw_batch_sha256=raw_sha,
        cases=cases,
    )
    fact_sha = hashlib.sha256(stable_model_bytes(package)).hexdigest()

    report = score_replication_with_objects(
        specimen=specimen,
        cases=cases,
        cluster_by_case=clusters,
        raw_batch=raw,
        fact_assessments=package,
        fact_assessment_sha256=fact_sha,
        scoring_commit_sha="d" * 40,
        scoring_runner_source_sha256="e" * 64,
    )

    receipt = Phase5B0ReplicationScoringReceiptV1(
        replication_raw_batch_sha256=report.replication_raw_batch_sha256,
        raw_scoring_report_sha256="2" * 64,
        fact_assessment_package_sha256=fact_sha,
        runtime_configuration_id=report.runtime_configuration_id,
        execution_commit_sha=report.execution_commit_sha,
        scoring_commit_sha=report.scoring_commit_sha,
        scoring_runner_source_sha256=report.scoring_runner_source_sha256,
        evaluator_provenance=report.evaluator_provenance,
        metric_aggregates=report.metric_aggregates,
        primary_failure_counts=report.primary_failure_counts,
        cluster_summaries=report.cluster_summaries,
        integrity=report.integrity,
        evidence_valid=report.evidence_valid,
        scientific_disposition=report.scientific_disposition,
        reconciliation_eligible=report.reconciliation_eligible,
    )

    public_text = receipt.model_dump_json()

    assert "Synthetic answer." not in public_text
    assert '"query":' not in public_text
    assert receipt.runtime_reexecuted is False
    assert receipt.live_provider_call_count == 0
    assert receipt.release_eligible is False
    assert receipt.replication_executed is True


def test_qualification_does_not_execute_real_replication_or_runtime() -> None:
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden_fragments = (
        "execute_phase5_b0_replication" + "(",
        "build_phase5_b0_primary_pipeline" + "(",
        "prepare_fact_assessment_packet" + "(",
        "score_phase5_b0_replication" + "(",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
