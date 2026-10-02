from __future__ import annotations

from pathlib import Path

from rag_reliability.contracts.runtime import RetrievedEvidence
from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
)
from rag_reliability.evaluation.stratified_retrieval_candidate import (
    IncumbentPreservingStratifiedRrfRanker,
)
from rag_reliability.evaluation.stratified_retrieval_candidate_protocol import (
    StratifiedRetrievalCandidateContractV1,
)

ROOT = Path(__file__).resolve().parents[2]


def _item(
    document: object,
    *,
    rank: int,
    score: float,
) -> RetrievedEvidence:
    from rag_reliability.runtime.models import IndexedDocument

    assert isinstance(document, IndexedDocument)
    return RetrievedEvidence(
        evidence_id=document.evidence_id,
        source_ids=document.source_ids,
        document_ids=document.document_ids,
        content=document.content,
        rank=rank,
        score=score,
        authority_level=document.authority_level,
        source_state=document.source_state,
        product_scope=document.product_scope,
        api_version_or_snapshot=document.api_version_or_snapshot,
        synthetic_overlay=document.synthetic_overlay,
        eligible_as_final_citation=document.eligible_as_final_citation,
    )


def test_stratified_ranker_rewards_agreement_and_stably_breaks_ties() -> None:
    documents, _ids = _load_indexed_documents(ROOT)
    first, second, third = documents[:3]

    incumbent = (
        _item(first, rank=1, score=1.0),
        _item(second, rank=2, score=0.5),
    )
    native_authored = (
        _item(first, rank=1, score=4.0),
        _item(third, rank=2, score=3.0),
    )

    ranker = IncumbentPreservingStratifiedRrfRanker(
        contract=StratifiedRetrievalCandidateContractV1(),
    )
    ranked = ranker.rank_all(
        incumbent_items=incumbent,
        lane_rankings={
            ChunkKind.AUTHORED_SECTION: native_authored,
            ChunkKind.OPENAPI_OPERATION_CORE: (),
            ChunkKind.OPENAPI_COMPONENT: (),
        },
    )

    assert ranked[0].evidence_id == first.evidence_id

    tied_ids = sorted((second.evidence_id, third.evidence_id))
    assert tuple(item.evidence_id for item in ranked[1:]) == tuple(tied_ids)

    assert ranked[0].score == (1 / 61) + (1 / 61)
    assert ranked[1].score == 1 / 62
    assert ranked[2].score == 1 / 62


def test_stratified_ranker_keeps_items_present_on_only_one_surface() -> None:
    documents, _ids = _load_indexed_documents(ROOT)
    first, second = documents[:2]

    ranker = IncumbentPreservingStratifiedRrfRanker(
        contract=StratifiedRetrievalCandidateContractV1(),
    )
    ranked = ranker.rank_all(
        incumbent_items=(_item(first, rank=1, score=1.0),),
        lane_rankings={
            ChunkKind.AUTHORED_SECTION: (),
            ChunkKind.OPENAPI_OPERATION_CORE: (
                _item(second, rank=1, score=2.0),
            ),
            ChunkKind.OPENAPI_COMPONENT: (),
        },
    )

    assert {item.evidence_id for item in ranked} == {
        first.evidence_id,
        second.evidence_id,
    }
    assert tuple(item.rank for item in ranked) == (1, 2)


def test_runtime_top_k_is_frozen_at_20() -> None:
    documents, _ids = _load_indexed_documents(ROOT)
    source = documents[0]

    ranker = IncumbentPreservingStratifiedRrfRanker(
        contract=StratifiedRetrievalCandidateContractV1(),
    )

    items = tuple(
        _item(source, rank=index, score=float(30 - index))
        .model_copy(
            update={"evidence_id": f"test-{index}"}
        )
        for index in range(1, 26)
    )

    assert len(ranker.runtime_top_k(items)) == 20
