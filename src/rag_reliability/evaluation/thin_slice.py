"""Development-only deterministic scoring for the Phase 2 thin RAG slice."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.config.identity import RuntimeConfiguration
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.corpus import RealSourceRecord
from rag_reliability.contracts.enums import (
    CitationValidationStatus,
    EvaluationRole,
    FailureLabel,
    RefusalReason,
    ResponseMode,
    RuntimeErrorCode,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import AnswerOutcome, ErrorOutcome, RefusalOutcome
from rag_reliability.runtime import (
    BoundedContextBuilder,
    CurrentGithubRestSourcePolicyFilter,
    DeterministicRagPipeline,
    ExactCitationValidator,
    IndexedDocument,
    PipelineExecution,
    ReplayEntry,
    ReplayProvider,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

_SUITE_ID: Literal["phase2b-thin-slice-dev-v1"] = "phase2b-thin-slice-dev-v1"
_TOKEN_SPACE = re.compile(r"\s+")
_FORBIDDEN_TEMPLATE_MARKERS = ("{%", "{{", "{#")


class ThinSliceSourceFixture(ContractModel):
    """One short real-source excerpt plus its provenance manifest."""

    manifest: RealSourceRecord
    content: NonEmptyStr

    @model_validator(mode="after")
    def validate_content_custody(self) -> ThinSliceSourceFixture:
        digest = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        if digest != self.manifest.content_sha256:
            raise ValueError("thin-slice source content hash mismatch")
        if any(marker in self.content for marker in _FORBIDDEN_TEMPLATE_MARKERS):
            raise ValueError("thin-slice source contains unresolved template directives")
        return self

    def to_indexed_document(self) -> IndexedDocument:
        return IndexedDocument(
            source_id=self.manifest.source_id,
            content=self.content,
            authority_level=self.manifest.authority_level,
            source_state=self.manifest.source_state,
            product_scope=self.manifest.product_scope,
            api_version_or_snapshot=self.manifest.api_version_or_snapshot,
        )


class ThinSliceSourceSet(ContractModel):
    suite_id: Literal["phase2b-thin-slice-dev-v1"]
    sources: tuple[ThinSliceSourceFixture, ...] = Field(min_length=10, max_length=20)

    @model_validator(mode="after")
    def validate_unique_sources(self) -> ThinSliceSourceSet:
        source_ids = tuple(source.manifest.source_id for source in self.sources)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("thin-slice source IDs must be unique")
        return self


class ThinSliceCaseSet(ContractModel):
    suite_id: Literal["phase2b-thin-slice-dev-v1"]
    cases: tuple[EvaluationCase, ...] = Field(min_length=6, max_length=10)

    @model_validator(mode="after")
    def validate_development_only(self) -> ThinSliceCaseSet:
        case_ids = tuple(case.case_id for case in self.cases)
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("thin-slice case IDs must be unique")
        for case in self.cases:
            if case.data_role is not EvaluationRole.DEVELOPMENT:
                raise ValueError("thin-slice cases must be development-only")
            if case.expected_response_mode is ResponseMode.QUALIFIED_ANSWER:
                raise ValueError("Phase 2B does not support qualified-answer cases")
        return self


class ThinSliceReplaySet(ContractModel):
    suite_id: Literal["phase2b-thin-slice-dev-v1"]
    entries: tuple[ReplayEntry, ...]

    @model_validator(mode="after")
    def validate_unique_queries(self) -> ThinSliceReplaySet:
        queries = tuple(entry.query for entry in self.entries)
        if len(queries) != len(set(queries)):
            raise ValueError("thin-slice replay queries must be unique")
        return self


class ThinSliceBundle(ContractModel):
    """Validated fixture bundle kept outside the runtime boundary."""

    sources: ThinSliceSourceSet
    cases: ThinSliceCaseSet
    replay: ThinSliceReplaySet
    runtime_config: RuntimeConfiguration
    source_fixture_hash: Sha256
    case_fixture_hash: Sha256
    replay_fixture_hash: Sha256
    runtime_config_file_hash: Sha256

    @model_validator(mode="after")
    def validate_cross_fixture_integrity(self) -> ThinSliceBundle:
        if not (
            self.sources.suite_id == self.cases.suite_id == self.replay.suite_id
        ):
            raise ValueError("thin-slice suite IDs do not match")

        source_ids = {source.manifest.source_id for source in self.sources.sources}
        answer_queries: set[str] = set()

        for case in self.cases.cases:
            missing_required = set(case.required_source_ids) - source_ids
            if missing_required:
                raise ValueError(
                    f"case {case.case_id} references unknown required sources"
                )
            missing_forbidden = set(case.forbidden_source_ids) - source_ids
            if missing_forbidden:
                raise ValueError(
                    f"case {case.case_id} references unknown forbidden sources"
                )
            if case.expected_response_mode is ResponseMode.ANSWER:
                answer_queries.add(case.query)

        replay_by_query = {entry.query: entry for entry in self.replay.entries}
        if set(replay_by_query) != answer_queries:
            raise ValueError("replay queries must exactly match answerable thin-slice cases")

        for case in self.cases.cases:
            if case.expected_response_mode is not ResponseMode.ANSWER:
                continue
            replay = replay_by_query[case.query]
            if not set(case.required_source_ids).issubset(replay.cited_source_ids):
                raise ValueError(
                    f"replay entry for {case.case_id} omits a required source citation"
                )
            if not set(replay.cited_source_ids).issubset(source_ids):
                raise ValueError(
                    f"replay entry for {case.case_id} cites an unknown source"
                )

        if self.runtime_config.reranker is not None:
            raise ValueError("Phase 2B runtime must keep reranking disabled")
        return self


class ThinSliceTraceEventSummary(ContractModel):
    stage: TraceStage
    status: TraceStatus
    source_ids: tuple[NonEmptyStr, ...] = ()
    error_code: NonEmptyStr | None = None


class ThinSliceCaseResult(ContractModel):
    case_id: NonEmptyStr
    expected_response_mode: ResponseMode
    actual_status: Literal["answer", "refusal", "error"]
    retrieval_required_source_pass: bool | None
    context_required_source_pass: bool | None
    citation_support_pass: bool | None
    required_fact_coverage_pass: bool | None
    refusal_behavior_pass: bool | None
    trace_completeness_pass: bool
    runtime_error_code: RuntimeErrorCode | None = None
    primary_failure: FailureLabel | None = None
    passed: bool
    trace_id: NonEmptyStr
    trace_events: tuple[ThinSliceTraceEventSummary, ...] = Field(min_length=1)


class ThinSliceMetricSummary(ContractModel):
    metric_id: NonEmptyStr
    applicable_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)
    failed_cases: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_counts(self) -> ThinSliceMetricSummary:
        if self.passed_cases + self.failed_cases != self.applicable_cases:
            raise ValueError("metric case counts do not reconcile")
        return self


class ThinSliceReport(ContractModel):
    report_schema_version: Literal["phase2b-report-v1"] = "phase2b-report-v1"
    suite_id: Literal["phase2b-thin-slice-dev-v1"] = _SUITE_ID
    evidence_class: Literal["development_only"] = "development_only"
    release_eligible: Literal[False] = False
    runtime_configuration_hash: Sha256
    source_fixture_hash: Sha256
    case_fixture_hash: Sha256
    replay_fixture_hash: Sha256
    runtime_config_file_hash: Sha256
    case_count: int = Field(ge=1)
    passed_case_count: int = Field(ge=0)
    failed_case_count: int = Field(ge=0)
    all_cases_passed: bool
    metric_summaries: tuple[ThinSliceMetricSummary, ...]
    case_results: tuple[ThinSliceCaseResult, ...]

    @model_validator(mode="after")
    def validate_report_counts(self) -> ThinSliceReport:
        if self.passed_case_count + self.failed_case_count != self.case_count:
            raise ValueError("report case counts do not reconcile")
        if len(self.case_results) != self.case_count:
            raise ValueError("report case result count does not match case_count")
        if self.all_cases_passed != (self.failed_case_count == 0):
            raise ValueError("all_cases_passed is inconsistent with failure count")
        return self


def _sha256_file(path: Path) -> Sha256:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_thin_slice_bundle(repo_root: Path) -> ThinSliceBundle:
    fixture_root = repo_root / "datasets" / "thin_slice"
    source_path = fixture_root / "phase2b_sources_v1.json"
    case_path = fixture_root / "phase2b_cases_v1.json"
    replay_path = fixture_root / "phase2b_replay_v1.json"
    config_path = fixture_root / "phase2b_runtime_config_v1.json"

    sources = ThinSliceSourceSet.model_validate_json(
        source_path.read_text(encoding="utf-8")
    )
    cases = ThinSliceCaseSet.model_validate_json(case_path.read_text(encoding="utf-8"))
    replay = ThinSliceReplaySet.model_validate_json(
        replay_path.read_text(encoding="utf-8")
    )
    runtime_config = RuntimeConfiguration.model_validate_json(
        config_path.read_text(encoding="utf-8")
    )

    return ThinSliceBundle(
        sources=sources,
        cases=cases,
        replay=replay,
        runtime_config=runtime_config,
        source_fixture_hash=_sha256_file(source_path),
        case_fixture_hash=_sha256_file(case_path),
        replay_fixture_hash=_sha256_file(replay_path),
        runtime_config_file_hash=_sha256_file(config_path),
    )


def build_thin_slice_pipeline(bundle: ThinSliceBundle) -> DeterministicRagPipeline:
    documents = tuple(source.to_indexed_document() for source in bundle.sources.sources)
    config = bundle.runtime_config
    return DeterministicRagPipeline(
        config=config,
        retriever=LexicalRetriever(config.retrieval, documents),
        source_filter=CurrentGithubRestSourcePolicyFilter(config.source_policy),
        context_builder=BoundedContextBuilder(config.context),
        provider=ReplayProvider(config.provider, bundle.replay.entries),
        citation_validator=ExactCitationValidator(config.citation),
    )


def _normalize(text: str) -> str:
    return _TOKEN_SPACE.sub(" ", text).strip().casefold()


def _source_ids_for_stage(
    execution: PipelineExecution,
    stage: TraceStage,
) -> tuple[str, ...]:
    for event in execution.trace.events:
        if event.stage is stage:
            return tuple(event.source_ids)
    return ()


def _trace_complete(execution: PipelineExecution) -> bool:
    stages = tuple(event.stage for event in execution.trace.events)
    outcome = execution.outcome

    if isinstance(outcome, AnswerOutcome):
        answer_expected = (
            TraceStage.RETRIEVAL,
            TraceStage.FILTERING,
            TraceStage.CONTEXT_ASSEMBLY,
            TraceStage.PROVIDER_GENERATION,
            TraceStage.CITATION_VALIDATION,
        )
        return stages == answer_expected

    if isinstance(outcome, RefusalOutcome):
        if outcome.reason is RefusalReason.INSUFFICIENT_EVIDENCE:
            insufficient_evidence_expected = (
                TraceStage.RETRIEVAL,
                TraceStage.FILTERING,
                TraceStage.REFUSAL_FALLBACK,
            )
            return stages == insufficient_evidence_expected
        if outcome.reason is RefusalReason.UNSUPPORTED_CITATION:
            unsupported_citation_expected = (
                TraceStage.RETRIEVAL,
                TraceStage.FILTERING,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStage.PROVIDER_GENERATION,
                TraceStage.CITATION_VALIDATION,
                TraceStage.REFUSAL_FALLBACK,
            )
            return stages == unsupported_citation_expected
        return bool(stages) and stages[-1] is TraceStage.REFUSAL_FALLBACK

    if isinstance(outcome, ErrorOutcome):
        return bool(execution.trace.events) and (
            execution.trace.events[-1].status is TraceStatus.ERROR
        )

    return False


def _citation_failure(outcome: AnswerOutcome) -> FailureLabel:
    if any(
        check.status is CitationValidationStatus.MISSING
        for check in outcome.citation_validation.checks
    ):
        return FailureLabel.CITATION_MISSING
    return FailureLabel.CITATION_NOT_SUPPORTED


def _map_error_failure(error_code: RuntimeErrorCode) -> FailureLabel | None:
    mapping = {
        RuntimeErrorCode.PROVIDER_TIMEOUT: FailureLabel.PROVIDER_TIMEOUT,
        RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE: (
            FailureLabel.PROVIDER_MALFORMED_RESPONSE
        ),
        RuntimeErrorCode.CONTEXT_BUILD_ERROR: FailureLabel.CONTEXT_EXCLUSION,
    }
    return mapping.get(error_code)


def score_thin_slice_case(
    case: EvaluationCase,
    execution: PipelineExecution,
) -> ThinSliceCaseResult:
    retrieval_ids = set(_source_ids_for_stage(execution, TraceStage.RETRIEVAL))
    context_ids = set(_source_ids_for_stage(execution, TraceStage.CONTEXT_ASSEMBLY))
    required_ids = set(case.required_source_ids)
    trace_complete = _trace_complete(execution)
    outcome = execution.outcome

    retrieval_pass: bool | None = None
    context_pass: bool | None = None
    citation_pass: bool | None = None
    fact_pass: bool | None = None
    refusal_pass: bool | None = None
    runtime_error_code: RuntimeErrorCode | None = None
    failure = execution.trace.primary_failure

    if case.expected_response_mode is ResponseMode.ANSWER:
        retrieval_pass = required_ids.issubset(retrieval_ids)
        context_pass = required_ids.issubset(context_ids)

        if isinstance(outcome, AnswerOutcome):
            citation_pass = (
                outcome.citation_validation.all_material_claims_supported
                and required_ids.issubset(outcome.cited_source_ids)
            )
            normalized_answer = _normalize(outcome.answer_text)
            fact_pass = all(
                _normalize(fact) in normalized_answer
                for fact in case.gold_fact_rubric
            )
        else:
            citation_pass = False
            fact_pass = False

    if case.expected_response_mode is ResponseMode.REFUSE:
        refusal_pass = isinstance(outcome, RefusalOutcome) and (
            case.must_refuse_reason == outcome.reason.value
        )

    if isinstance(outcome, ErrorOutcome):
        runtime_error_code = outcome.error_code

    passed_checks = [trace_complete]
    for check in (
        retrieval_pass,
        context_pass,
        citation_pass,
        fact_pass,
        refusal_pass,
    ):
        if check is not None:
            passed_checks.append(check)
    passed = all(passed_checks) and not isinstance(outcome, ErrorOutcome)

    if not passed and failure is None:
        if not trace_complete:
            failure = FailureLabel.TRACE_INCOMPLETE
        elif case.expected_response_mode is ResponseMode.REFUSE:
            if isinstance(outcome, AnswerOutcome):
                failure = FailureLabel.UNSAFE_ANSWER
            elif not refusal_pass:
                failure = FailureLabel.UNSAFE_REFUSAL
        elif isinstance(outcome, RefusalOutcome):
            failure = FailureLabel.UNSAFE_REFUSAL
        elif isinstance(outcome, ErrorOutcome):
            failure = _map_error_failure(outcome.error_code)
        elif retrieval_pass is False:
            failure = FailureLabel.RETRIEVAL_MISS
        elif context_pass is False:
            failure = FailureLabel.CONTEXT_EXCLUSION
        elif citation_pass is False and isinstance(outcome, AnswerOutcome):
            failure = _citation_failure(outcome)
        elif fact_pass is False:
            failure = FailureLabel.UNSUPPORTED_ANSWER

    return ThinSliceCaseResult(
        case_id=case.case_id,
        expected_response_mode=case.expected_response_mode,
        actual_status=outcome.status,
        retrieval_required_source_pass=retrieval_pass,
        context_required_source_pass=context_pass,
        citation_support_pass=citation_pass,
        required_fact_coverage_pass=fact_pass,
        refusal_behavior_pass=refusal_pass,
        trace_completeness_pass=trace_complete,
        runtime_error_code=runtime_error_code,
        primary_failure=failure,
        passed=passed,
        trace_id=execution.trace.trace_id,
        trace_events=tuple(
            ThinSliceTraceEventSummary(
                stage=event.stage,
                status=event.status,
                source_ids=event.source_ids,
                error_code=event.error_code,
            )
            for event in execution.trace.events
        ),
    )


def _metric_summary(
    metric_id: str,
    values: tuple[bool | None, ...],
) -> ThinSliceMetricSummary:
    applicable = tuple(value for value in values if value is not None)
    passed = sum(1 for value in applicable if value)
    return ThinSliceMetricSummary(
        metric_id=metric_id,
        applicable_cases=len(applicable),
        passed_cases=passed,
        failed_cases=len(applicable) - passed,
    )


async def execute_thin_slice(bundle: ThinSliceBundle) -> ThinSliceReport:
    pipeline = build_thin_slice_pipeline(bundle)
    results: list[ThinSliceCaseResult] = []

    for case in bundle.cases.cases:
        execution = await pipeline.run(case.to_runtime_input())
        results.append(score_thin_slice_case(case, execution))

    case_results = tuple(results)
    passed_count = sum(1 for result in case_results if result.passed)

    metric_summaries = (
        _metric_summary(
            "required_source_retrieval_v1",
            tuple(result.retrieval_required_source_pass for result in case_results),
        ),
        _metric_summary(
            "context_gold_inclusion_v1",
            tuple(result.context_required_source_pass for result in case_results),
        ),
        _metric_summary(
            "citation_reference_validity_v1",
            tuple(result.citation_support_pass for result in case_results),
        ),
        _metric_summary(
            "required_fact_coverage_v1",
            tuple(result.required_fact_coverage_pass for result in case_results),
        ),
        _metric_summary(
            "refusal_behavior_v1",
            tuple(result.refusal_behavior_pass for result in case_results),
        ),
        _metric_summary(
            "trace_completeness_v1",
            tuple(result.trace_completeness_pass for result in case_results),
        ),
    )

    return ThinSliceReport(
        runtime_configuration_hash=bundle.runtime_config.configuration_id,
        source_fixture_hash=bundle.source_fixture_hash,
        case_fixture_hash=bundle.case_fixture_hash,
        replay_fixture_hash=bundle.replay_fixture_hash,
        runtime_config_file_hash=bundle.runtime_config_file_hash,
        case_count=len(case_results),
        passed_case_count=passed_count,
        failed_case_count=len(case_results) - passed_count,
        all_cases_passed=passed_count == len(case_results),
        metric_summaries=metric_summaries,
        case_results=case_results,
    )


def canonical_report_bytes(report: ThinSliceReport) -> bytes:
    payload = report.model_dump(mode="json")
    text = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return (text + "\n").encode("utf-8")


def write_thin_slice_report(report: ThinSliceReport, output_path: Path) -> Sha256:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_bytes = canonical_report_bytes(report)
    output_path.write_bytes(report_bytes)
    digest = hashlib.sha256(report_bytes).hexdigest()
    output_path.with_suffix(output_path.suffix + ".sha256").write_text(
        f"{digest}  {output_path.name}\n",
        encoding="utf-8",
    )
    return digest
