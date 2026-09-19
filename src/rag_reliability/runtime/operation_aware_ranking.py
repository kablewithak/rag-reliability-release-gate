"""Deterministic operation-aware stable partition for an existing ranking."""

from __future__ import annotations

from collections.abc import Mapping

from rag_reliability.contracts.runtime import RetrievedEvidence
from rag_reliability.runtime.operation_resolution import (
    OperationResolution,
    ResolutionStatus,
)


def stable_partition_by_operation_lineage(
    *,
    items: tuple[RetrievedEvidence, ...],
    resolution: OperationResolution,
    linked_operation_ids_by_evidence_id: Mapping[str, tuple[str, ...]],
) -> tuple[RetrievedEvidence, ...]:
    """Move exact resolved-operation lineage first without changing scores."""

    expected_ranks = tuple(range(1, len(items) + 1))
    observed_ranks = tuple(item.rank for item in items)

    if observed_ranks != expected_ranks:
        raise ValueError("operation-aware partition requires contiguous input ranks")

    if resolution.status is not ResolutionStatus.RESOLVED:
        return items

    operation_id = resolution.operation_ids[0]

    promoted = tuple(
        item
        for item in items
        if operation_id
        in linked_operation_ids_by_evidence_id.get(
            item.evidence_id,
            (),
        )
    )

    if not promoted:
        return items

    remainder = tuple(
        item
        for item in items
        if operation_id
        not in linked_operation_ids_by_evidence_id.get(
            item.evidence_id,
            (),
        )
    )

    reordered = (*promoted, *remainder)

    return tuple(
        item if item.rank == rank else item.model_copy(update={"rank": rank})
        for rank, item in enumerate(reordered, start=1)
    )
