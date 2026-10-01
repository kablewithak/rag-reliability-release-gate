"""Deterministic Phase 5 same-source companion rescue candidate."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import RetrievedEvidence
from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    OperationResolution,
    ResolutionStatus,
)


class CompanionChunkMetadata(ContractModel):
    """Narrow frozen chunk metadata visible to the companion candidate."""

    evidence_id: NonEmptyStr
    chunk_kind: ChunkKind
    source_ids: tuple[NonEmptyStr, ...] = Field(min_length=1)
    source_state: SourceState
    authority_level: AuthorityLevel


def _validate_contiguous_ranks(
    items: tuple[RetrievedEvidence, ...],
) -> None:
    observed = tuple(item.rank for item in items)
    expected = tuple(range(1, len(items) + 1))

    if observed != expected:
        raise ValueError(
            "source-companion rescue requires contiguous input ranks"
        )

    evidence_ids = tuple(item.evidence_id for item in items)

    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError(
            "source-companion rescue requires unique evidence IDs"
        )


def _is_current_authoritative_authored(
    metadata: CompanionChunkMetadata,
) -> bool:
    return (
        metadata.chunk_kind is ChunkKind.AUTHORED_SECTION
        and metadata.source_state is SourceState.CURRENT
        and metadata.authority_level is AuthorityLevel.AUTHORITATIVE
    )


def stable_rescue_same_source_companions(
    *,
    items: tuple[RetrievedEvidence, ...],
    metadata_by_evidence_id: Mapping[
        str,
        CompanionChunkMetadata,
    ],
    anchor_window: int = 5,
) -> tuple[RetrievedEvidence, ...]:
    """Promote same-source authored siblings after the highest-ranked anchor."""

    if anchor_window < 1:
        raise ValueError("anchor_window must be positive")

    _validate_contiguous_ranks(items)

    missing = tuple(
        item.evidence_id
        for item in items
        if item.evidence_id not in metadata_by_evidence_id
    )

    if missing:
        raise ValueError(
            "frozen chunk metadata missing for ranked evidence: "
            f"{missing[0]}"
        )

    anchor_index: int | None = None
    anchor_source_id: str | None = None

    for index, item in enumerate(items[:anchor_window]):
        metadata = metadata_by_evidence_id[item.evidence_id]

        if not _is_current_authoritative_authored(metadata):
            continue

        source_ids = tuple(sorted(set(metadata.source_ids)))

        if len(source_ids) != 1:
            return items

        anchor_index = index
        anchor_source_id = source_ids[0]
        break

    if anchor_index is None or anchor_source_id is None:
        return items

    prefix = items[:anchor_index]
    anchor = items[anchor_index]
    suffix = items[anchor_index + 1 :]

    companions: list[RetrievedEvidence] = []
    remainder: list[RetrievedEvidence] = []

    for item in suffix:
        metadata = metadata_by_evidence_id[item.evidence_id]
        is_companion = (
            _is_current_authoritative_authored(metadata)
            and anchor_source_id in metadata.source_ids
        )

        if is_companion:
            companions.append(item)
        else:
            remainder.append(item)

    if not companions:
        return items

    reordered = (
        *prefix,
        anchor,
        *companions,
        *remainder,
    )

    original_scores = {
        item.evidence_id: item.score
        for item in items
    }

    reranked = tuple(
        item
        if item.rank == rank
        else item.model_copy(update={"rank": rank})
        for rank, item in enumerate(reordered, start=1)
    )

    if any(
        item.score != original_scores[item.evidence_id]
        for item in reranked
    ):
        raise ValueError(
            "source-companion rescue changed retrieval scores"
        )

    return reranked


class SourceCompanionRescueCandidate:
    """Apply the frozen rescue only to ambiguous or unresolved queries."""

    def __init__(
        self,
        *,
        resolver: DeterministicOperationResolver,
        metadata_by_evidence_id: Mapping[
            str,
            CompanionChunkMetadata,
        ],
    ) -> None:
        self._resolver = resolver
        self._metadata_by_evidence_id = dict(
            metadata_by_evidence_id
        )

    def rank(
        self,
        *,
        query: str,
        current_ranked_retrieval: tuple[
            RetrievedEvidence,
            ...,
        ],
    ) -> tuple[
        OperationResolution,
        tuple[RetrievedEvidence, ...],
    ]:
        resolution = self._resolver.resolve(query)

        if resolution.status is ResolutionStatus.RESOLVED:
            return resolution, current_ranked_retrieval

        if resolution.status not in {
            ResolutionStatus.AMBIGUOUS,
            ResolutionStatus.UNRESOLVED,
        }:
            raise ValueError(
                f"unsupported resolution status: {resolution.status}"
            )

        rescued = stable_rescue_same_source_companions(
            items=current_ranked_retrieval,
            metadata_by_evidence_id=self._metadata_by_evidence_id,
            anchor_window=5,
        )

        return resolution, rescued
