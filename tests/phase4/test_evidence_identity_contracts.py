from datetime import UTC, datetime

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    ResponseMode,
    ScenarioClass,
    SourceState,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import (
    ContextBundle,
    ContextItem,
    ProviderResponse,
    RetrievedEvidence,
    SourceFilterResult,
)
from rag_reliability.contracts.tracing import TraceEvent
from rag_reliability.runtime.models import (
    IndexedDocument,
    ReplayEntry,
)


def _evidence(
    evidence_id: str,
    source_id: str,
) -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id=evidence_id,
        source_ids=(source_id,),
        document_ids=(
            f"document:{evidence_id}",
        ),
        content=f"Evidence {evidence_id}",
        rank=1,
        score=1.0,
        authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )


def test_phase2_legacy_retrieval_identity_migrates() -> None:
    evidence = RetrievedEvidence.model_validate(
        {
            "source_id": "source-1",
            "content": "Evidence",
            "rank": 1,
            "score": 1.0,
            "authority_level": "authoritative",
            "source_state": "current",
            "product_scope": "api.github.com",
            "api_version_or_snapshot": "2026-03-10",
        }
    )

    assert evidence.evidence_id == "source-1"
    assert evidence.source_ids == ("source-1",)
    assert evidence.document_ids == ()

    assert "source_id" not in RetrievedEvidence.model_fields


def test_full_corpus_evidence_separates_chunk_from_provenance() -> None:
    evidence = RetrievedEvidence(
        evidence_id="chunk-abc",
        source_ids=(
            "source-a",
            "source-b",
        ),
        document_ids=(
            "document-a",
            "document-b",
        ),
        content="Shared component evidence",
        rank=1,
        score=1.0,
        authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )

    assert evidence.evidence_id == "chunk-abc"
    assert evidence.source_ids == (
        "source-a",
        "source-b",
    )


def test_context_allows_multiple_chunks_from_same_source() -> None:
    context = ContextBundle(
        query="Question",
        items=(
            ContextItem(
                evidence_id="chunk-a",
                source_ids=("source-1",),
                document_ids=("document-1",),
                content="First chunk",
                position=1,
                authority_level=(
                    AuthorityLevel.AUTHORITATIVE
                ),
                source_state=SourceState.CURRENT,
                eligible_as_final_citation=True,
            ),
            ContextItem(
                evidence_id="chunk-b",
                source_ids=("source-1",),
                document_ids=("document-1",),
                content="Second chunk",
                position=2,
                authority_level=(
                    AuthorityLevel.AUTHORITATIVE
                ),
                source_state=SourceState.CURRENT,
                eligible_as_final_citation=True,
            ),
        ),
        assembled_context="First chunk\n\nSecond chunk",
    )

    assert tuple(
        item.evidence_id
        for item in context.items
    ) == (
        "chunk-a",
        "chunk-b",
    )


def test_filter_partition_is_keyed_by_evidence_identity() -> None:
    first = _evidence(
        "chunk-a",
        "source-1",
    )

    second = RetrievedEvidence(
        **{
            **first.model_dump(),
            "evidence_id": "chunk-b",
            "rank": 2,
        }
    )

    result = SourceFilterResult(
        eligible=(
            first,
            second,
        )
    )

    assert len(result.eligible) == 2


def test_provider_citations_are_evidence_ids() -> None:
    response = ProviderResponse(
        answer_text="Answer",
        cited_evidence_ids=(
            "chunk-a",
        ),
    )

    assert response.cited_evidence_ids == (
        "chunk-a",
    )

    assert (
        set(ProviderResponse.model_fields)
        == {
            "answer_text",
            "cited_evidence_ids",
        }
    )


def test_phase2_legacy_cited_source_ids_migrate() -> None:
    response = ProviderResponse.model_validate(
        {
            "answer_text": "Answer",
            "cited_source_ids": [
                "source-1"
            ],
        }
    )

    replay = ReplayEntry.model_validate(
        {
            "query": "Question",
            "answer_text": "Answer",
            "cited_source_ids": [
                "source-1"
            ],
        }
    )

    assert response.cited_evidence_ids == (
        "source-1",
    )

    assert replay.cited_evidence_ids == (
        "source-1",
    )


def test_phase2_indexed_document_identity_migrates() -> None:
    document = IndexedDocument.model_validate(
        {
            "source_id": "source-1",
            "content": "Evidence",
            "authority_level": "authoritative",
            "source_state": "current",
            "product_scope": "api.github.com",
            "api_version_or_snapshot": "2026-03-10",
        }
    )

    assert document.evidence_id == "source-1"
    assert document.source_ids == (
        "source-1",
    )
    assert document.document_ids == ()


def test_evaluation_gold_separates_evidence_from_sources() -> None:
    case = EvaluationCase(
        case_id="phase4-dev-001",
        case_version="1.0",
        data_role=EvaluationRole.DEVELOPMENT,
        source_family=(
            EvaluationSourceFamily.ISSUES
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        criticality=Criticality.CRITICAL,
        query="Question",
        expected_response_mode=(
            ResponseMode.ANSWER
        ),
        required_fact_ids=("fact-1",),
        required_evidence_ids=(
            "chunk-current",
        ),
        required_source_ids=(
            "openapi-current:issues/create",
        ),
        allowed_source_states=(
            SourceState.CURRENT,
        ),
        forbidden_evidence_ids=(
            "chunk-historical",
        ),
        forbidden_source_ids=(
            "openapi-historical:issues/create",
        ),
        required_api_version="2026-03-10",
        required_authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        gold_fact_rubric=(
            "Required supported fact.",
        ),
        scoring_notes="Phase 4 contract test.",
        authoring_evidence=(
            "chunk-current",
        ),
    )

    assert (
        case.required_evidence_ids
        != case.required_source_ids
    )

    assert case.to_runtime_input().model_dump() == {
        "case_id": "phase4-dev-001",
        "query": "Question",
    }


def test_phase2_case_source_identity_migrates_to_evidence_identity() -> None:
    case = EvaluationCase(
        case_id="legacy-dev-001",
        case_version="1.0",
        data_role=EvaluationRole.DEVELOPMENT,
        source_family=(
            EvaluationSourceFamily.ISSUES
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        criticality=Criticality.NONCRITICAL,
        query="Question",
        expected_response_mode=(
            ResponseMode.ANSWER
        ),
        required_fact_ids=("fact-1",),
        required_source_ids=("source-1",),
        allowed_source_states=(
            SourceState.CURRENT,
        ),
        required_api_version="2026-03-10",
        required_authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        gold_fact_rubric=("Fact",),
        scoring_notes="Legacy migration.",
        authoring_evidence=("source-1",),
    )

    assert case.required_evidence_ids == (
        "source-1",
    )


def test_trace_can_preserve_evidence_and_source_attribution() -> None:
    event = TraceEvent(
        event_id="trace-event-1",
        stage=TraceStage.RETRIEVAL,
        status=TraceStatus.OK,
        occurred_at=datetime.now(UTC),
        duration_ms=1.0,
        evidence_ids=(
            "chunk-a",
            "chunk-b",
        ),
        source_ids=(
            "source-1",
        ),
    )

    assert event.evidence_ids == (
        "chunk-a",
        "chunk-b",
    )

    assert event.source_ids == (
        "source-1",
    )