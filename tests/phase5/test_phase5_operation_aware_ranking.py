from __future__ import annotations

import pytest

from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import RetrievedEvidence
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_resolution import (
    OperationResolution,
    ResolutionStatus,
)


def _item(evidence_id: str, rank: int, score: float) -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id=evidence_id,
        source_ids=(f"source-{evidence_id}",),
        document_ids=(f"document-{evidence_id}",),
        content=f"content-{evidence_id}",
        rank=rank,
        score=score,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="github-rest",
        api_version_or_snapshot="test",
    )


def test_resolved_partition_promotes_exact_lineage_stably() -> None:
    items = (
        _item("a", 1, 4.0),
        _item("b", 2, 3.0),
        _item("c", 3, 2.0),
        _item("d", 4, 1.0),
    )
    resolution = OperationResolution(
        status=ResolutionStatus.RESOLVED,
        operation_ids=("repos/create-in-org",),
    )
    lineage = {
        "a": (),
        "b": ("repos/create-in-org",),
        "c": (),
        "d": ("repos/create-in-org",),
    }

    ranked = stable_partition_by_operation_lineage(
        items=items,
        resolution=resolution,
        linked_operation_ids_by_evidence_id=lineage,
    )

    assert tuple(item.evidence_id for item in ranked) == ("b", "d", "a", "c")
    assert tuple(item.rank for item in ranked) == (1, 2, 3, 4)
    assert tuple(item.score for item in ranked) == (3.0, 1.0, 4.0, 2.0)


@pytest.mark.parametrize(
    "resolution",
    (
        OperationResolution(
            status=ResolutionStatus.AMBIGUOUS,
            operation_ids=("pulls/get", "pulls/update"),
        ),
        OperationResolution(
            status=ResolutionStatus.UNRESOLVED,
        ),
    ),
)
def test_nonresolved_partition_preserves_generic_ranking_exactly(
    resolution: OperationResolution,
) -> None:
    items = (
        _item("a", 1, 2.0),
        _item("b", 2, 1.0),
    )

    ranked = stable_partition_by_operation_lineage(
        items=items,
        resolution=resolution,
        linked_operation_ids_by_evidence_id={
            "b": ("pulls/get",),
        },
    )

    assert ranked is items


def test_resolved_partition_without_matching_lineage_is_exact_noop() -> None:
    items = (
        _item("a", 1, 2.0),
        _item("b", 2, 1.0),
    )

    ranked = stable_partition_by_operation_lineage(
        items=items,
        resolution=OperationResolution(
            status=ResolutionStatus.RESOLVED,
            operation_ids=("issues/create",),
        ),
        linked_operation_ids_by_evidence_id={},
    )

    assert ranked is items


def test_partition_rejects_noncontiguous_input_ranks() -> None:
    items = (
        _item("a", 1, 2.0),
        _item("b", 3, 1.0),
    )

    with pytest.raises(
        ValueError,
        match="requires contiguous input ranks",
    ):
        stable_partition_by_operation_lineage(
            items=items,
            resolution=OperationResolution(
                status=ResolutionStatus.UNRESOLVED,
            ),
            linked_operation_ids_by_evidence_id={},
        )
