from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.chunked import (
    Phase3dChunkingReceipt,
    Phase3dChunkManifest,
)
from rag_reliability.corpus.chunking import (
    CHUNK_BYTE_BUDGET,
    ChunkKind,
    Phase3dChunkingConfig,
)

ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = (
    ROOT
    / "datasets"
    / "chunk_manifests"
    / "phase3d_structural_chunking_config_v1.json"
)

MANIFEST_PATH = (
    ROOT
    / "datasets"
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase3d_chunking_receipt_v1.json"
)

CHUNK_ROOT = (
    ROOT
    / "datasets"
    / "chunks"
    / "phase3d_v1"
)

EXPECTED_CONFIG_SHA = (
    "5a76bbc64d4a10bada0d7efe7cc52eb7929dd8cd8ac1fb474aa2c63e775c0dda"
)

EXPECTED_MANIFEST_SHA = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

EXPECTED_RECEIPT_SHA = (
    "4ed1115473192b62000d3772455606996cd9ae5c633db50a7c74ad07d396fe29"
)


def _verified_bytes(
    path: Path,
    expected_sha: str,
) -> bytes:
    content = path.read_bytes()

    assert (
        hashlib.sha256(content).hexdigest()
        == expected_sha
    )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    assert (
        sidecar.read_text(
            encoding="utf-8"
        ).strip()
        == f"{expected_sha}  {path.name}"
    )

    return content


def test_phase3d_control_artifact_identities_are_frozen() -> None:
    config = Phase3dChunkingConfig.model_validate_json(
        _verified_bytes(
            CONFIG_PATH,
            EXPECTED_CONFIG_SHA,
        )
    )

    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            MANIFEST_PATH,
            EXPECTED_MANIFEST_SHA,
        )
    )

    receipt = Phase3dChunkingReceipt.model_validate_json(
        _verified_bytes(
            RECEIPT_PATH,
            EXPECTED_RECEIPT_SHA,
        )
    )

    assert config.byte_budget == 8192
    assert config.overlap_bytes == 0

    assert (
        manifest.chunking_config_sha256
        == EXPECTED_CONFIG_SHA
    )

    assert (
        receipt.chunking_config_sha256
        == EXPECTED_CONFIG_SHA
    )

    assert (
        receipt.chunk_manifest_sha256
        == EXPECTED_MANIFEST_SHA
    )

    assert manifest.baseline_authorized is False
    assert manifest.release_eligible is False
    assert receipt.baseline_authorized is False
    assert receipt.release_eligible is False


def test_phase3d_manifest_has_frozen_chunk_counts() -> None:
    manifest = Phase3dChunkManifest.model_validate_json(
        MANIFEST_PATH.read_bytes()
    )

    assert manifest.total_chunk_count == 1333
    assert manifest.markdown_chunk_count == 26
    assert manifest.operation_core_chunk_count == 504
    assert manifest.component_chunk_count == 803

    assert manifest.component_occurrence_count == 4884
    assert manifest.unique_scoped_component_count == 747
    assert (
        manifest.duplicate_component_occurrence_count
        == 4137
    )

    observed = {
        kind: sum(
            chunk.chunk_kind is kind
            for chunk in manifest.chunks
        )
        for kind in ChunkKind
    }

    assert observed == {
        ChunkKind.AUTHORED_SECTION: 26,
        ChunkKind.OPENAPI_OPERATION_CORE: 504,
        ChunkKind.OPENAPI_COMPONENT: 803,
    }


def test_phase3d_chunk_file_set_and_identity_match_manifest() -> None:
    manifest = Phase3dChunkManifest.model_validate_json(
        MANIFEST_PATH.read_bytes()
    )

    expected_paths = {
        (
            ROOT
            / Path(chunk.content_path)
        ).resolve()
        for chunk in manifest.chunks
    }

    observed_paths = {
        path.resolve()
        for path in CHUNK_ROOT.rglob("*")
        if path.is_file()
    }

    assert observed_paths == expected_paths

    for chunk in manifest.chunks:
        path = (
            ROOT
            / Path(chunk.content_path)
        )

        content = path.read_bytes()

        assert len(content) == chunk.byte_count
        assert len(content) <= CHUNK_BYTE_BUDGET

        assert (
            hashlib.sha256(content).hexdigest()
            == chunk.content_sha256
        )


def test_phase3d_chunk_lineage_covers_all_509_inputs() -> None:
    manifest = Phase3dChunkManifest.model_validate_json(
        MANIFEST_PATH.read_bytes()
    )

    source_document_ids: set[str] = set()

    for source_manifest in (
        ROOT
        / "datasets"
        / "source_manifests"
        / "phase3b_normalized_corpus_v1.json",
        ROOT
        / "datasets"
        / "source_manifests"
        / "phase3c_background_normalized_corpus_v1.json",
    ):
        payload = json.loads(
            source_manifest.read_text(
                encoding="utf-8"
            )
        )

        source_document_ids.update(
            document["document_id"]
            for document in payload["documents"]
        )

    assert len(source_document_ids) == 509

    all_parent_ids = {
        parent.document_id
        for chunk in manifest.chunks
        for parent in chunk.parents
    }

    assert all_parent_ids == source_document_ids

    authored_parent_ids = {
        parent.document_id
        for chunk in manifest.chunks
        if chunk.chunk_kind is ChunkKind.AUTHORED_SECTION
        for parent in chunk.parents
    }

    operation_parent_ids = {
        parent.document_id
        for chunk in manifest.chunks
        if chunk.chunk_kind
        is ChunkKind.OPENAPI_OPERATION_CORE
        for parent in chunk.parents
    }

    assert len(authored_parent_ids) == 10
    assert len(operation_parent_ids) == 499

    assert (
        authored_parent_ids
        | operation_parent_ids
        == source_document_ids
    )