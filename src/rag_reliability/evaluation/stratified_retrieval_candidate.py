"""Deterministic incumbent-preserving stratified RRF candidate mechanics."""

from __future__ import annotations

from collections.abc import Mapping

from rag_reliability.contracts.runtime import RetrievedEvidence
from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.evaluation.stratified_retrieval_candidate_protocol import (
    StratifiedRetrievalCandidateContractV1,
)


class IncumbentPreservingStratifiedRrfRanker:
    """Fuse incumbent rank with each item's native-lane BM25 rank."""

    def __init__(
        self,
        *,
        contract: StratifiedRetrievalCandidateContractV1,
    ) -> None:
        if contract.merge_method != (
            "equal_weight_rrf_incumbent_rank_plus_native_lane_rank"
        ):
            raise ValueError("unsupported stratified merge method")
        if contract.post_merge_operation_partition:
            raise ValueError("post-merge operation partition is forbidden")
        if (
            contract.raw_cross_lane_score_comparison_used
            or contract.fixed_lane_quota_used
            or contract.round_robin_merge_used
        ):
            raise ValueError("unsupported stratified merge semantics")

        self._contract = contract

    def rank_all(
        self,
        *,
        incumbent_items: tuple[RetrievedEvidence, ...],
        lane_rankings: Mapping[
            ChunkKind,
            tuple[RetrievedEvidence, ...],
        ],
    ) -> tuple[RetrievedEvidence, ...]:
        expected_lanes = set(ChunkKind)
        if set(lane_rankings) != expected_lanes:
            raise ValueError("stratified candidate requires all frozen chunk-kind lanes")

        incumbent_by_id = {
            item.evidence_id: item
            for item in incumbent_items
        }
        incumbent_rank = {
            item.evidence_id: item.rank
            for item in incumbent_items
        }

        native_by_id: dict[str, RetrievedEvidence] = {}
        native_rank: dict[str, int] = {}

        for kind in ChunkKind:
            for item in lane_rankings[kind]:
                if item.evidence_id in native_by_id:
                    raise ValueError(
                        "native lane rankings must be disjoint by evidence_id"
                    )
                native_by_id[item.evidence_id] = item
                native_rank[item.evidence_id] = item.rank

        evidence_ids = set(incumbent_by_id) | set(native_by_id)
        fused: list[tuple[float, RetrievedEvidence]] = []

        for evidence_id in evidence_ids:
            score = 0.0

            if evidence_id in incumbent_rank:
                score += (
                    self._contract.incumbent_rank_weight
                    / (
                        self._contract.fusion_constant
                        + incumbent_rank[evidence_id]
                    )
                )

            if evidence_id in native_rank:
                score += (
                    self._contract.native_lane_rank_weight
                    / (
                        self._contract.fusion_constant
                        + native_rank[evidence_id]
                    )
                )

            source = (
                incumbent_by_id[evidence_id]
                if evidence_id in incumbent_by_id
                else native_by_id[evidence_id]
            )
            fused.append((score, source))

        fused.sort(
            key=lambda item: (
                -item[0],
                item[1].evidence_id,
            )
        )

        return tuple(
            source.model_copy(
                update={
                    "rank": rank,
                    "score": score,
                }
            )
            for rank, (score, source) in enumerate(
                fused,
                start=1,
            )
        )

    def runtime_top_k(
        self,
        ranked: tuple[RetrievedEvidence, ...],
    ) -> tuple[RetrievedEvidence, ...]:
        return ranked[: self._contract.final_retrieval_top_k]
