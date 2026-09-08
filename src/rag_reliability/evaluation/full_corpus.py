"""Project the frozen Phase 3D chunk corpus into runtime evidence records."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.corpus.chunked import (
    Phase3dChunkManifest,
)
from rag_reliability.runtime.models import (
    IndexedDocument,
)

PHASE3D_CHUNK_MANIFEST_SHA256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

PHASE3D_CHUNK_COUNT = 1333

_PHASE3D_MANIFEST_RELATIVE_PATH = Path(
    "datasets"
) / "chunk_manifests" / (
    "phase3d_chunk_manifest_v1.json"
)

_PHASE3D_CHUNK_ROOT_RELATIVE_PATH = (
    Path("datasets")
    / "chunks"
    / "phase3d_v1"
)


class Phase3dRuntimeCorpusError(
    ValueError
):
    """Frozen Phase 3D corpus cannot be safely projected to runtime."""


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _read_verified_manifest(
    repo_root: Path,
) -> Phase3dChunkManifest:
    path = (
        repo_root
        / _PHASE3D_MANIFEST_RELATIVE_PATH
    )

    content = path.read_bytes()

    observed_sha = _sha256_bytes(
        content
    )

    if (
        observed_sha
        != PHASE3D_CHUNK_MANIFEST_SHA256
    ):
        raise Phase3dRuntimeCorpusError(
            "Phase 3D chunk manifest SHA mismatch"
        )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    expected_sidecar = (
        f"{PHASE3D_CHUNK_MANIFEST_SHA256}  "
        f"{path.name}"
    )

    observed_sidecar = (
        sidecar.read_text(
            encoding="utf-8"
        )
        .strip()
    )

    if (
        observed_sidecar
        != expected_sidecar
    ):
        raise Phase3dRuntimeCorpusError(
            "Phase 3D chunk manifest sidecar mismatch"
        )

    return (
        Phase3dChunkManifest
        .model_validate_json(
            content
        )
    )


def load_phase3d_indexed_documents(
    repo_root: Path,
) -> tuple[IndexedDocument, ...]:
    """Load exactly the frozen 1,333 Phase 3D chunks for runtime retrieval."""

    manifest = _read_verified_manifest(
        repo_root
    )

    if (
        len(manifest.chunks)
        != PHASE3D_CHUNK_COUNT
    ):
        raise Phase3dRuntimeCorpusError(
            "Phase 3D chunk count mismatch"
        )

    chunk_root = (
        repo_root
        / _PHASE3D_CHUNK_ROOT_RELATIVE_PATH
    ).resolve()

    expected_paths: set[Path] = set()
    documents: list[
        IndexedDocument
    ] = []

    for chunk in manifest.chunks:
        path = (
            repo_root
            / Path(chunk.content_path)
        ).resolve()

        if not path.is_relative_to(
            chunk_root
        ):
            raise Phase3dRuntimeCorpusError(
                "chunk path escapes frozen "
                "Phase 3D chunk root"
            )

        expected_paths.add(path)

        content_bytes = path.read_bytes()

        if (
            len(content_bytes)
            != chunk.byte_count
        ):
            raise Phase3dRuntimeCorpusError(
                f"chunk byte-count mismatch: "
                f"{chunk.chunk_id}"
            )

        if (
            _sha256_bytes(content_bytes)
            != chunk.content_sha256
        ):
            raise Phase3dRuntimeCorpusError(
                f"chunk SHA mismatch: "
                f"{chunk.chunk_id}"
            )

        try:
            content = content_bytes.decode(
                "utf-8"
            )
        except UnicodeDecodeError as exc:
            raise Phase3dRuntimeCorpusError(
                f"chunk is not UTF-8: "
                f"{chunk.chunk_id}"
            ) from exc

        source_ids = tuple(
            parent.source_id
            for parent in chunk.parents
        )

        document_ids = tuple(
            parent.document_id
            for parent in chunk.parents
        )

        documents.append(
            IndexedDocument(
                evidence_id=chunk.chunk_id,
                source_ids=source_ids,
                document_ids=document_ids,
                content=content,
                authority_level=(
                    chunk.evidence_scope
                    .authority_level
                ),
                source_state=(
                    chunk.evidence_scope
                    .source_state
                ),
                product_scope=(
                    chunk.evidence_scope
                    .product_scope
                ),
                api_version_or_snapshot=(
                    chunk.evidence_scope
                    .api_version_or_snapshot
                ),
                synthetic_overlay=False,
                eligible_as_final_citation=True,
            )
        )

    observed_paths = {
        path.resolve()
        for path in chunk_root.rglob("*")
        if path.is_file()
    }

    if (
        observed_paths
        != expected_paths
    ):
        raise Phase3dRuntimeCorpusError(
            "Phase 3D chunk file set does "
            "not match the frozen manifest"
        )

    ordered = tuple(
        sorted(
            documents,
            key=lambda item: (
                item.evidence_id
            ),
        )
    )

    evidence_ids = tuple(
        item.evidence_id
        for item in ordered
    )

    if (
        len(evidence_ids)
        != len(set(evidence_ids))
    ):
        raise Phase3dRuntimeCorpusError(
            "runtime evidence IDs are not unique"
        )

    if (
        len(ordered)
        != PHASE3D_CHUNK_COUNT
    ):
        raise Phase3dRuntimeCorpusError(
            "runtime corpus projection "
            "count mismatch"
        )

    return ordered