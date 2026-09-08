"""Phase 3D chunk-corpus custody contracts."""

from __future__ import annotations

from collections import Counter
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    Sha256,
)
from rag_reliability.corpus.chunking import (
    ChunkKind,
    CorpusChunkRecord,
)

PHASE3B_NORMALIZED_MANIFEST_SHA256: Literal[
    "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
] = "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"

PHASE3C_NORMALIZED_MANIFEST_SHA256: Literal[
    "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"
] = "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"

EXPECTED_INPUT_DOCUMENT_COUNT: Literal[509] = 509
EXPECTED_MARKDOWN_CHUNK_COUNT: Literal[26] = 26
EXPECTED_OPERATION_CORE_CHUNK_COUNT: Literal[504] = 504
EXPECTED_COMPONENT_CHUNK_COUNT: Literal[803] = 803
EXPECTED_TOTAL_CHUNK_COUNT: Literal[1333] = 1333

EXPECTED_COMPONENT_OCCURRENCE_COUNT: Literal[4884] = 4884
EXPECTED_UNIQUE_SCOPED_COMPONENT_COUNT: Literal[747] = 747
EXPECTED_DUPLICATE_COMPONENT_OCCURRENCE_COUNT: Literal[4137] = 4137


class Phase3dChunkManifest(ContractModel):
    """Frozen file-backed Phase 3D retrieval chunk corpus."""

    manifest_version: Literal[
        "phase3d-chunk-manifest-v1"
    ] = "phase3d-chunk-manifest-v1"

    phase3b_normalized_manifest_sha256: Literal[
        "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
    ] = PHASE3B_NORMALIZED_MANIFEST_SHA256

    phase3c_normalized_manifest_sha256: Literal[
        "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"
    ] = PHASE3C_NORMALIZED_MANIFEST_SHA256

    chunking_config_sha256: Sha256

    input_document_count: Literal[509] = EXPECTED_INPUT_DOCUMENT_COUNT

    chunks: tuple[CorpusChunkRecord, ...] = Field(
        min_length=1333,
        max_length=1333,
    )

    markdown_chunk_count: Literal[26] = EXPECTED_MARKDOWN_CHUNK_COUNT
    operation_core_chunk_count: Literal[
        504
    ] = EXPECTED_OPERATION_CORE_CHUNK_COUNT
    component_chunk_count: Literal[803] = EXPECTED_COMPONENT_CHUNK_COUNT
    total_chunk_count: Literal[1333] = EXPECTED_TOTAL_CHUNK_COUNT

    component_occurrence_count: Literal[
        4884
    ] = EXPECTED_COMPONENT_OCCURRENCE_COUNT
    unique_scoped_component_count: Literal[
        747
    ] = EXPECTED_UNIQUE_SCOPED_COMPONENT_COUNT
    duplicate_component_occurrence_count: Literal[
        4137
    ] = EXPECTED_DUPLICATE_COMPONENT_OCCURRENCE_COUNT

    chunking_status: Literal["complete"] = "complete"
    chunked_corpus_ready: Literal[True] = True

    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_frozen_chunk_corpus(self) -> Self:
        if (
            self.markdown_chunk_count
            + self.operation_core_chunk_count
            + self.component_chunk_count
            != self.total_chunk_count
        ):
            raise ValueError(
                "chunk-kind counts do not reconcile to total chunk count"
            )

        if (
            self.unique_scoped_component_count
            + self.duplicate_component_occurrence_count
            != self.component_occurrence_count
        ):
            raise ValueError(
                "component deduplication counts do not reconcile"
            )

        chunk_ids = tuple(
            chunk.chunk_id
            for chunk in self.chunks
        )

        if chunk_ids != tuple(sorted(chunk_ids)):
            raise ValueError(
                "chunk manifest must be chunk-ID sorted"
            )

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError(
                "chunk IDs must be unique"
            )

        content_paths = tuple(
            chunk.content_path
            for chunk in self.chunks
        )

        if len(content_paths) != len(set(content_paths)):
            raise ValueError(
                "chunk content paths must be unique"
            )

        observed_counts = Counter(
            chunk.chunk_kind
            for chunk in self.chunks
        )

        expected_counts = Counter(
            {
                ChunkKind.AUTHORED_SECTION: (
                    self.markdown_chunk_count
                ),
                ChunkKind.OPENAPI_OPERATION_CORE: (
                    self.operation_core_chunk_count
                ),
                ChunkKind.OPENAPI_COMPONENT: (
                    self.component_chunk_count
                ),
            }
        )

        if observed_counts != expected_counts:
            raise ValueError(
                "observed chunk-kind counts do not match frozen counts"
            )

        policy_hashes = {
            chunk.chunking_policy_sha256
            for chunk in self.chunks
        }

        if policy_hashes != {
            self.chunking_config_sha256
        }:
            raise ValueError(
                "chunk records do not share the frozen chunking policy"
            )

        return self


class Phase3dChunkingReceipt(ContractModel):
    """Completion receipt for the Phase 3D chunk materialization boundary."""

    receipt_version: Literal[
        "phase3d-chunking-receipt-v1"
    ] = "phase3d-chunking-receipt-v1"

    phase3b_normalized_manifest_sha256: Literal[
        "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
    ] = PHASE3B_NORMALIZED_MANIFEST_SHA256

    phase3c_normalized_manifest_sha256: Literal[
        "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"
    ] = PHASE3C_NORMALIZED_MANIFEST_SHA256

    chunking_config_sha256: Sha256
    chunk_manifest_sha256: Sha256

    input_document_count: Literal[509] = EXPECTED_INPUT_DOCUMENT_COUNT
    input_file_identity_match_count: Literal[
        509
    ] = EXPECTED_INPUT_DOCUMENT_COUNT

    markdown_chunk_count: Literal[26] = EXPECTED_MARKDOWN_CHUNK_COUNT
    operation_core_chunk_count: Literal[
        504
    ] = EXPECTED_OPERATION_CORE_CHUNK_COUNT
    component_chunk_count: Literal[803] = EXPECTED_COMPONENT_CHUNK_COUNT
    total_chunk_count: Literal[1333] = EXPECTED_TOTAL_CHUNK_COUNT
    chunk_file_identity_match_count: Literal[
        1333
    ] = EXPECTED_TOTAL_CHUNK_COUNT

    component_occurrence_count: Literal[
        4884
    ] = EXPECTED_COMPONENT_OCCURRENCE_COUNT
    unique_scoped_component_count: Literal[
        747
    ] = EXPECTED_UNIQUE_SCOPED_COMPONENT_COUNT
    duplicate_component_occurrence_count: Literal[
        4137
    ] = EXPECTED_DUPLICATE_COMPONENT_OCCURRENCE_COUNT

    chunking_status: Literal["complete"] = "complete"
    chunked_corpus_ready: Literal[True] = True

    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_receipt(self) -> Self:
        if (
            self.markdown_chunk_count
            + self.operation_core_chunk_count
            + self.component_chunk_count
            != self.total_chunk_count
        ):
            raise ValueError(
                "receipt chunk counts do not reconcile"
            )

        if (
            self.unique_scoped_component_count
            + self.duplicate_component_occurrence_count
            != self.component_occurrence_count
        ):
            raise ValueError(
                "receipt component counts do not reconcile"
            )

        return self