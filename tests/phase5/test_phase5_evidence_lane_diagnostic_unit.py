from __future__ import annotations

from pathlib import Path

from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.evaluation.evidence_lane_diagnostic import (
    _load_manifest,
    _partition_documents_by_lane,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
)

ROOT = Path(__file__).resolve().parents[2]


def test_evidence_lane_partition_matches_frozen_manifest_counts() -> None:
    manifest = _load_manifest(ROOT)
    documents, _evidence_ids = _load_indexed_documents(ROOT)

    lanes = _partition_documents_by_lane(
        documents=documents,
        manifest=manifest,
    )

    assert len(lanes[ChunkKind.AUTHORED_SECTION]) == 26
    assert len(lanes[ChunkKind.OPENAPI_OPERATION_CORE]) == 504
    assert len(lanes[ChunkKind.OPENAPI_COMPONENT]) == 803

    combined = {
        item.evidence_id
        for lane in lanes.values()
        for item in lane
    }
    assert len(combined) == 1333


def test_evidence_lane_partition_is_disjoint() -> None:
    manifest = _load_manifest(ROOT)
    documents, _evidence_ids = _load_indexed_documents(ROOT)

    lanes = _partition_documents_by_lane(
        documents=documents,
        manifest=manifest,
    )

    lane_sets = tuple(
        {
            item.evidence_id
            for item in lanes[kind]
        }
        for kind in ChunkKind
    )

    assert lane_sets[0].isdisjoint(lane_sets[1])
    assert lane_sets[0].isdisjoint(lane_sets[2])
    assert lane_sets[1].isdisjoint(lane_sets[2])
