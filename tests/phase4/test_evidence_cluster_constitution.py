from pathlib import Path

from rag_reliability.contracts.enums import (
    DataRole,
    EvaluationRole,
)
from rag_reliability.corpus.chunked import (
    Phase3dChunkManifest,
)
from rag_reliability.corpus.chunking import (
    ChunkKind,
)
from rag_reliability.evaluation.constitution import (
    Phase4EvidenceClusterConstitution,
)

ROOT = Path(__file__).resolve().parents[2]

CONSTITUTION_PATH = (
    ROOT
    / "datasets"
    / "evaluation"
    / "phase4_evidence_cluster_constitution_v1.json"
)

CHUNK_MANIFEST_PATH = (
    ROOT
    / "datasets"
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)


def _constitution(
) -> Phase4EvidenceClusterConstitution:
    return (
        Phase4EvidenceClusterConstitution
        .model_validate_json(
            CONSTITUTION_PATH.read_text(
                encoding="utf-8"
            )
        )
    )


def _manifest(
) -> Phase3dChunkManifest:
    return (
        Phase3dChunkManifest
        .model_validate_json(
            CHUNK_MANIFEST_PATH.read_text(
                encoding="utf-8"
            )
        )
    )


def test_constitution_freezes_30_clusters_and_60_cases() -> None:
    constitution = _constitution()

    assert len(
        constitution.clusters
    ) == 30

    assert (
        constitution.canonical_case_count
        == 60
    )

    assert (
        constitution.development_case_count
        == 24
    )

    assert (
        constitution.tuning_case_count
        == 18
    )

    assert (
        constitution.held_out_case_count
        == 18
    )


def test_cluster_roles_are_exactly_disjoint() -> None:
    constitution = _constitution()

    by_role = {
        role: {
            evidence_id
            for cluster
            in constitution.clusters
            if cluster.data_role is role
            for evidence_id
            in cluster.authoring_evidence_ids
        }
        for role in EvaluationRole
    }

    assert not (
        by_role[EvaluationRole.DEVELOPMENT]
        & by_role[EvaluationRole.TUNING]
    )

    assert not (
        by_role[EvaluationRole.DEVELOPMENT]
        & by_role[EvaluationRole.HELD_OUT]
    )

    assert not (
        by_role[EvaluationRole.TUNING]
        & by_role[EvaluationRole.HELD_OUT]
    )


def test_openapi_components_are_not_gold_authoring_evidence() -> None:
    constitution = _constitution()
    manifest = _manifest()

    gold_ids = {
        evidence_id
        for cluster in constitution.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    component_ids = {
        chunk.chunk_id
        for chunk in manifest.chunks
        if (
            chunk.chunk_kind
            is ChunkKind.OPENAPI_COMPONENT
        )
    }

    assert not (
        gold_ids
        & component_ids
    )


def test_background_load_chunks_are_not_gold_authoring_evidence() -> None:
    constitution = _constitution()
    manifest = _manifest()

    gold_ids = {
        evidence_id
        for cluster in constitution.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    background_ids = {
        chunk.chunk_id
        for chunk in manifest.chunks
        if (
            chunk.evidence_scope.data_role
            is DataRole.BACKGROUND_LOAD_SOURCE
        )
    }

    assert not (
        gold_ids
        & background_ids
    )


def test_every_gold_authoring_id_exists_in_frozen_chunk_manifest() -> None:
    constitution = _constitution()
    manifest = _manifest()

    manifest_ids = {
        chunk.chunk_id
        for chunk in manifest.chunks
    }

    gold_ids = {
        evidence_id
        for cluster in constitution.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    assert gold_ids <= manifest_ids