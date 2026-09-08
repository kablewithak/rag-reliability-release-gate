"""Materialize and verify the frozen Phase 3D structural chunk corpus."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from rag_reliability.corpus.background_normalized import (
    Phase3cBackgroundNormalizedCorpusManifest,
)
from rag_reliability.corpus.chunked import (
    EXPECTED_COMPONENT_CHUNK_COUNT,
    EXPECTED_COMPONENT_OCCURRENCE_COUNT,
    EXPECTED_DUPLICATE_COMPONENT_OCCURRENCE_COUNT,
    EXPECTED_INPUT_DOCUMENT_COUNT,
    EXPECTED_MARKDOWN_CHUNK_COUNT,
    EXPECTED_OPERATION_CORE_CHUNK_COUNT,
    EXPECTED_TOTAL_CHUNK_COUNT,
    EXPECTED_UNIQUE_SCOPED_COMPONENT_COUNT,
    PHASE3B_NORMALIZED_MANIFEST_SHA256,
    PHASE3C_NORMALIZED_MANIFEST_SHA256,
    Phase3dChunkingReceipt,
    Phase3dChunkManifest,
)
from rag_reliability.corpus.chunking import (
    ChunkEvidenceScope,
    ChunkKind,
    ChunkParentLineage,
    CorpusChunkRecord,
    Phase3dChunkingConfig,
    build_chunk_id,
    canonical_json_text,
    chunk_markdown_structurally,
    component_dedup_key,
    operation_core,
    referenced_components,
    sha256_text,
    split_json_structurally,
    utf8_size,
)
from rag_reliability.corpus.models import SemanticOperationFamily
from rag_reliability.corpus.normalization import write_exact_text
from rag_reliability.corpus.normalized import (
    NormalizedCorpusDocument,
    Phase3bNormalizedCorpusManifest,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)

_PHASE3B_MANIFEST_PATH = Path(
    "datasets/source_manifests/phase3b_normalized_corpus_v1.json"
)

_PHASE3C_MANIFEST_PATH = Path(
    "datasets/source_manifests/"
    "phase3c_background_normalized_corpus_v1.json"
)

_CHUNK_CONFIG_PATH = Path(
    "datasets/chunk_manifests/"
    "phase3d_structural_chunking_config_v1.json"
)

_CHUNK_ROOT = Path(
    "datasets/chunks/phase3d_v1"
)

_CHUNK_MANIFEST_PATH = Path(
    "datasets/chunk_manifests/"
    "phase3d_chunk_manifest_v1.json"
)

_CHUNK_RECEIPT_PATH = Path(
    "artifacts/development/"
    "phase3d_chunking_receipt_v1.json"
)


@dataclass(frozen=True)
class _ChunkCandidate:
    record: CorpusChunkRecord
    content: str


@dataclass
class _ComponentGroup:
    scope: ChunkEvidenceScope
    component_ref: str
    component_value: object
    canonical_value: str
    parents: dict[str, ChunkParentLineage]
    semantic_families: set[SemanticOperationFamily]
    operation_ids: set[str]


def _read_and_hash(
    path: Path,
) -> tuple[bytes, str]:
    content = path.read_bytes()

    return (
        content,
        hashlib.sha256(content).hexdigest(),
    )


def _read_verified_json(
    path: Path,
) -> tuple[bytes, str]:
    content, digest = _read_and_hash(path)

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    parts = (
        sidecar.read_text(
            encoding="utf-8"
        )
        .strip()
        .split()
    )

    if len(parts) != 2:
        raise ValueError(
            f"malformed SHA-256 sidecar: {path.name}"
        )

    if parts[1] != path.name:
        raise ValueError(
            f"SHA-256 sidecar filename mismatch: {path.name}"
        )

    if parts[0] != digest:
        raise ValueError(
            f"SHA-256 sidecar mismatch: {path.name}"
        )

    return content, digest


def _chunk_content_path(
    kind: ChunkKind,
    chunk_id: str,
) -> str:
    if kind is ChunkKind.AUTHORED_SECTION:
        path = (
            _CHUNK_ROOT
            / "authored"
            / f"{chunk_id}.md"
        )

        return path.as_posix()

    if kind is ChunkKind.OPENAPI_OPERATION_CORE:
        path = (
            _CHUNK_ROOT
            / "openapi"
            / "operation_core"
            / f"{chunk_id}.json"
        )

        return path.as_posix()

    path = (
        _CHUNK_ROOT
        / "openapi"
        / "component"
        / f"{chunk_id}.json"
    )

    return path.as_posix()


def _load_inputs(
    repo_root: Path,
) -> tuple[
    tuple[NormalizedCorpusDocument, ...],
    dict[str, str],
]:
    phase3b_bytes, phase3b_sha = _read_verified_json(
        repo_root / _PHASE3B_MANIFEST_PATH
    )

    if (
        phase3b_sha
        != PHASE3B_NORMALIZED_MANIFEST_SHA256
    ):
        raise ValueError(
            "Phase 3B normalized manifest does not match frozen identity"
        )

    phase3c_bytes, phase3c_sha = _read_verified_json(
        repo_root / _PHASE3C_MANIFEST_PATH
    )

    if (
        phase3c_sha
        != PHASE3C_NORMALIZED_MANIFEST_SHA256
    ):
        raise ValueError(
            "Phase 3C normalized manifest does not match frozen identity"
        )

    phase3b = (
        Phase3bNormalizedCorpusManifest.model_validate_json(
            phase3b_bytes
        )
    )

    phase3c = (
        Phase3cBackgroundNormalizedCorpusManifest.model_validate_json(
            phase3c_bytes
        )
    )

    documents = tuple(
        sorted(
            (
                *phase3b.documents,
                *phase3c.documents,
            ),
            key=lambda document: document.document_id,
        )
    )

    if len(documents) != EXPECTED_INPUT_DOCUMENT_COUNT:
        raise ValueError(
            "Phase 3D input document count does not match frozen evidence"
        )

    document_ids = tuple(
        document.document_id
        for document in documents
    )

    if len(document_ids) != len(set(document_ids)):
        raise ValueError(
            "Phase 3D input document IDs must be unique"
        )

    contents: dict[str, str] = {}

    for document in documents:
        path = (
            repo_root
            / Path(document.content_path)
        )

        if not path.is_file():
            raise ValueError(
                f"normalized input file is missing: {document.content_path}"
            )

        raw = path.read_bytes()

        digest = hashlib.sha256(
            raw
        ).hexdigest()

        if (
            digest
            != document.normalized_content_sha256
        ):
            raise ValueError(
                f"normalized input SHA mismatch: {document.document_id}"
            )

        if (
            len(raw)
            != document.normalized_byte_count
        ):
            raise ValueError(
                "normalized input byte-count mismatch: "
                f"{document.document_id}"
            )

        contents[
            document.document_id
        ] = raw.decode("utf-8")

    return documents, contents


def _markdown_candidates(
    document: NormalizedCorpusDocument,
    content: str,
    *,
    config_sha256: str,
) -> tuple[_ChunkCandidate, ...]:
    scope = ChunkEvidenceScope.from_document(
        document
    )

    parent = ChunkParentLineage.from_document(
        document
    )

    fragments = chunk_markdown_structurally(
        content
    )

    candidates: list[_ChunkCandidate] = []

    for index, fragment in enumerate(
        fragments
    ):
        content_sha = sha256_text(
            fragment.text
        )

        chunk_id = build_chunk_id(
            chunk_kind=ChunkKind.AUTHORED_SECTION,
            content_sha256=content_sha,
            chunk_index=index,
            parent_document_ids=(
                document.document_id,
            ),
            evidence_scope=scope,
        )

        record = CorpusChunkRecord(
            chunk_id=chunk_id,
            chunk_kind=ChunkKind.AUTHORED_SECTION,
            content_path=_chunk_content_path(
                ChunkKind.AUTHORED_SECTION,
                chunk_id,
            ),
            content_sha256=content_sha,
            byte_count=utf8_size(
                fragment.text
            ),
            chunking_policy_sha256=(
                config_sha256
            ),
            chunk_index=index,
            parents=(parent,),
            evidence_scope=scope,
            section_headings=(
                fragment.section_headings
            ),
        )

        candidates.append(
            _ChunkCandidate(
                record=record,
                content=fragment.text,
            )
        )

    return tuple(candidates)


def _openapi_payload(
    content: str,
) -> dict[str, object]:
    value = json.loads(content)

    if not isinstance(value, dict):
        raise ValueError(
            "normalized OpenAPI operation must be a JSON object"
        )

    if any(
        not isinstance(key, str)
        for key in value
    ):
        raise ValueError(
            "normalized OpenAPI object keys must be strings"
        )

    return cast(
        dict[str, object],
        value,
    )


def _operation_candidates(
    document: NormalizedCorpusDocument,
    payload: dict[str, object],
    *,
    config_sha256: str,
) -> tuple[_ChunkCandidate, ...]:
    if document.semantic_family is None:
        raise ValueError(
            "OpenAPI document lacks semantic family"
        )

    if document.operation_id is None:
        raise ValueError(
            "OpenAPI document lacks operation ID"
        )

    scope = ChunkEvidenceScope.from_document(
        document
    )

    parent = ChunkParentLineage.from_document(
        document
    )

    core_chunks = split_json_structurally(
        operation_core(payload)
    )

    candidates: list[_ChunkCandidate] = []

    for index, content in enumerate(
        core_chunks
    ):
        content_sha = sha256_text(
            content
        )

        chunk_id = build_chunk_id(
            chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
            content_sha256=content_sha,
            chunk_index=index,
            parent_document_ids=(
                document.document_id,
            ),
            evidence_scope=scope,
        )

        record = CorpusChunkRecord(
            chunk_id=chunk_id,
            chunk_kind=ChunkKind.OPENAPI_OPERATION_CORE,
            content_path=_chunk_content_path(
                ChunkKind.OPENAPI_OPERATION_CORE,
                chunk_id,
            ),
            content_sha256=content_sha,
            byte_count=utf8_size(content),
            chunking_policy_sha256=(
                config_sha256
            ),
            chunk_index=index,
            parents=(parent,),
            evidence_scope=scope,
            semantic_families=(
                document.semantic_family,
            ),
            linked_operation_ids=(
                document.operation_id,
            ),
        )

        candidates.append(
            _ChunkCandidate(
                record=record,
                content=content,
            )
        )

    return tuple(candidates)


def _collect_component_groups(
    documents: tuple[
        NormalizedCorpusDocument,
        ...,
    ],
    contents: dict[str, str],
) -> tuple[
    dict[str, _ComponentGroup],
    int,
]:
    groups: dict[
        str,
        _ComponentGroup,
    ] = {}

    occurrence_count = 0

    for document in documents:
        if (
            document.document_kind
            != "openapi_operation_contract"
        ):
            continue

        if document.semantic_family is None:
            raise ValueError(
                "OpenAPI document lacks semantic family"
            )

        if document.operation_id is None:
            raise ValueError(
                "OpenAPI document lacks operation ID"
            )

        payload = _openapi_payload(
            contents[document.document_id]
        )

        scope = ChunkEvidenceScope.from_document(
            document
        )

        parent = ChunkParentLineage.from_document(
            document
        )

        for component_ref, component_value in (
            referenced_components(payload)
        ):
            occurrence_count += 1

            key = component_dedup_key(
                scope,
                component_ref,
                component_value,
            )

            canonical_value = (
                canonical_json_text(
                    component_value
                )
            )

            group = groups.get(key)

            if group is None:
                groups[key] = _ComponentGroup(
                    scope=scope,
                    component_ref=component_ref,
                    component_value=component_value,
                    canonical_value=canonical_value,
                    parents={
                        document.document_id: parent,
                    },
                    semantic_families={
                        document.semantic_family,
                    },
                    operation_ids={
                        document.operation_id,
                    },
                )

                continue

            if group.scope != scope:
                raise ValueError(
                    "component deduplication scope collision"
                )

            if (
                group.component_ref
                != component_ref
            ):
                raise ValueError(
                    "component reference collision"
                )

            if (
                group.canonical_value
                != canonical_value
            ):
                raise ValueError(
                    "component content collision"
                )

            existing_parent = (
                group.parents.get(
                    document.document_id
                )
            )

            if (
                existing_parent is not None
                and existing_parent != parent
            ):
                raise ValueError(
                    "component parent-lineage collision"
                )

            group.parents[
                document.document_id
            ] = parent

            group.semantic_families.add(
                document.semantic_family
            )

            group.operation_ids.add(
                document.operation_id
            )

    return groups, occurrence_count


def _component_candidates(
    groups: dict[str, _ComponentGroup],
    *,
    config_sha256: str,
) -> tuple[_ChunkCandidate, ...]:
    candidates: list[
        _ChunkCandidate
    ] = []

    for key in sorted(groups):
        group = groups[key]

        parents = tuple(
            group.parents[
                document_id
            ]
            for document_id in sorted(
                group.parents
            )
        )

        parent_document_ids = tuple(
            parent.document_id
            for parent in parents
        )

        semantic_families = tuple(
            sorted(
                group.semantic_families
            )
        )

        operation_ids = tuple(
            sorted(
                group.operation_ids
            )
        )

        payload = {
            "reference": (
                group.component_ref
            ),
            "value": (
                group.component_value
            ),
        }

        chunks = split_json_structurally(
            payload
        )

        for index, content in enumerate(
            chunks
        ):
            content_sha = sha256_text(
                content
            )

            chunk_id = build_chunk_id(
                chunk_kind=ChunkKind.OPENAPI_COMPONENT,
                content_sha256=content_sha,
                chunk_index=index,
                parent_document_ids=(
                    parent_document_ids
                ),
                evidence_scope=group.scope,
                component_ref=(
                    group.component_ref
                ),
            )

            record = CorpusChunkRecord(
                chunk_id=chunk_id,
                chunk_kind=ChunkKind.OPENAPI_COMPONENT,
                content_path=_chunk_content_path(
                    ChunkKind.OPENAPI_COMPONENT,
                    chunk_id,
                ),
                content_sha256=content_sha,
                byte_count=utf8_size(
                    content
                ),
                chunking_policy_sha256=(
                    config_sha256
                ),
                chunk_index=index,
                parents=parents,
                evidence_scope=(
                    group.scope
                ),
                semantic_families=(
                    semantic_families
                ),
                linked_operation_ids=(
                    operation_ids
                ),
                component_ref=(
                    group.component_ref
                ),
            )

            candidates.append(
                _ChunkCandidate(
                    record=record,
                    content=content,
                )
            )

    return tuple(candidates)


def _materialize_candidates(
    repo_root: Path,
    candidates: tuple[
        _ChunkCandidate,
        ...,
    ],
) -> int:
    match_count = 0

    for candidate in candidates:
        path = (
            repo_root
            / Path(
                candidate.record.content_path
            )
        )

        digest, byte_count = (
            write_exact_text(
                path,
                candidate.content,
            )
        )

        if (
            digest
            != candidate.record.content_sha256
        ):
            raise ValueError(
                "materialized chunk SHA mismatch: "
                f"{candidate.record.chunk_id}"
            )

        if (
            byte_count
            != candidate.record.byte_count
        ):
            raise ValueError(
                "materialized chunk byte-count mismatch: "
                f"{candidate.record.chunk_id}"
            )

        match_count += 1

    expected_paths = {
        (
            repo_root
            / Path(
                candidate.record.content_path
            )
        ).resolve()
        for candidate in candidates
    }

    chunk_root = (
        repo_root
        / _CHUNK_ROOT
    )

    observed_paths = {
        path.resolve()
        for path in chunk_root.rglob("*")
        if path.is_file()
    }

    if observed_paths != expected_paths:
        raise ValueError(
            "materialized Phase 3D chunk file set "
            "does not exactly match expected manifest paths"
        )

    return match_count


def main() -> None:
    repo_root = Path.cwd()

    documents, contents = _load_inputs(
        repo_root
    )

    config = Phase3dChunkingConfig()

    config_sha = write_json_with_sha256(
        repo_root / _CHUNK_CONFIG_PATH,
        config,
    )

    candidates: list[
        _ChunkCandidate
    ] = []

    for document in documents:
        content = contents[
            document.document_id
        ]

        if (
            document.document_kind
            == "authored_guidance"
        ):
            candidates.extend(
                _markdown_candidates(
                    document,
                    content,
                    config_sha256=(
                        config_sha
                    ),
                )
            )

            continue

        payload = _openapi_payload(
            content
        )

        candidates.extend(
            _operation_candidates(
                document,
                payload,
                config_sha256=(
                    config_sha
                ),
            )
        )

    groups, component_occurrences = (
        _collect_component_groups(
            documents,
            contents,
        )
    )

    candidates.extend(
        _component_candidates(
            groups,
            config_sha256=config_sha,
        )
    )

    ordered_candidates = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                candidate.record.chunk_id
            ),
        )
    )

    records = tuple(
        candidate.record
        for candidate in ordered_candidates
    )

    chunk_ids = tuple(
        record.chunk_id
        for record in records
    )

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError(
            "Phase 3D candidate chunk IDs are not unique"
        )

    if (
        component_occurrences
        != EXPECTED_COMPONENT_OCCURRENCE_COUNT
    ):
        raise ValueError(
            "component occurrence count drifted from dry-run evidence"
        )

    if (
        len(groups)
        != EXPECTED_UNIQUE_SCOPED_COMPONENT_COUNT
    ):
        raise ValueError(
            "unique scoped component count drifted "
            "from dry-run evidence"
        )

    duplicate_occurrences = (
        component_occurrences
        - len(groups)
    )

    if (
        duplicate_occurrences
        != EXPECTED_DUPLICATE_COMPONENT_OCCURRENCE_COUNT
    ):
        raise ValueError(
            "duplicate component occurrence count drifted "
            "from dry-run evidence"
        )

    manifest = Phase3dChunkManifest(
        chunking_config_sha256=(
            config_sha
        ),
        chunks=records,
    )

    if (
        manifest.markdown_chunk_count
        != EXPECTED_MARKDOWN_CHUNK_COUNT
    ):
        raise ValueError(
            "Markdown chunk count drifted"
        )

    if (
        manifest.operation_core_chunk_count
        != EXPECTED_OPERATION_CORE_CHUNK_COUNT
    ):
        raise ValueError(
            "operation-core chunk count drifted"
        )

    if (
        manifest.component_chunk_count
        != EXPECTED_COMPONENT_CHUNK_COUNT
    ):
        raise ValueError(
            "component chunk count drifted"
        )

    if (
        manifest.total_chunk_count
        != EXPECTED_TOTAL_CHUNK_COUNT
    ):
        raise ValueError(
            "total chunk count drifted"
        )

    chunk_file_match_count = (
        _materialize_candidates(
            repo_root,
            ordered_candidates,
        )
    )

    if (
        chunk_file_match_count
        != EXPECTED_TOTAL_CHUNK_COUNT
    ):
        raise ValueError(
            "chunk file identity-match count drifted"
        )

    manifest_sha = (
        write_json_with_sha256(
            repo_root
            / _CHUNK_MANIFEST_PATH,
            manifest,
        )
    )

    receipt = Phase3dChunkingReceipt(
        chunking_config_sha256=(
            config_sha
        ),
        chunk_manifest_sha256=(
            manifest_sha
        ),
    )

    receipt_sha = (
        write_json_with_sha256(
            repo_root
            / _CHUNK_RECEIPT_PATH,
            receipt,
        )
    )

    print(
        f"PHASE3D_CHUNKING_CONFIG_SHA256={config_sha}"
    )
    print(
        "PHASE3D_INPUT_DOCUMENT_COUNT="
        f"{len(documents)}"
    )
    print(
        "PHASE3D_INPUT_FILE_IDENTITY_MATCH_COUNT="
        f"{len(contents)}"
    )
    print(
        "PHASE3D_MARKDOWN_CHUNK_COUNT="
        f"{manifest.markdown_chunk_count}"
    )
    print(
        "PHASE3D_OPERATION_CORE_CHUNK_COUNT="
        f"{manifest.operation_core_chunk_count}"
    )
    print(
        "PHASE3D_COMPONENT_OCCURRENCE_COUNT="
        f"{component_occurrences}"
    )
    print(
        "PHASE3D_UNIQUE_SCOPED_COMPONENT_COUNT="
        f"{len(groups)}"
    )
    print(
        "PHASE3D_DUPLICATE_COMPONENT_OCCURRENCE_COUNT="
        f"{duplicate_occurrences}"
    )
    print(
        "PHASE3D_COMPONENT_CHUNK_COUNT="
        f"{manifest.component_chunk_count}"
    )
    print(
        "PHASE3D_TOTAL_CHUNK_COUNT="
        f"{manifest.total_chunk_count}"
    )
    print(
        "PHASE3D_CHUNK_FILE_IDENTITY_MATCH_COUNT="
        f"{chunk_file_match_count}"
    )
    print(
        f"PHASE3D_CHUNK_MANIFEST_SHA256={manifest_sha}"
    )
    print(
        f"PHASE3D_CHUNKING_RECEIPT_SHA256={receipt_sha}"
    )
    print(
        "PHASE3D_CHUNKING_STATUS="
        f"{manifest.chunking_status}"
    )
    print(
        "PHASE3D_CHUNKED_CORPUS_READY="
        f"{str(manifest.chunked_corpus_ready).lower()}"
    )
    print(
        "PHASE3D_BASELINE_AUTHORIZED="
        f"{str(manifest.baseline_authorized).lower()}"
    )
    print(
        "PHASE3D_RELEASE_ELIGIBLE="
        f"{str(manifest.release_eligible).lower()}"
    )


if __name__ == "__main__":
    main()