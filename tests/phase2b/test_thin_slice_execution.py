import asyncio
from pathlib import Path

from rag_reliability.contracts.enums import FailureLabel
from rag_reliability.evaluation.thin_slice import (
    build_thin_slice_pipeline,
    canonical_report_bytes,
    execute_thin_slice,
    load_thin_slice_bundle,
    score_thin_slice_case,
)
from rag_reliability.runtime import (
    BoundedContextBuilder,
    CurrentGithubRestSourcePolicyFilter,
    DeterministicRagPipeline,
    ExactCitationValidator,
    ReplayProvider,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_thin_slice_executes_all_cases_with_no_failures() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)
    report = asyncio.run(execute_thin_slice(bundle))

    assert report.case_count == 10
    assert report.passed_case_count == 10
    assert report.failed_case_count == 0
    assert report.all_cases_passed is True
    assert all(result.passed for result in report.case_results)


def test_thin_slice_report_is_byte_deterministic() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)

    first = asyncio.run(execute_thin_slice(bundle))
    second = asyncio.run(execute_thin_slice(bundle))

    assert canonical_report_bytes(first) == canonical_report_bytes(second)


def test_scorer_detects_retrieval_miss_for_answerable_case() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)
    config = bundle.runtime_config
    case = bundle.cases.cases[0]

    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=LexicalRetriever(config.retrieval, ()),
        source_filter=CurrentGithubRestSourcePolicyFilter(config.source_policy),
        context_builder=BoundedContextBuilder(config.context),
        provider=ReplayProvider(config.provider, bundle.replay.entries),
        citation_validator=ExactCitationValidator(config.citation),
    )

    execution = asyncio.run(pipeline.run(case.to_runtime_input()))
    result = score_thin_slice_case(case, execution)

    assert result.passed is False
    assert result.retrieval_required_source_pass is False
    assert result.primary_failure is FailureLabel.RETRIEVAL_MISS


def test_runtime_pipeline_receives_only_runtime_case_projection() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)
    pipeline = build_thin_slice_pipeline(bundle)
    case = bundle.cases.cases[0]

    execution = asyncio.run(pipeline.run(case.to_runtime_input()))

    assert execution.trace.case_id == case.case_id
    assert execution.outcome.status == "answer"
