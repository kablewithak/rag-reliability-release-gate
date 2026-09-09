import hashlib
from pathlib import Path

from rag_reliability.contracts.enums import (
    DataRole,
)
from rag_reliability.corpus.chunked import (
    Phase3dChunkManifest,
)
from rag_reliability.corpus.chunking import (
    ChunkKind,
)
from rag_reliability.evaluation.authoring_dossier import (
    PHASE4_CONSTITUTION_SHA256,
    Phase4AuthoringDossier,
)
from rag_reliability.evaluation.constitution import (
    Phase4EvidenceClusterConstitution,
)

ROOT = Path(__file__).resolve().parents[2]

DOSSIER_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_authoring_dossier_v1.json"
)

MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_authoring_dossier_v1.md"
)

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


def _dossier(
) -> Phase4AuthoringDossier:
    return (
        Phase4AuthoringDossier
        .model_validate_json(
            DOSSIER_PATH.read_text(
                encoding="utf-8"
            )
        )
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


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def test_dossier_preserves_frozen_cluster_and_evidence_counts(
) -> None:
    dossier = _dossier()

    assert len(
        dossier.clusters
    ) == 30

    evidence_ids = {
        evidence_id
        for cluster in dossier.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    assert len(
        evidence_ids
    ) == 68

    assert (
        dossier.phase4_constitution_sha256
        == PHASE4_CONSTITUTION_SHA256
    )

    assert (
        dossier.case_authoring_authorized
        is True
    )

    assert (
        dossier.baseline_authorized
        is False
    )


def test_dossier_matches_constitution_exactly(
) -> None:
    dossier = _dossier()
    constitution = _constitution()

    constitution_by_id = {
        cluster.cluster_id: cluster
        for cluster
        in constitution.clusters
    }

    assert {
        cluster.cluster_id
        for cluster in dossier.clusters
    } == set(
        constitution_by_id
    )

    for review in dossier.clusters:
        frozen = constitution_by_id[
            review.cluster_id
        ]

        assert (
            review.evaluation_role
            is frozen.data_role
        )

        assert (
            review.cluster_kind
            is frozen.cluster_kind
        )

        assert (
            review.source_family
            is frozen.source_family
        )

        assert (
            review.operation_id
            == frozen.operation_id
        )

        assert (
            review.authored_source_id
            == frozen.authored_source_id
        )

        assert tuple(
            evidence.evidence_id
            for evidence
            in review.current_evidence
        ) == tuple(
            frozen.current_evidence_ids
        )

        assert tuple(
            evidence.evidence_id
            for evidence
            in review.historical_evidence
        ) == tuple(
            frozen.historical_evidence_ids
        )

        assert (
            review.current_source_ids
            == frozen.current_source_ids
        )

        assert (
            review.historical_source_ids
            == frozen.historical_source_ids
        )


def test_dossier_evidence_matches_frozen_chunk_manifest(
) -> None:
    dossier = _dossier()
    manifest = _manifest()

    chunk_by_id = {
        chunk.chunk_id: chunk
        for chunk in manifest.chunks
    }

    for cluster in dossier.clusters:
        for evidence in (
            *cluster.current_evidence,
            *cluster.historical_evidence,
        ):
            chunk = chunk_by_id[
                evidence.evidence_id
            ]

            assert (
                evidence.chunk_kind
                is chunk.chunk_kind
            )

            assert (
                evidence.content_path
                == chunk.content_path
            )

            assert (
                evidence.content_sha256
                == chunk.content_sha256
            )

            assert (
                evidence.byte_count
                == chunk.byte_count
            )

            assert (
                evidence.parents
                == chunk.parents
            )

            assert (
                evidence.evidence_scope
                == chunk.evidence_scope
            )

            content = (
                ROOT
                / evidence.content_path
            ).read_bytes()

            assert (
                len(content)
                == evidence.byte_count
            )

            assert (
                _sha256_bytes(content)
                == evidence.content_sha256
            )


def test_dossier_excludes_component_and_background_gold(
) -> None:
    dossier = _dossier()

    for cluster in dossier.clusters:
        for evidence in (
            *cluster.current_evidence,
            *cluster.historical_evidence,
        ):
            assert (
                evidence.chunk_kind
                is not ChunkKind.OPENAPI_COMPONENT
            )

            assert (
                evidence.evidence_scope.data_role
                is not DataRole.BACKGROUND_LOAD_SOURCE
            )


def test_markdown_review_is_hash_bound_to_dossier(
) -> None:
    dossier = _dossier()

    markdown_bytes = (
        MARKDOWN_PATH.read_bytes()
    )

    observed_sha = _sha256_bytes(
        markdown_bytes
    )

    assert (
        observed_sha
        == dossier.review_markdown_sha256
    )

    sidecar = MARKDOWN_PATH.with_suffix(
        ".md.sha256"
    )

    assert (
        sidecar.read_text(
            encoding="utf-8"
        ).strip()
        == (
            f"{observed_sha}  "
            f"{MARKDOWN_PATH.name}"
        )
    )
