from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.chunking import (
    CHUNK_BYTE_BUDGET,
    CHUNK_OVERLAP_BYTES,
    ChunkEvidenceScope,
    ChunkKind,
    ChunkParentLineage,
    CorpusChunkRecord,
    Phase3dChunkingConfig,
    StructuralChunkingError,
    build_chunk_id,
    chunk_markdown_structurally,
    component_dedup_key,
    operation_core,
    split_json_structurally,
    utf8_size,
)

_SCOPE = ChunkEvidenceScope(
    source_family=CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT,
    source_state=SourceState.CURRENT,
    authority_level=AuthorityLevel.AUTHORITATIVE,
    data_role=DataRole.CORPUS_SOURCE,
    product_scope="api.github.com",
    api_version_or_snapshot="2026-03-10",
    source_commit_sha_or_version=(
        "3cef12e8a02d612ad032473d4fb87266f2befeae"
    ),
    source_license="MIT",
    source_url=(
        "https://raw.githubusercontent.com/"
        "github/rest-api-description/"
        "3cef12e8a02d612ad032473d4fb87266f2befeae/"
        "descriptions/api.github.com/"
        "api.github.com.2026-03-10.yaml"
    ),
)


def _operation_record(
    *,
    byte_count: int = 100,
) -> CorpusChunkRecord:
    return CorpusChunkRecord(
        chunk_id="chunk-test",
        chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
        content_path="datasets/chunks/chunk-test.json",
        content_sha256="0" * 64,
        byte_count=byte_count,
        chunking_policy_sha256="1" * 64,
        chunk_index=0,
        parents=(
            ChunkParentLineage(
                document_id="document-a",
                normalized_content_sha256="2" * 64,
                source_id="source-a",
            ),
        ),
        evidence_scope=_SCOPE,
        semantic_families=("issues",),
        linked_operation_ids=("issues/get",),
    )


def test_phase3d_candidate_policy_is_frozen_to_8k_zero_overlap() -> None:
    config = Phase3dChunkingConfig()

    assert config.byte_budget == 8192
    assert config.overlap_bytes == 0
    assert CHUNK_BYTE_BUDGET == 8192
    assert CHUNK_OVERLAP_BYTES == 0
    assert config.baseline_authorized is False
    assert config.release_eligible is False


def test_chunk_record_rejects_content_over_budget() -> None:
    with pytest.raises(ValidationError):
        _operation_record(
            byte_count=CHUNK_BYTE_BUDGET + 1
        )


def test_chunk_record_rejects_unsorted_parent_lineage() -> None:
    with pytest.raises(
        ValidationError,
        match="deterministically document-ID sorted",
    ):
        CorpusChunkRecord(
            chunk_id="chunk-test",
            chunk_kind=ChunkKind.OPENAPI_COMPONENT,
            content_path="datasets/chunks/chunk-test.json",
            content_sha256="0" * 64,
            byte_count=100,
            chunking_policy_sha256="1" * 64,
            chunk_index=0,
            parents=(
                ChunkParentLineage(
                    document_id="document-b",
                    normalized_content_sha256="2" * 64,
                    source_id="source-b",
                ),
                ChunkParentLineage(
                    document_id="document-a",
                    normalized_content_sha256="3" * 64,
                    source_id="source-a",
                ),
            ),
            evidence_scope=_SCOPE,
            semantic_families=("issues",),
            linked_operation_ids=(
                "issues/get",
                "issues/list",
            ),
            component_ref="#/components/schemas/issue",
        )


def test_chunk_record_rejects_duplicate_parent_lineage() -> None:
    parent = ChunkParentLineage(
        document_id="document-a",
        normalized_content_sha256="2" * 64,
        source_id="source-a",
    )

    with pytest.raises(
        ValidationError,
        match="document IDs must be unique",
    ):
        CorpusChunkRecord(
            chunk_id="chunk-test",
            chunk_kind=ChunkKind.OPENAPI_COMPONENT,
            content_path="datasets/chunks/chunk-test.json",
            content_sha256="0" * 64,
            byte_count=100,
            chunking_policy_sha256="1" * 64,
            chunk_index=0,
            parents=(parent, parent),
            evidence_scope=_SCOPE,
            semantic_families=("issues",),
            linked_operation_ids=("issues/get",),
            component_ref="#/components/schemas/issue",
        )

