"""Score the immutable Phase 5 G5N primary B0 batch without re-execution.

This module is an offline evaluator boundary. It never invokes the runtime pipeline
or provider. It binds completed G5N primary custody, joins evaluator-owned
DEVELOPMENT/TUNING truth only after execution, prepares a private semantic fact
assessment packet, and materializes a private detailed scoring report plus a
public-safe scoring receipt.

The frozen measurement scorer and aggregation implementation remain unchanged.
The synthetic aggregation report is used only as the already-frozen arithmetic
and integrity engine; it is never published as B0 evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import (
    EvaluationRole,
    FailureLabel,
    ResponseMode,
)
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import AnswerOutcome
from rag_reliability.evaluation.b0_authorization_models import (
    Phase5B0SpecimenV1,
    stable_model_bytes,
)
from rag_reliability.evaluation.b0_primary_execution import (
    Phase5B0PrimaryExecutionReceiptV1,
    Phase5B0PrimaryExecutionRecordV1,
    Phase5B0PrimaryRawBatchV1,
)
from rag_reliability.evaluation.development_cases import (
    Phase4DevelopmentCaseSuite,
)
from rag_reliability.evaluation.measurement_aggregation import (
    Phase5AggregationRecord,
    Phase5EvidenceIntegritySummary,
    Phase5MetricAggregate,
    Phase5RoleExpectation,
    Phase5SyntheticAggregationExpectation,
    aggregate_phase5_synthetic_scores,
)
from rag_reliability.evaluation.measurement_instrument import (
    Phase5FactAssessmentSet,
)
from rag_reliability.evaluation.measurement_scoring import (
    Phase5CaseScore,
    score_phase5_case,
)
from rag_reliability.evaluation.tuning_cases import (
    Phase4TuningCaseSuite,
)

_SPECIMEN_SHA256: Sha256 = "5ce922230e8a09041c7ea6248ee0f4acf412182ee062c6a16a15b65668485986"
_DEVELOPMENT_SUITE_SHA256: Sha256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SUITE_SHA256: Sha256 = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
_PRIMARY_RECEIPT_SHA256: Sha256 = "1849a3d64740374d7890c6201ec4696b8fcfc5458d7f7c1217d76970f7cf661d"

_SPECIMEN_PATH = Path("artifacts/development/phase5_b0_specimen_v1.json")
_DEVELOPMENT_SUITE_PATH = Path("artifacts/development/phase4c_development_cases_v1.json")
_TUNING_SUITE_PATH = Path("artifacts/development/phase4c_tuning_cases_v1.json")
_PRIMARY_RECEIPT_PATH = Path("artifacts/development/phase5_b0_primary_execution_receipt_v1.json")
_PRIMARY_RAW_BATCH_PATH = Path("evidence_vault/eval_reports/phase5_b0_primary_execution_v1.json")

_FACT_TEMPLATE_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_primary_fact_assessment_template_v1.json"
)
_FACT_ASSESSMENTS_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_primary_fact_assessments_v1.json"
)
_RAW_SCORING_PATH = Path("evidence_vault/eval_reports/phase5_b0_primary_scoring_v1.json")
_PUBLIC_SCORING_RECEIPT_PATH = Path(
    "artifacts/development/phase5_b0_primary_scoring_receipt_v1.json"
)

_RUNNER_RELATIVE_PATH = "src/rag_reliability/evaluation/b0_primary_scoring.py"


class Phase5B0PrimaryScoringError(ValueError):
    """The G5N primary batch cannot be scored without violating custody."""


class Phase5B0FactPromptV1(ContractModel):
    """One evaluator-owned semantic fact prompt."""

    fact_id: NonEmptyStr
    rubric: NonEmptyStr


class Phase5B0FactAssessmentTemplateCaseV1(ContractModel):
    """Private evaluator packet for one answerable case."""

    case_id: NonEmptyStr
    query: NonEmptyStr
    actual_status: NonEmptyStr
    answer_text: NonEmptyStr | None = None
    outcome_message: NonEmptyStr | None = None
    facts: tuple[Phase5B0FactPromptV1, ...] = Field(min_length=1)


class Phase5B0PrimaryFactAssessmentTemplateV1(ContractModel):
    """Private prompt packet; never a completed semantic verdict artifact."""

    packet_version: Literal["phase5-b0-primary-fact-assessment-template-v1"] = (
        "phase5-b0-primary-fact-assessment-template-v1"
    )

    primary_raw_batch_sha256: Sha256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SUITE_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SUITE_SHA256

    fact_scoring_method_id: Literal["evaluator_owned_fact_verdict_v1"] = (
        "evaluator_owned_fact_verdict_v1"
    )

    answer_case_count: int = Field(ge=1, le=42)
    cases: tuple[
        Phase5B0FactAssessmentTemplateCaseV1,
        ...,
    ] = Field(min_length=1, max_length=42)

    contains_raw_runtime_answers: Literal[True] = True
    private_evidence_only: Literal[True] = True
    held_out_outcomes_exposed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False

    @model_validator(mode="after")
    def validate_packet(self) -> Self:
        if self.development_suite_sha256 != _DEVELOPMENT_SUITE_SHA256:
            raise ValueError("DEVELOPMENT suite identity drifted")
        if self.tuning_suite_sha256 != _TUNING_SUITE_SHA256:
            raise ValueError("TUNING suite identity drifted")

        if self.answer_case_count != len(self.cases):
            raise ValueError("answer case count does not reconcile")

        case_ids = tuple(case.case_id for case in self.cases)
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("fact template case IDs must be unique")

        return self


class Phase5B0PrimaryFactAssessmentPackageV1(ContractModel):
    """Completed evaluator-owned fact verdict package for the primary batch."""

    package_version: Literal["phase5-b0-primary-fact-assessments-v1"] = (
        "phase5-b0-primary-fact-assessments-v1"
    )

    primary_raw_batch_sha256: Sha256

    fact_scoring_method_id: Literal["evaluator_owned_fact_verdict_v1"] = (
        "evaluator_owned_fact_verdict_v1"
    )

    evaluator_provenance: NonEmptyStr

    assessments: tuple[
        Phase5FactAssessmentSet,
        ...,
    ] = Field(min_length=1, max_length=42)

    held_out_outcomes_exposed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False

    @model_validator(mode="after")
    def validate_package(self) -> Self:
        case_ids = tuple(item.case_id for item in self.assessments)
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("fact assessment case IDs must be unique")
        return self


class Phase5B0FailureCountV1(ContractModel):
    label: FailureLabel
    count: int = Field(ge=1)


class Phase5B0ClusterSummaryV1(ContractModel):
    cluster_id: NonEmptyStr
    role: EvaluationRole
    case_count: int = Field(ge=1)
    answer_case_count: int = Field(ge=0)
    refusal_case_count: int = Field(ge=0)
    critical_failure_count: int = Field(ge=0)
    primary_failure_counts: tuple[Phase5B0FailureCountV1, ...] = ()
    classification_complete: bool
    trace_complete: bool

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        if self.case_count != self.answer_case_count + self.refusal_case_count:
            raise ValueError("cluster response-mode counts do not reconcile")
        return self


class Phase5B0PrimaryCaseScoringRecordV1(ContractModel):
    case_id: NonEmptyStr
    cluster_id: NonEmptyStr
    role: EvaluationRole
    score: Phase5CaseScore

    @model_validator(mode="after")
    def validate_case_id(self) -> Self:
        if self.case_id != self.score.case_id:
            raise ValueError("case scoring record does not match score case_id")
        return self


ScientificDisposition = Literal[
    "DIAGNOSTIC_SUPPORT",
    "INCONCLUSIVE",
]


class Phase5B0PrimaryRawScoringReportV1(ContractModel):
    """Private detailed G5N-S scoring evidence."""

    report_version: Literal["phase5-b0-primary-scoring-v1"] = "phase5-b0-primary-scoring-v1"

    evidence_class: Literal["b0_primary_scoring"] = "b0_primary_scoring"

    specimen_sha256: Sha256 = _SPECIMEN_SHA256
    primary_execution_receipt_sha256: Sha256 = _PRIMARY_RECEIPT_SHA256

    primary_raw_batch_sha256: Sha256
    fact_assessment_package_sha256: Sha256

    runtime_configuration_id: Sha256
    execution_commit_sha: NonEmptyStr
    scoring_commit_sha: NonEmptyStr
    scoring_runner_source_sha256: Sha256

    expected_case_count: Literal[42] = 42
    observed_case_count: int = Field(ge=0, le=42)

    records: tuple[
        Phase5B0PrimaryCaseScoringRecordV1,
        ...,
    ] = Field(max_length=42)

    metric_aggregates: tuple[
        Phase5MetricAggregate,
        ...,
    ] = Field(min_length=13, max_length=13)

    integrity: Phase5EvidenceIntegritySummary

    primary_failure_counts: tuple[Phase5B0FailureCountV1, ...] = ()
    cluster_summaries: tuple[Phase5B0ClusterSummaryV1, ...]

    evidence_valid: bool
    scientific_disposition: ScientificDisposition
    replication_eligible: bool

    quality_threshold_used_for_validity: Literal[False] = False
    runtime_reexecuted: Literal[False] = False
    live_provider_call_count: Literal[0] = 0
    evaluator_truth_joined_after_execution: Literal[True] = True
    held_out_outcomes_exposed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.specimen_sha256 != _SPECIMEN_SHA256:
            raise ValueError("specimen identity drifted")
        if self.primary_execution_receipt_sha256 != _PRIMARY_RECEIPT_SHA256:
            raise ValueError("primary custody receipt identity drifted")

        if self.observed_case_count != len(self.records):
            raise ValueError("observed case count does not reconcile")

        if self.evidence_valid != self.integrity.all_passed:
            raise ValueError("evidence validity does not reconcile")

        if self.replication_eligible != self.evidence_valid:
            raise ValueError("replication eligibility must follow B0 evidence validity")

        expected_disposition: ScientificDisposition = (
            "DIAGNOSTIC_SUPPORT" if self.evidence_valid else "INCONCLUSIVE"
        )
        if self.scientific_disposition != expected_disposition:
            raise ValueError("scientific disposition does not reconcile")

        return self


class Phase5B0PrimaryScoringReceiptV1(ContractModel):
    """Public-safe aggregate receipt for the G5N-S primary score."""

    receipt_version: Literal["phase5-b0-primary-scoring-receipt-v1"] = (
        "phase5-b0-primary-scoring-receipt-v1"
    )

    evidence_class: Literal["b0_primary_scoring"] = "b0_primary_scoring"

    specimen_sha256: Sha256 = _SPECIMEN_SHA256
    primary_execution_receipt_sha256: Sha256 = _PRIMARY_RECEIPT_SHA256

    primary_raw_batch_sha256: Sha256
    raw_scoring_report_sha256: Sha256
    fact_assessment_package_sha256: Sha256

    runtime_configuration_id: Sha256
    execution_commit_sha: NonEmptyStr
    scoring_commit_sha: NonEmptyStr
    scoring_runner_source_sha256: Sha256
    evaluator_provenance: NonEmptyStr

    expected_case_count: Literal[42] = 42
    observed_case_count: Literal[42] = 42
    development_case_count: Literal[24] = 24
    tuning_case_count: Literal[18] = 18

    metric_aggregates: tuple[
        Phase5MetricAggregate,
        ...,
    ] = Field(min_length=13, max_length=13)

    primary_failure_counts: tuple[Phase5B0FailureCountV1, ...] = ()
    cluster_summaries: tuple[Phase5B0ClusterSummaryV1, ...]

    integrity: Phase5EvidenceIntegritySummary

    evidence_valid: bool
    scientific_disposition: ScientificDisposition
    replication_eligible: bool

    scoring_performed: Literal[True] = True
    quality_threshold_used_for_validity: Literal[False] = False
    runtime_reexecuted: Literal[False] = False
    live_provider_call_count: Literal[0] = 0
    evaluator_truth_joined_after_execution: Literal[True] = True
    held_out_outcomes_exposed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    replication_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.specimen_sha256 != _SPECIMEN_SHA256:
            raise ValueError("receipt specimen identity drifted")
        if self.primary_execution_receipt_sha256 != _PRIMARY_RECEIPT_SHA256:
            raise ValueError("receipt primary custody identity drifted")

        if self.evidence_valid != self.integrity.all_passed:
            raise ValueError("receipt evidence validity does not reconcile")

        if self.replication_eligible != self.evidence_valid:
            raise ValueError("receipt replication eligibility must follow evidence validity")

        expected_disposition: ScientificDisposition = (
            "DIAGNOSTIC_SUPPORT" if self.evidence_valid else "INCONCLUSIVE"
        )
        if self.scientific_disposition != expected_disposition:
            raise ValueError("receipt scientific disposition does not reconcile")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _verified_bytes(
    path: Path,
    expected_sha256: str | None = None,
) -> bytes:
    if not path.exists():
        raise Phase5B0PrimaryScoringError(f"required artifact missing: {path}")

    content = path.read_bytes()
    digest = _sha256_bytes(content)

    if expected_sha256 is not None and digest != expected_sha256:
        raise Phase5B0PrimaryScoringError(f"artifact SHA drifted: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists():
        raise Phase5B0PrimaryScoringError(f"required SHA sidecar missing: {sidecar}")

    expected_sidecar = f"{digest}  {path.name}"
    observed_sidecar = sidecar.read_text(encoding="utf-8").strip()

    if observed_sidecar != expected_sidecar:
        raise Phase5B0PrimaryScoringError(f"SHA sidecar mismatch: {path}")

    return content


def _write_durable_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _write_or_verify_immutable_model(
    path: Path,
    value: ContractModel,
) -> str:
    content = stable_model_bytes(value)
    digest = _sha256_bytes(content)
    sidecar = path.with_suffix(path.suffix + ".sha256")
    sidecar_bytes = f"{digest}  {path.name}\n".encode()

    if path.exists():
        if path.read_bytes() != content:
            raise Phase5B0PrimaryScoringError(
                f"refusing to replace different scoring artifact: {path}"
            )
    else:
        if sidecar.exists():
            raise Phase5B0PrimaryScoringError(f"orphan scoring sidecar exists: {sidecar}")
        _write_durable_bytes(path, content)

    if sidecar.exists():
        if sidecar.read_bytes() != sidecar_bytes:
            raise Phase5B0PrimaryScoringError(f"scoring sidecar mismatch: {sidecar}")
    else:
        _write_durable_bytes(sidecar, sidecar_bytes)

    return digest


def _git_value(repo_root: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _require_clean_main(repo_root: Path) -> str:
    branch = _git_value(
        repo_root,
        "branch",
        "--show-current",
    )
    if branch != "main":
        raise Phase5B0PrimaryScoringError("G5N-S evidence work requires branch main")

    status = _git_value(
        repo_root,
        "status",
        "--short",
    )
    if status:
        raise Phase5B0PrimaryScoringError("G5N-S evidence work requires a clean tracked worktree")

    return _git_value(
        repo_root,
        "rev-parse",
        "HEAD",
    )


def _verify_evaluator_bindings(
    repo_root: Path,
    specimen: Phase5B0SpecimenV1,
) -> None:
    for binding in specimen.evaluator_source_bindings:
        path = repo_root / binding.path
        if not path.exists():
            raise Phase5B0PrimaryScoringError(f"frozen evaluator source missing: {binding.path}")
        if _sha256_file(path) != binding.sha256:
            raise Phase5B0PrimaryScoringError(f"frozen evaluator source drifted: {binding.path}")


def _load_inputs(
    repo_root: Path,
) -> tuple[
    Phase5B0SpecimenV1,
    Phase4DevelopmentCaseSuite,
    Phase4TuningCaseSuite,
    Phase5B0PrimaryExecutionReceiptV1,
    Phase5B0PrimaryRawBatchV1,
]:
    specimen = Phase5B0SpecimenV1.model_validate_json(
        _verified_bytes(
            repo_root / _SPECIMEN_PATH,
            _SPECIMEN_SHA256,
        )
    )
    _verify_evaluator_bindings(
        repo_root,
        specimen,
    )

    development = Phase4DevelopmentCaseSuite.model_validate_json(
        _verified_bytes(
            repo_root / _DEVELOPMENT_SUITE_PATH,
            _DEVELOPMENT_SUITE_SHA256,
        )
    )
    tuning = Phase4TuningCaseSuite.model_validate_json(
        _verified_bytes(
            repo_root / _TUNING_SUITE_PATH,
            _TUNING_SUITE_SHA256,
        )
    )
    receipt = Phase5B0PrimaryExecutionReceiptV1.model_validate_json(
        _verified_bytes(
            repo_root / _PRIMARY_RECEIPT_PATH,
            _PRIMARY_RECEIPT_SHA256,
        )
    )

    raw_bytes = _verified_bytes(repo_root / _PRIMARY_RAW_BATCH_PATH)
    raw = Phase5B0PrimaryRawBatchV1.model_validate_json(raw_bytes)

    raw_sha = _sha256_bytes(raw_bytes)
    if raw_sha != receipt.raw_batch_sha256:
        raise Phase5B0PrimaryScoringError(
            "raw primary batch SHA does not match public custody receipt"
        )

    if receipt.execution_commit_sha != raw.execution_commit_sha:
        raise Phase5B0PrimaryScoringError(
            "execution commit does not reconcile across primary custody"
        )

    if not receipt.primary_execution_complete:
        raise Phase5B0PrimaryScoringError("primary custody receipt is not complete")
    if receipt.started_slot_count != 42 or receipt.terminal_record_count != 42:
        raise Phase5B0PrimaryScoringError("primary custody does not reconcile to 42/42")
    if receipt.unreconciled_started_slot_count != 0:
        raise Phase5B0PrimaryScoringError("primary custody contains unreconciled starts")
    if not raw.batch_complete or raw.batch_decision != "COMPLETE":
        raise Phase5B0PrimaryScoringError("raw primary batch is not complete")

    return (
        specimen,
        development,
        tuning,
        receipt,
        raw,
    )


def _ordered_cases_and_clusters(
    specimen: Phase5B0SpecimenV1,
    development: Phase4DevelopmentCaseSuite,
    tuning: Phase4TuningCaseSuite,
) -> tuple[
    tuple[EvaluationCase, ...],
    dict[str, str],
]:
    by_case: dict[str, EvaluationCase] = {}
    cluster_by_case: dict[str, str] = {}

    for development_record in development.records:
        by_case[development_record.case.case_id] = development_record.case
        cluster_by_case[development_record.case.case_id] = development_record.cluster_id

    for tuning_record in tuning.records:
        by_case[tuning_record.case.case_id] = tuning_record.case
        cluster_by_case[tuning_record.case.case_id] = tuning_record.cluster_id

    expected_ids = specimen.case_ids_in_execution_order

    if set(by_case) != set(expected_ids):
        raise Phase5B0PrimaryScoringError("frozen evaluator case set does not match B0 specimen")

    ordered = tuple(by_case[case_id] for case_id in expected_ids)

    if len(ordered) != 42:
        raise Phase5B0PrimaryScoringError("B0 scorer requires exactly 42 evaluator cases")

    if any(
        case.data_role
        not in {
            EvaluationRole.DEVELOPMENT,
            EvaluationRole.TUNING,
        }
        for case in ordered
    ):
        raise Phase5B0PrimaryScoringError("protected role entered G5N-S evaluator case set")

    return (
        ordered,
        cluster_by_case,
    )


def build_fact_assessment_template(
    *,
    raw_batch_sha256: str,
    cases: tuple[EvaluationCase, ...],
    records: tuple[
        Phase5B0PrimaryExecutionRecordV1,
        ...,
    ],
) -> Phase5B0PrimaryFactAssessmentTemplateV1:
    """Build the private semantic-adjudication packet without scoring."""

    execution_by_case = {record.case_id: record.execution for record in records}

    answer_cases: list[Phase5B0FactAssessmentTemplateCaseV1] = []

    for case in cases:
        if case.expected_response_mode is ResponseMode.REFUSE:
            continue

        execution = execution_by_case.get(case.case_id)
        if execution is None:
            raise Phase5B0PrimaryScoringError(
                f"missing primary execution for answer case: {case.case_id}"
            )

        if len(case.required_fact_ids) != len(case.gold_fact_rubric):
            raise Phase5B0PrimaryScoringError(f"fact ID/rubric count mismatch: {case.case_id}")

        outcome = execution.outcome
        answer_text: str | None = None
        outcome_message: str | None = None

        if isinstance(
            outcome,
            AnswerOutcome,
        ):
            answer_text = outcome.answer_text
        else:
            outcome_message = outcome.message

        answer_cases.append(
            Phase5B0FactAssessmentTemplateCaseV1(
                case_id=case.case_id,
                query=case.query,
                actual_status=outcome.status,
                answer_text=answer_text,
                outcome_message=outcome_message,
                facts=tuple(
                    Phase5B0FactPromptV1(
                        fact_id=fact_id,
                        rubric=rubric,
                    )
                    for fact_id, rubric in zip(
                        case.required_fact_ids,
                        case.gold_fact_rubric,
                        strict=True,
                    )
                ),
            )
        )

    return Phase5B0PrimaryFactAssessmentTemplateV1(
        primary_raw_batch_sha256=(raw_batch_sha256),
        answer_case_count=len(answer_cases),
        cases=tuple(answer_cases),
    )


def _validate_fact_assessments(
    *,
    package: Phase5B0PrimaryFactAssessmentPackageV1,
    raw_batch_sha256: str,
    cases: tuple[EvaluationCase, ...],
) -> dict[
    str,
    Phase5FactAssessmentSet,
]:
    if package.primary_raw_batch_sha256 != raw_batch_sha256:
        raise Phase5B0PrimaryScoringError(
            "fact assessments are not bound to this raw primary batch"
        )

    expected_answer_cases = {
        case.case_id: case
        for case in cases
        if (case.expected_response_mode is not ResponseMode.REFUSE)
    }
    observed = {item.case_id: item for item in package.assessments}

    if set(observed) != set(expected_answer_cases):
        raise Phase5B0PrimaryScoringError("fact assessment package must exactly cover answer cases")

    for case_id, case in expected_answer_cases.items():
        assessment = observed[case_id]
        expected_fact_ids = set(case.required_fact_ids)
        observed_fact_ids = {verdict.fact_id for verdict in assessment.verdicts}

        if observed_fact_ids != expected_fact_ids:
            raise Phase5B0PrimaryScoringError(f"fact verdict coverage drifted: {case_id}")

    return observed


def _failure_counts(
    scores: tuple[
        Phase5CaseScore,
        ...,
    ],
) -> tuple[
    Phase5B0FailureCountV1,
    ...,
]:
    labels = tuple(score.primary_failure for score in scores if score.primary_failure is not None)
    counts: Counter[FailureLabel] = Counter(labels)

    return tuple(
        Phase5B0FailureCountV1(
            label=label,
            count=counts[label],
        )
        for label in sorted(
            counts,
            key=lambda item: item.value,
        )
    )


def _cluster_summaries(
    *,
    records: tuple[
        Phase5B0PrimaryCaseScoringRecordV1,
        ...,
    ],
    cases_by_id: dict[str, EvaluationCase],
) -> tuple[
    Phase5B0ClusterSummaryV1,
    ...,
]:
    by_cluster: dict[
        tuple[EvaluationRole, str],
        list[Phase5B0PrimaryCaseScoringRecordV1],
    ] = {}

    for record in records:
        by_cluster.setdefault(
            (
                record.role,
                record.cluster_id,
            ),
            [],
        ).append(record)

    summaries: list[Phase5B0ClusterSummaryV1] = []

    for (
        role,
        cluster_id,
    ), members in sorted(
        by_cluster.items(),
        key=lambda item: (
            item[0][0].value,
            item[0][1],
        ),
    ):
        member_scores = tuple(member.score for member in members)
        answer_count = sum(
            cases_by_id[member.case_id].expected_response_mode is not ResponseMode.REFUSE
            for member in members
        )
        refusal_count = len(members) - answer_count

        summaries.append(
            Phase5B0ClusterSummaryV1(
                cluster_id=cluster_id,
                role=role,
                case_count=len(members),
                answer_case_count=(answer_count),
                refusal_case_count=(refusal_count),
                critical_failure_count=sum(
                    score.critical_failure_count_contribution for score in member_scores
                ),
                primary_failure_counts=(_failure_counts(member_scores)),
                classification_complete=all(
                    score.classification_complete for score in member_scores
                ),
                trace_complete=all(score.trace_completeness for score in member_scores),
            )
        )

    return tuple(summaries)


def score_primary_with_objects(
    *,
    specimen: Phase5B0SpecimenV1,
    cases: tuple[EvaluationCase, ...],
    cluster_by_case: dict[str, str],
    raw_batch: Phase5B0PrimaryRawBatchV1,
    fact_assessments: Phase5B0PrimaryFactAssessmentPackageV1,
    fact_assessment_sha256: str,
    scoring_commit_sha: str,
    scoring_runner_source_sha256: str,
) -> Phase5B0PrimaryRawScoringReportV1:
    """Score immutable primary executions with evaluator truth joined offline."""

    if not raw_batch.batch_complete or len(raw_batch.records) != 42:
        raise Phase5B0PrimaryScoringError(
            "scoring requires the complete immutable 42-record primary batch"
        )

    raw_sha = _sha256_bytes(stable_model_bytes(raw_batch))

    assessments_by_case = _validate_fact_assessments(
        package=fact_assessments,
        raw_batch_sha256=raw_sha,
        cases=cases,
    )

    execution_by_case = {record.case_id: record for record in raw_batch.records}

    if (
        tuple(record.case_id for record in raw_batch.records)
        != specimen.case_ids_in_execution_order
    ):
        raise Phase5B0PrimaryScoringError("raw primary execution order drifted from B0 specimen")

    scored_records: list[Phase5B0PrimaryCaseScoringRecordV1] = []
    aggregation_records: list[Phase5AggregationRecord] = []

    for case in cases:
        execution_record = execution_by_case.get(case.case_id)
        if execution_record is None:
            raise Phase5B0PrimaryScoringError(f"missing primary execution record: {case.case_id}")

        assessment = assessments_by_case.get(case.case_id)

        score = score_phase5_case(
            case,
            execution_record.execution,
            assessment,
        )

        scored_records.append(
            Phase5B0PrimaryCaseScoringRecordV1(
                case_id=case.case_id,
                cluster_id=(cluster_by_case[case.case_id]),
                role=case.data_role,
                score=score,
            )
        )

        aggregation_records.append(
            Phase5AggregationRecord(
                orchestration=(case.to_orchestration_view()),
                score=score,
                configuration_id=(specimen.runtime_configuration_id),
                evaluator_runtime_boundary_verified=True,
            )
        )

    synthetic_engine_report = aggregate_phase5_synthetic_scores(
        tuple(aggregation_records),
        Phase5SyntheticAggregationExpectation(
            expected_configuration_id=(specimen.runtime_configuration_id),
            role_expectations=(
                Phase5RoleExpectation(
                    role=(EvaluationRole.DEVELOPMENT),
                    case_count=24,
                ),
                Phase5RoleExpectation(
                    role=(EvaluationRole.TUNING),
                    case_count=18,
                ),
            ),
        ),
    )

    evidence_valid = synthetic_engine_report.integrity.all_passed

    disposition: ScientificDisposition = "DIAGNOSTIC_SUPPORT" if evidence_valid else "INCONCLUSIVE"

    scores = tuple(record.score for record in scored_records)
    cases_by_id = {case.case_id: case for case in cases}

    return Phase5B0PrimaryRawScoringReportV1(
        primary_raw_batch_sha256=raw_sha,
        fact_assessment_package_sha256=(fact_assessment_sha256),
        runtime_configuration_id=(specimen.runtime_configuration_id),
        execution_commit_sha=(raw_batch.execution_commit_sha),
        scoring_commit_sha=(scoring_commit_sha),
        scoring_runner_source_sha256=(scoring_runner_source_sha256),
        observed_case_count=len(scored_records),
        records=tuple(scored_records),
        metric_aggregates=(synthetic_engine_report.metric_aggregates),
        integrity=(synthetic_engine_report.integrity),
        primary_failure_counts=(_failure_counts(scores)),
        cluster_summaries=(
            _cluster_summaries(
                records=tuple(scored_records),
                cases_by_id=(cases_by_id),
            )
        ),
        evidence_valid=evidence_valid,
        scientific_disposition=(disposition),
        replication_eligible=(evidence_valid),
    )


def prepare_fact_assessment_packet(
    repo_root: Path,
) -> tuple[
    Phase5B0PrimaryFactAssessmentTemplateV1,
    str,
]:
    """Freeze a private prompt packet for semantic fact adjudication."""

    repo_root = repo_root.resolve()
    _require_clean_main(repo_root)

    (
        specimen,
        development,
        tuning,
        receipt,
        raw,
    ) = _load_inputs(repo_root)

    cases, _cluster_by_case = _ordered_cases_and_clusters(
        specimen,
        development,
        tuning,
    )

    raw_sha = _sha256_file(repo_root / _PRIMARY_RAW_BATCH_PATH)

    if raw_sha != receipt.raw_batch_sha256:
        raise Phase5B0PrimaryScoringError(
            "raw primary batch SHA drifted before assessment preparation"
        )

    template = build_fact_assessment_template(
        raw_batch_sha256=raw_sha,
        cases=cases,
        records=raw.records,
    )

    template_sha = _write_or_verify_immutable_model(
        repo_root / _FACT_TEMPLATE_PATH,
        template,
    )

    return (
        template,
        template_sha,
    )


def score_phase5_b0_primary(
    repo_root: Path,
) -> tuple[
    Phase5B0PrimaryRawScoringReportV1,
    str,
    Phase5B0PrimaryScoringReceiptV1,
    str,
]:
    """Score the completed primary batch without runtime or provider calls."""

    repo_root = repo_root.resolve()
    scoring_commit_sha = _require_clean_main(repo_root)

    (
        specimen,
        development,
        tuning,
        _receipt,
        raw,
    ) = _load_inputs(repo_root)

    cases, cluster_by_case = _ordered_cases_and_clusters(
        specimen,
        development,
        tuning,
    )

    fact_bytes = _verified_bytes(repo_root / _FACT_ASSESSMENTS_PATH)
    fact_sha = _sha256_bytes(fact_bytes)

    fact_package = Phase5B0PrimaryFactAssessmentPackageV1.model_validate_json(fact_bytes)

    runner_sha = _sha256_file(repo_root / _RUNNER_RELATIVE_PATH)

    raw_report = score_primary_with_objects(
        specimen=specimen,
        cases=cases,
        cluster_by_case=(cluster_by_case),
        raw_batch=raw,
        fact_assessments=(fact_package),
        fact_assessment_sha256=(fact_sha),
        scoring_commit_sha=(scoring_commit_sha),
        scoring_runner_source_sha256=(runner_sha),
    )

    raw_report_sha = _write_or_verify_immutable_model(
        repo_root / _RAW_SCORING_PATH,
        raw_report,
    )

    public_receipt = Phase5B0PrimaryScoringReceiptV1(
        primary_raw_batch_sha256=(raw_report.primary_raw_batch_sha256),
        raw_scoring_report_sha256=(raw_report_sha),
        fact_assessment_package_sha256=(fact_sha),
        runtime_configuration_id=(raw_report.runtime_configuration_id),
        execution_commit_sha=(raw_report.execution_commit_sha),
        scoring_commit_sha=(scoring_commit_sha),
        scoring_runner_source_sha256=(runner_sha),
        evaluator_provenance=(fact_package.evaluator_provenance),
        metric_aggregates=(raw_report.metric_aggregates),
        primary_failure_counts=(raw_report.primary_failure_counts),
        cluster_summaries=(raw_report.cluster_summaries),
        integrity=(raw_report.integrity),
        evidence_valid=(raw_report.evidence_valid),
        scientific_disposition=(raw_report.scientific_disposition),
        replication_eligible=(raw_report.replication_eligible),
    )

    public_receipt_sha = _write_or_verify_immutable_model(
        repo_root / _PUBLIC_SCORING_RECEIPT_PATH,
        public_receipt,
    )

    return (
        raw_report,
        raw_report_sha,
        public_receipt,
        public_receipt_sha,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("Prepare or score the frozen Phase 5 G5N primary batch.")
    )
    parser.add_argument(
        "command",
        choices=(
            "prepare",
            "score",
        ),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]

    if args.command == "prepare":
        (
            template,
            template_sha,
        ) = prepare_fact_assessment_packet(repo_root)

        print("PHASE5_G5N_FACT_TEMPLATE=COMPLETE")
        print(f"PHASE5_G5N_FACT_TEMPLATE_SHA256={template_sha}")
        print(f"PHASE5_G5N_FACT_TEMPLATE_ANSWER_CASES={template.answer_case_count}")
        print(f"PHASE5_G5N_FACT_TEMPLATE_PATH={_FACT_TEMPLATE_PATH}")
        print("PHASE5_G5N_RUNTIME_REEXECUTED=false")
        print("PHASE5_G5N_LIVE_PROVIDER_CALLS=0")
        return 0

    (
        raw_report,
        raw_sha,
        receipt,
        receipt_sha,
    ) = score_phase5_b0_primary(repo_root)

    print("PHASE5_G5N_SCORING=COMPLETE")
    print(f"PHASE5_G5N_SCORING_RECEIPT_SHA256={receipt_sha}")
    print(f"PHASE5_G5N_SCORING_RAW_REPORT_SHA256={raw_sha}")
    print(f"PHASE5_G5N_SCORING_CASES={raw_report.observed_case_count}")
    print(f"PHASE5_G5N_SCORING_EVIDENCE_VALID={str(receipt.evidence_valid).lower()}")
    print(f"PHASE5_G5N_SCIENTIFIC_DISPOSITION={receipt.scientific_disposition}")
    print(f"PHASE5_G5O_REPLICATION_ELIGIBLE={str(receipt.replication_eligible).lower()}")
    print("PHASE5_G5N_RUNTIME_REEXECUTED=false")
    print("PHASE5_G5N_LIVE_PROVIDER_CALLS=0")

    return 0 if receipt.evidence_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
