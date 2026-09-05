import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import (
    RejectedEvidence,
    RetrievalResult,
    RetrievedEvidence,
    SourceFilterResult,
)


def evidence(source_id: str, rank: int) -> RetrievedEvidence:
    return RetrievedEvidence(
        source_id=source_id,
        content=f"Evidence for {source_id}",
        rank=rank,
        score=0.5,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="github-rest",
        api_version_or_snapshot="2026-03-10",
    )


def test_retrieval_result_rejects_duplicate_ranks() -> None:
    with pytest.raises(ValidationError):
        RetrievalResult(items=(evidence("source-1", 1), evidence("source-2", 1)))


def test_filter_result_rejects_source_in_both_partitions() -> None:
    item = evidence("source-1", 1)

    with pytest.raises(ValidationError):
        SourceFilterResult(
            eligible=(item,),
            rejected=(
                RejectedEvidence(
                    source_id="source-1",
                    reason_code="wrong_scope",
                ),
            ),
        )
