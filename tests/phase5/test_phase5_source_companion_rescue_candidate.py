from __future__ import annotations

from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import RetrievedEvidence
from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.evaluation.source_companion_rescue_candidate import (
    CompanionChunkMetadata,
    stable_rescue_same_source_companions,
)


def _item(
    evidence_id: str,
    rank: int,
    score: float,
) -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id=evidence_id,
        source_ids=(f"source-{evidence_id}",),
        document_ids=(f"doc-{evidence_id}",),
        content=f"content {evidence_id}",
        rank=rank,
        score=score,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )


def _metadata(
    evidence_id: str,
    source_id: str,
    *,
    chunk_kind: ChunkKind = ChunkKind.AUTHORED_SECTION,
    source_state: SourceState = SourceState.CURRENT,
    authority_level: AuthorityLevel = AuthorityLevel.AUTHORITATIVE,
) -> CompanionChunkMetadata:
    return CompanionChunkMetadata(
        evidence_id=evidence_id,
        chunk_kind=chunk_kind,
        source_ids=(source_id,),
        source_state=source_state,
        authority_level=authority_level,
    )


def test_same_source_sibling_moves_immediately_after_anchor() -> None:
    items = (
        _item("a", 1, 1.0),
        _item("anchor", 2, 0.9),
        _item("x", 3, 0.8),
        _item("sibling", 4, 0.7),
    )

    metadata = {
        "a": _metadata(
            "a",
            "other-a",
            chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
        ),
        "anchor": _metadata(
            "anchor",
            "docs-guidance",
        ),
        "x": _metadata(
            "x",
            "other-x",
            chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
        ),
        "sibling": _metadata(
            "sibling",
            "docs-guidance",
        ),
    }

    result = stable_rescue_same_source_companions(
        items=items,
        metadata_by_evidence_id=metadata,
    )

    assert tuple(item.evidence_id for item in result) == (
        "a",
        "anchor",
        "sibling",
        "x",
    )
    assert tuple(item.rank for item in result) == (
        1,
        2,
        3,
        4,
    )
    assert {
        item.evidence_id: item.score
        for item in result
    } == {
        item.evidence_id: item.score
        for item in items
    }


def test_highest_ranked_eligible_anchor_wins() -> None:
    items = (
        _item("anchor-1", 1, 1.0),
        _item("anchor-2", 2, 0.9),
        _item("sibling-2", 3, 0.8),
        _item("sibling-1", 4, 0.7),
    )

    metadata = {
        "anchor-1": _metadata(
            "anchor-1",
            "source-1",
        ),
        "anchor-2": _metadata(
            "anchor-2",
            "source-2",
        ),
        "sibling-2": _metadata(
            "sibling-2",
            "source-2",
        ),
        "sibling-1": _metadata(
            "sibling-1",
            "source-1",
        ),
    }

    result = stable_rescue_same_source_companions(
        items=items,
        metadata_by_evidence_id=metadata,
    )

    assert tuple(item.evidence_id for item in result) == (
        "anchor-1",
        "sibling-1",
        "anchor-2",
        "sibling-2",
    )


def test_ineligible_authored_chunks_are_not_anchors_or_companions() -> None:
    items = (
        _item("historical", 1, 1.0),
        _item("anchor", 2, 0.9),
        _item("historical-sibling", 3, 0.8),
        _item("current-sibling", 4, 0.7),
    )

    metadata = {
        "historical": _metadata(
            "historical",
            "docs-guidance",
            source_state=SourceState.HISTORICAL_COMPARISON,
        ),
        "anchor": _metadata(
            "anchor",
            "docs-guidance",
        ),
        "historical-sibling": _metadata(
            "historical-sibling",
            "docs-guidance",
            source_state=SourceState.HISTORICAL_COMPARISON,
        ),
        "current-sibling": _metadata(
            "current-sibling",
            "docs-guidance",
        ),
    }

    result = stable_rescue_same_source_companions(
        items=items,
        metadata_by_evidence_id=metadata,
    )

    assert tuple(item.evidence_id for item in result) == (
        "historical",
        "anchor",
        "current-sibling",
        "historical-sibling",
    )


def test_no_anchor_in_first_five_preserves_ranking_exactly() -> None:
    items = tuple(
        _item(
            f"evidence-{index}",
            index,
            1.0 / index,
        )
        for index in range(1, 7)
    )

    metadata = {
        item.evidence_id: _metadata(
            item.evidence_id,
            f"source-{item.evidence_id}",
            chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
        )
        for item in items
    }

    result = stable_rescue_same_source_companions(
        items=items,
        metadata_by_evidence_id=metadata,
    )

    assert result == items


def test_missing_metadata_fails_closed() -> None:
    items = (
        _item("a", 1, 1.0),
        _item("b", 2, 0.9),
    )

    metadata = {
        "a": _metadata(
            "a",
            "source-a",
        ),
    }

    try:
        stable_rescue_same_source_companions(
            items=items,
            metadata_by_evidence_id=metadata,
        )
    except ValueError as exc:
        assert "metadata missing" in str(exc)
    else:
        raise AssertionError(
            "expected missing metadata to fail closed"
        )