def test_chunk_id_is_deterministic() -> None:
    first = build_chunk_id(
        chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
        content_sha256="a" * 64,
        chunk_index=0,
        parent_document_ids=("document-a",),
        evidence_scope=_SCOPE,
    )

    second = build_chunk_id(
        chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
        content_sha256="a" * 64,
        chunk_index=0,
        parent_document_ids=("document-a",),
        evidence_scope=_SCOPE,
    )

    assert first == second
    assert first.startswith("chunk-")


def test_component_dedup_key_respects_data_role_boundary() -> None:
    component = {
        "description": "The repository owner.",
        "type": "string",
    }

    corpus_key = component_dedup_key(
        _SCOPE,
        "#/components/parameters/owner",
        component,
    )

    background_scope = _SCOPE.model_copy(
        update={
            "data_role": DataRole.BACKGROUND_LOAD_SOURCE,
        }
    )

    background_key = component_dedup_key(
        background_scope,
        "#/components/parameters/owner",
        component,
    )

    assert corpus_key != background_key


def test_small_json_remains_one_structural_chunk() -> None:
    payload = {
        "method": "get",
        "operation": {
            "operationId": "issues/get",
            "summary": "Get an issue",
        },
        "path": "/repos/{owner}/{repo}/issues/{issue_number}",
        "path_parameters": [],
        "referenced_components": {},
    }

    chunks = split_json_structurally(
        operation_core(payload)
    )

    assert len(chunks) == 1
    assert utf8_size(chunks[0]) <= CHUNK_BYTE_BUDGET

    rendered = json.loads(chunks[0])

    assert rendered["fragments"][0]["path"] == []


def test_large_nested_json_splits_only_at_structure() -> None:
    value = {
        "schemas": {
            f"schema-{index}": {
                "description": "x" * 600,
                "type": "string",
            }
            for index in range(30)
        }
    }

    chunks = split_json_structurally(
        value,
        budget=2048,
    )

    assert len(chunks) > 1
    assert all(
        utf8_size(chunk) <= 2048
        for chunk in chunks
    )

    for chunk in chunks:
        payload = json.loads(chunk)
        assert "fragments" in payload


def test_oversized_json_scalar_fails_closed() -> None:
    value = {
        "description": "x" * 9000,
    }

    with pytest.raises(
        StructuralChunkingError,
        match="scalar exceeds",
    ):
        split_json_structurally(value)


def test_markdown_chunking_preserves_exact_text() -> None:
    text = (
        "# First\n\n"
        "Alpha paragraph.\n\n"
        "# Second\n\n"
        "Beta paragraph.\n\n"
        "Gamma paragraph.\n"
    )

    chunks = chunk_markdown_structurally(
        text,
        budget=48,
    )

    assert "".join(
        chunk.text
        for chunk in chunks
    ) == text

    assert all(
        utf8_size(chunk.text) <= 48
        for chunk in chunks
    )


def test_markdown_chunk_metadata_preserves_heading_context() -> None:
    text = (
        "# Authentication\n\n"
        "Use an authentication token.\n\n"
        "Do not expose credentials.\n"
    )

    chunks = chunk_markdown_structurally(
        text,
        budget=48,
    )

    assert chunks
    assert all(
        chunk.section_headings == ("Authentication",)
        for chunk in chunks
    )


def test_oversized_markdown_atomic_block_fails_closed() -> None:
    text = "# Heading\n\n" + ("x" * 9000)

    with pytest.raises(
        StructuralChunkingError,
        match="atomic block exceeds",
    ):
        chunk_markdown_structurally(text)