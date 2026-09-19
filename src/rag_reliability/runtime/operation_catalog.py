"""Build the runtime-safe operation catalog from the frozen Phase 3D corpus."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from rag_reliability.contracts.enums import AuthorityLevel, DataRole, SourceState
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.chunking import ChunkKind, CorpusChunkRecord
from rag_reliability.corpus.models import HttpMethod
from rag_reliability.runtime.operation_resolution import RuntimeOperationDescriptor

_CHUNK_MANIFEST_PATH = (
    Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
)

_CHUNK_MANIFEST_SHA256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_manifest(repo_root: Path) -> Phase3dChunkManifest:
    path = repo_root / _CHUNK_MANIFEST_PATH
    content = path.read_bytes()

    if _sha256_bytes(content) != _CHUNK_MANIFEST_SHA256:
        raise ValueError("Phase 3D chunk manifest hash mismatch")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{_CHUNK_MANIFEST_SHA256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError("Phase 3D chunk manifest sidecar mismatch")

    return Phase3dChunkManifest.model_validate_json(content)


def _read_verified_chunk(repo_root: Path, chunk: CorpusChunkRecord) -> object:
    path = repo_root / Path(chunk.content_path)
    content = path.read_bytes()

    if _sha256_bytes(content) != chunk.content_sha256:
        raise ValueError(f"operation chunk hash mismatch: {chunk.chunk_id}")

    return cast(object, json.loads(content))


def _as_mapping(value: object, *, label: str) -> Mapping[object, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return cast(Mapping[object, object], value)


def _fragment_value(payload: object, target: tuple[str, ...]) -> object | None:
    document = _as_mapping(payload, label="operation chunk payload")
    raw_fragments = document.get("fragments")

    if not isinstance(raw_fragments, list):
        raise ValueError("operation chunk payload requires fragments")

    fragments = cast(list[object], raw_fragments)

    for raw_fragment in fragments:
        fragment = _as_mapping(raw_fragment, label="operation chunk fragment")
        raw_path = fragment.get("path")

        if not isinstance(raw_path, list):
            raise ValueError("operation chunk fragment path must be a list")

        path_items = cast(list[object], raw_path)
        if any(not isinstance(item, str) for item in path_items):
            continue

        fragment_path = tuple(cast(list[str], raw_path))
        if len(fragment_path) > len(target):
            continue

        if target[: len(fragment_path)] != fragment_path:
            continue

        value = fragment.get("value")
        remainder = target[len(fragment_path) :]

        for key in remainder:
            if not isinstance(value, dict):
                value = None
                break

            mapping = cast(Mapping[object, object], value)
            if key not in mapping:
                value = None
                break

            value = mapping[key]

        if value is not None:
            return value

    return None


def _is_runtime_operation_chunk(chunk: CorpusChunkRecord) -> bool:
    scope = chunk.evidence_scope
    return (
        chunk.chunk_kind is ChunkKind.OPENAPI_OPERATION_CORE
        and scope.source_state is SourceState.CURRENT
        and scope.authority_level is AuthorityLevel.AUTHORITATIVE
        and scope.data_role is DataRole.CORPUS_SOURCE
    )


def _strings_for_target(
    payloads: tuple[object, ...],
    target: tuple[str, ...],
    label: str,
) -> tuple[str, ...]:
    values: set[str] = set()

    for payload in payloads:
        value = _fragment_value(payload, target)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"operation chunk {label} has invalid shape")
        values.add(value.strip())

    return tuple(sorted(values))


def _required_group_string(
    payloads: tuple[object, ...],
    target: tuple[str, ...],
    label: str,
) -> str:
    values = _strings_for_target(payloads, target, label)
    if len(values) != 1:
        raise ValueError(f"operation chunk group requires exactly one {label}")
    return values[0]


def _optional_group_string(
    payloads: tuple[object, ...],
    target: tuple[str, ...],
    label: str,
) -> str | None:
    values = _strings_for_target(payloads, target, label)
    if len(values) > 1:
        raise ValueError(f"operation chunk group contains conflicting {label}")
    return values[0] if values else None


def _descriptor_from_chunks(
    repo_root: Path,
    chunks: tuple[CorpusChunkRecord, ...],
) -> RuntimeOperationDescriptor:
    if not chunks:
        raise ValueError("operation descriptor requires at least one chunk")

    if any(not _is_runtime_operation_chunk(chunk) for chunk in chunks):
        raise ValueError("chunk group is outside the runtime operation-catalog boundary")

    operation_ids = {
        operation_id
        for chunk in chunks
        for operation_id in chunk.linked_operation_ids
    }
    if len(operation_ids) != 1:
        raise ValueError("operation chunk group must bind exactly one operation ID")

    families = {
        family
        for chunk in chunks
        for family in chunk.semantic_families
    }
    if len(families) != 1:
        raise ValueError("operation chunk group must bind exactly one semantic family")

    payloads = tuple(_read_verified_chunk(repo_root, chunk) for chunk in chunks)
    manifest_operation_id = next(iter(operation_ids))
    content_operation_id = _required_group_string(
        payloads,
        ("operation", "operationId"),
        "operationId",
    )

    if content_operation_id != manifest_operation_id:
        raise ValueError("operation content disagrees with manifest operation ID")

    method = cast(
        HttpMethod,
        _required_group_string(payloads, ("method",), "method"),
    )

    return RuntimeOperationDescriptor(
        operation_id=manifest_operation_id,
        method=method,
        path=_required_group_string(payloads, ("path",), "path"),
        semantic_family=next(iter(families)),
        summary=_optional_group_string(
            payloads,
            ("operation", "summary"),
            "summary",
        ),
    )


def load_runtime_operation_catalog(
    repo_root: Path,
) -> tuple[RuntimeOperationDescriptor, ...]:
    """Load only current authoritative operation-core structure from Phase 3D."""

    manifest = _verified_manifest(repo_root)
    grouped: dict[str, list[CorpusChunkRecord]] = defaultdict(list)

    for chunk in manifest.chunks:
        if not _is_runtime_operation_chunk(chunk):
            continue

        if len(chunk.linked_operation_ids) != 1:
            raise ValueError("operation-core chunk must carry exactly one operation ID")

        grouped[chunk.linked_operation_ids[0]].append(chunk)

    descriptors = tuple(
        _descriptor_from_chunks(
            repo_root,
            tuple(sorted(chunks, key=lambda chunk: chunk.chunk_index)),
        )
        for _operation_id, chunks in sorted(grouped.items())
    )

    operation_ids = tuple(item.operation_id for item in descriptors)

    if not descriptors:
        raise ValueError("runtime operation catalog is empty")

    if len(operation_ids) != len(set(operation_ids)):
        raise ValueError("runtime operation catalog contains duplicate operation IDs")

    return descriptors
