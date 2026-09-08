from __future__ import annotations

import asyncio
from pathlib import Path

from rag_reliability.config.identity import (
    CitationConfig,
    ContextConfig,
    RetrievalConfig,
    SourcePolicyConfig,
)
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CitationValidationStatus,
    SourceState,
)
from rag_reliability.contracts.runtime import (
    CitationValidationRequest,
    ContextBuildRequest,
    ProviderResponse,
    RetrievalRequest,
    SourceFilterRequest,
)
from rag_reliability.evaluation.full_corpus import (
    PHASE3D_CHUNK_COUNT,
    load_phase3d_indexed_documents,
)
from rag_reliability.runtime.citations import (
    ExactCitationValidator,
)
from rag_reliability.runtime.context import (
    BoundedContextBuilder,
)
from rag_reliability.runtime.filtering import (
    CurrentGithubRestSourcePolicyFilter,
)
from rag_reliability.runtime.models import (
    IndexedDocument,
)
from rag_reliability.runtime.retrieval import (
    LexicalRetriever,
)

ROOT = Path(__file__).resolve().parents[2]


def test_phase3d_runtime_projection_has_exact_frozen_identity() -> None:
    documents = (
        load_phase3d_indexed_documents(
            ROOT
        )
    )

    assert len(documents) == (
        PHASE3D_CHUNK_COUNT
    )

    evidence_ids = tuple(
        document.evidence_id
        for document in documents
    )

    assert len(evidence_ids) == 1333
    assert len(set(evidence_ids)) == 1333

    assert evidence_ids == tuple(
        sorted(evidence_ids)
    )


def test_phase3d_runtime_projection_preserves_parent_lineage() -> None:
    documents = (
        load_phase3d_indexed_documents(
            ROOT
        )
    )

    assert all(
        document.source_ids
        for document in documents
    )

    assert all(
        document.document_ids
        for document in documents
    )

    assert max(
        len(document.source_ids)
        for document in documents
    ) > 1

    assert max(
        len(document.document_ids)
        for document in documents
    ) > 1


def _shared_source_document(
    evidence_id: str,
    content: str,
) -> IndexedDocument:
    return IndexedDocument(
        evidence_id=evidence_id,
        source_ids=(
            "source-shared",
        ),
        document_ids=(
            "document-shared",
        ),
        content=content,
        authority_level=(
            AuthorityLevel.AUTHORITATIVE
        ),
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )


def test_runtime_keeps_multiple_chunks_from_same_source_distinct() -> None:
    documents = (
        _shared_source_document(
            "chunk-a",
            "issues labels first evidence",
        ),
        _shared_source_document(
            "chunk-b",
            "issues labels second evidence",
        ),
    )

    retrieval = asyncio.run(
        LexicalRetriever(
            RetrievalConfig(
                retriever_id="lexical-v1",
                top_k=2,
            ),
            documents,
        ).retrieve(
            RetrievalRequest(
                query="issues labels",
                top_k=2,
            )
        )
    )

    assert tuple(
        item.evidence_id
        for item in retrieval.items
    ) == (
        "chunk-a",
        "chunk-b",
    )

    filtered = asyncio.run(
        CurrentGithubRestSourcePolicyFilter(
            SourcePolicyConfig(
                policy_id=(
                    "github-rest-current-v1"
                )
            )
        ).apply(
            SourceFilterRequest(
                candidates=retrieval.items
            )
        )
    )

    assert len(filtered.eligible) == 2

    context = asyncio.run(
        BoundedContextBuilder(
            ContextConfig(
                builder_id=(
                    "bounded-context-v1"
                ),
                budget_unit_id="characters",
                max_budget=1000,
                max_evidence_items=2,
            )
        ).build(
            ContextBuildRequest(
                query="issues labels",
                evidence=filtered.eligible,
            )
        )
    )

    assert tuple(
        item.evidence_id
        for item in context.items
    ) == (
        "chunk-a",
        "chunk-b",
    )

    assert {
        source_id
        for item in context.items
        for source_id in item.source_ids
    } == {
        "source-shared"
    }


def test_citation_validation_is_keyed_by_evidence_id() -> None:
    document = _shared_source_document(
        "chunk-cited",
        "GitHub REST evidence.",
    )

    retrieval = asyncio.run(
        LexicalRetriever(
            RetrievalConfig(
                retriever_id="lexical-v1",
                top_k=1,
            ),
            (document,),
        ).retrieve(
            RetrievalRequest(
                query="GitHub REST evidence",
                top_k=1,
            )
        )
    )

    context = asyncio.run(
        BoundedContextBuilder(
            ContextConfig(
                builder_id=(
                    "bounded-context-v1"
                ),
                budget_unit_id="characters",
                max_budget=500,
                max_evidence_items=1,
            )
        ).build(
            ContextBuildRequest(
                query="GitHub REST evidence",
                evidence=retrieval.items,
            )
        )
    )

    result = asyncio.run(
        ExactCitationValidator(
            CitationConfig(
                validator_id=(
                    "exact-citation-v1"
                ),
                require_citations=True,
            )
        ).validate(
            CitationValidationRequest(
                provider_response=(
                    ProviderResponse(
                        answer_text=(
                            "GitHub REST evidence."
                        ),
                        cited_evidence_ids=(
                            "chunk-cited",
                        ),
                    )
                ),
                context=context,
            )
        )
    )

    assert (
        result.all_material_claims_supported
        is True
    )

    assert (
        result.checks[0].evidence_id
        == "chunk-cited"
    )

    assert (
        result.checks[0].status
        is CitationValidationStatus.SUPPORTED
    )