"""Phase 3D structural chunking contracts and deterministic primitives."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.models import SemanticOperationFamily
from rag_reliability.corpus.normalized import NormalizedCorpusDocument

CHUNK_BYTE_BUDGET: Literal[8192] = 8192
CHUNK_OVERLAP_BYTES: Literal[0] = 0

PHASE3B_NORMALIZED_MANIFEST_SHA256: Literal[
    "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
] = "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"

PHASE3C_NORMALIZED_MANIFEST_SHA256: Literal[
    "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"
] = "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"

_COMPONENT_DEDUP_SCOPE_FIELDS = (
    "source_family",
    "source_state",
    "authority_level",
    "data_role",
    "product_scope",
    "api_version_or_snapshot",
    "source_commit_sha_or_version",
    "source_license",
    "source_url",
    "component_ref",
    "component_content_sha256",
)

_EXPECTED_OPENAPI_KEYS = frozenset(
    {
        "method",
        "operation",
        "path",
        "path_parameters",
        "referenced_components",
    }
)

_HEADING_RE = re.compile(r"^#{1,6}[ \t]+")
_FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


class ChunkKind(StrEnum):
    """Frozen V1 semantic chunk kinds."""

    AUTHORED_SECTION = "authored_section"
    OPENAPI_OPERATION_CORE = "openapi_operation_core"
    OPENAPI_COMPONENT = "openapi_component"


class ChunkEvidenceScope(ContractModel):
    """Shared evidence identity that must survive chunking."""

    source_family: CorpusSourceFamily
    source_state: SourceState
    authority_level: AuthorityLevel
    data_role: DataRole
    product_scope: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr
    source_commit_sha_or_version: NonEmptyStr
    source_license: NonEmptyStr
    source_url: NonEmptyStr

    @classmethod
    def from_document(
        cls,
        document: NormalizedCorpusDocument,
    ) -> Self:
        provenance = document.provenance

        return cls(
            source_family=provenance.source_family,
            source_state=provenance.source_state,
            authority_level=provenance.authority_level,
            data_role=provenance.data_role,
            product_scope=provenance.product_scope,
            api_version_or_snapshot=provenance.api_version_or_snapshot,
            source_commit_sha_or_version=(
                provenance.source_commit_sha_or_version
            ),
            source_license=provenance.source_license,
            source_url=str(provenance.source_url),
        )


class ChunkParentLineage(ContractModel):
    """One normalized parent bound atomically to its source identity."""

    document_id: NonEmptyStr
    normalized_content_sha256: Sha256
    source_id: NonEmptyStr

    @classmethod
    def from_document(
        cls,
        document: NormalizedCorpusDocument,
    ) -> Self:
        return cls(
            document_id=document.document_id,
            normalized_content_sha256=(
                document.normalized_content_sha256
            ),
            source_id=document.provenance.source_id,
        )


class Phase3dChunkingConfig(ContractModel):
    """Candidate V1 structural chunking configuration."""

    config_version: Literal[
        "phase3d-structural-chunking-config-v1"
    ] = "phase3d-structural-chunking-config-v1"

    phase3b_normalized_manifest_sha256: Literal[
        "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
    ] = PHASE3B_NORMALIZED_MANIFEST_SHA256

    phase3c_normalized_manifest_sha256: Literal[
        "81abcd940f8bb72b38955d44f1a5d9544311c1790110052642b677bf54d88706"
    ] = PHASE3C_NORMALIZED_MANIFEST_SHA256

    byte_budget: Literal[8192] = CHUNK_BYTE_BUDGET
    overlap_bytes: Literal[0] = CHUNK_OVERLAP_BYTES

    authored_strategy: Literal[
        "heading_then_markdown_block"
    ] = "heading_then_markdown_block"

    openapi_core_strategy: Literal[
        "structural_json"
    ] = "structural_json"

    component_strategy: Literal[
        "scope_deduplicated_structural_json"
    ] = "scope_deduplicated_structural_json"

    oversized_scalar_policy: Literal[
        "fail_closed"
    ] = "fail_closed"

    component_dedup_scope_fields: tuple[NonEmptyStr, ...] = (
        _COMPONENT_DEDUP_SCOPE_FIELDS
    )

    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_frozen_candidate(self) -> Self:
        if (
            self.component_dedup_scope_fields
            != _COMPONENT_DEDUP_SCOPE_FIELDS
        ):
            raise ValueError(
                "component deduplication scope does not match "
                "the Phase 3D candidate policy"
            )

        return self


class CorpusChunkRecord(ContractModel):
    """File-backed retrieval chunk with complete evidence lineage."""

    chunk_id: NonEmptyStr
    chunk_kind: ChunkKind
    content_path: NonEmptyStr
    content_sha256: Sha256
    byte_count: int = Field(gt=0, le=CHUNK_BYTE_BUDGET)

    chunking_policy_sha256: Sha256
    chunk_index: int = Field(ge=0)

    parents: tuple[ChunkParentLineage, ...] = Field(
        min_length=1
    )

    evidence_scope: ChunkEvidenceScope

    semantic_families: tuple[
        SemanticOperationFamily,
        ...,
    ] = ()

    linked_operation_ids: tuple[NonEmptyStr, ...] = ()

    component_ref: NonEmptyStr | None = None
    section_headings: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_chunk_semantics(self) -> Self:
        lineage_count = len(self.parents)

        parent_document_ids = tuple(
            parent.document_id
            for parent in self.parents
        )

        if parent_document_ids != tuple(
            sorted(parent_document_ids)
        ):
            raise ValueError(
                "parent lineage must be deterministically document-ID sorted"
            )

        if len(set(parent_document_ids)) != lineage_count:
            raise ValueError(
                "parent lineage document IDs must be unique"
            )

        if self.semantic_families != tuple(
            sorted(set(self.semantic_families))
        ):
            raise ValueError(
                "semantic families must be sorted and unique"
            )

        if self.linked_operation_ids != tuple(
            sorted(set(self.linked_operation_ids))
        ):
            raise ValueError(
                "linked operation IDs must be sorted and unique"
            )

        if self.chunk_kind is ChunkKind.AUTHORED_SECTION:
            if self.component_ref is not None:
                raise ValueError(
                    "authored chunks cannot carry a component reference"
                )

            if self.semantic_families:
                raise ValueError(
                    "authored chunks cannot carry semantic operation families"
                )

            if self.linked_operation_ids:
                raise ValueError(
                    "authored chunks cannot carry linked operation IDs"
                )

            return self

        if self.section_headings:
            raise ValueError(
                "OpenAPI chunks cannot carry Markdown section headings"
            )

        if self.chunk_kind is ChunkKind.OPENAPI_OPERATION_CORE:
            if lineage_count != 1:
                raise ValueError(
                    "operation-core chunks require exactly one parent document"
                )

            if self.component_ref is not None:
                raise ValueError(
                    "operation-core chunks cannot carry a component reference"
                )

            if len(self.semantic_families) != 1:
                raise ValueError(
                    "operation-core chunks require exactly one semantic family"
                )

            if len(self.linked_operation_ids) != 1:
                raise ValueError(
                    "operation-core chunks require exactly one operation ID"
                )

            return self

        if self.component_ref is None:
            raise ValueError(
                "OpenAPI component chunks require a component reference"
            )

        if not self.semantic_families:
            raise ValueError(
                "OpenAPI component chunks require semantic family lineage"
            )

        if not self.linked_operation_ids:
            raise ValueError(
                "OpenAPI component chunks require operation lineage"
            )

        return self


class StructuralChunkingError(ValueError):
    """Raised when a source cannot be split without violating structure."""


@dataclass(frozen=True)
class StructuralJsonFragment:
    """One maximal JSON subtree that fits the configured byte budget."""

    path: tuple[str | int, ...]
    value: object


@dataclass(frozen=True)
class MarkdownChunkFragment:
    """One exact Markdown fragment plus heading metadata."""

    text: str
    section_headings: tuple[str, ...]


def utf8_size(text: str) -> int:
    """Return exact UTF-8 byte size."""

    return len(text.encode("utf-8"))


def canonical_json_text(value: object) -> str:
    """Serialize JSON deterministically for hashing and chunk material."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(text: str) -> str:
    """Return lowercase SHA-256 for exact UTF-8 text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def operation_core(
    payload: dict[str, object],
) -> dict[str, object]:
    """Extract the frozen OpenAPI operation-core surface."""

    observed_keys = frozenset(payload)

    if observed_keys != _EXPECTED_OPENAPI_KEYS:
        raise StructuralChunkingError(
            "OpenAPI normalized document shape does not match "
            "the frozen five-field Phase 3D input contract"
        )

    return {
        "method": payload["method"],
        "operation": payload["operation"],
        "path": payload["path"],
        "path_parameters": payload["path_parameters"],
    }


def referenced_components(
    payload: dict[str, object],
) -> tuple[tuple[str, object], ...]:
    """Return referenced components in deterministic reference order."""

    observed_keys = frozenset(payload)

    if observed_keys != _EXPECTED_OPENAPI_KEYS:
        raise StructuralChunkingError(
            "OpenAPI normalized document shape does not match "
            "the frozen five-field Phase 3D input contract"
        )

    raw_components = payload["referenced_components"]

    if not isinstance(raw_components, dict):
        raise StructuralChunkingError(
            "referenced_components must be a JSON object"
        )

    components = cast(dict[object, object], raw_components)

    if any(not isinstance(key, str) for key in components):
        raise StructuralChunkingError(
            "referenced component keys must be strings"
        )

    typed_components = cast(dict[str, object], raw_components)

    return tuple(
        (reference, typed_components[reference])
        for reference in sorted(typed_components)
    )


def component_content_sha256(value: object) -> str:
    """Hash one canonical referenced-component value."""

    return sha256_text(canonical_json_text(value))


def component_dedup_key(
    scope: ChunkEvidenceScope,
    component_ref: str,
    component_value: object,
) -> str:
    """Build the scoped identity used for component deduplication."""

    payload = {
        "scope": scope.model_dump(mode="json"),
        "component_ref": component_ref,
        "component_content_sha256": (
            component_content_sha256(component_value)
        ),
    }

    return hashlib.sha256(
        canonical_json_text(payload).encode("utf-8")
    ).hexdigest()


def build_chunk_id(
    *,
    chunk_kind: ChunkKind,
    content_sha256: str,
    chunk_index: int,
    parent_document_ids: tuple[str, ...],
    evidence_scope: ChunkEvidenceScope,
    component_ref: str | None = None,
) -> str:
    """Build one deterministic chunk identity."""

    payload = {
        "chunk_kind": chunk_kind.value,
        "content_sha256": content_sha256,
        "chunk_index": chunk_index,
        "parent_document_ids": list(parent_document_ids),
        "evidence_scope": evidence_scope.model_dump(mode="json"),
        "component_ref": component_ref,
    }

    digest = hashlib.sha256(
        canonical_json_text(payload).encode("utf-8")
    ).hexdigest()

    return f"chunk-{digest}"


def _fragment_payload(
    fragment: StructuralJsonFragment,
) -> dict[str, object]:
    return {
        "path": list(fragment.path),
        "value": fragment.value,
    }


def render_structural_json_group(
    fragments: tuple[StructuralJsonFragment, ...],
) -> str:
    """Render one independently valid structural JSON retrieval chunk."""

    return canonical_json_text(
        {
            "fragments": [
                _fragment_payload(fragment)
                for fragment in fragments
            ]
        }
    )


def _collect_structural_fragments(
    value: object,
    *,
    path: tuple[str | int, ...],
    budget: int,
) -> tuple[StructuralJsonFragment, ...]:
    fragment = StructuralJsonFragment(
        path=path,
        value=value,
    )

    single = render_structural_json_group((fragment,))

    if utf8_size(single) <= budget:
        return (fragment,)

    if isinstance(value, dict):
        if not value:
            raise StructuralChunkingError(
                "empty JSON object unexpectedly exceeds chunk budget"
            )

        if any(not isinstance(key, str) for key in value):
            raise StructuralChunkingError(
                "JSON object keys must be strings"
            )

        typed_value = cast(dict[str, object], value)

        fragments: list[StructuralJsonFragment] = []

        for key in sorted(typed_value):
            fragments.extend(
                _collect_structural_fragments(
                    typed_value[key],
                    path=(*path, key),
                    budget=budget,
                )
            )

        return tuple(fragments)

    if isinstance(value, list):
        if not value:
            raise StructuralChunkingError(
                "empty JSON array unexpectedly exceeds chunk budget"
            )

        fragments = []

        for index, item in enumerate(value):
            fragments.extend(
                _collect_structural_fragments(
                    item,
                    path=(*path, index),
                    budget=budget,
                )
            )

        return tuple(fragments)

    raise StructuralChunkingError(
        "JSON scalar exceeds structural chunk budget and "
        "cannot be split without slicing scalar content"
    )


def split_json_structurally(
    value: object,
    *,
    budget: int = CHUNK_BYTE_BUDGET,
) -> tuple[str, ...]:
    """Split JSON only at object/list structural boundaries."""

    if budget <= 0:
        raise ValueError("chunk budget must be positive")

    atomic = _collect_structural_fragments(
        value,
        path=(),
        budget=budget,
    )

    chunks: list[str] = []
    current: list[StructuralJsonFragment] = []

    for fragment in atomic:
        candidate = tuple([*current, fragment])
        rendered = render_structural_json_group(candidate)

        if utf8_size(rendered) <= budget:
            current.append(fragment)
            continue

        if not current:
            raise StructuralChunkingError(
                "single structural JSON fragment exceeds chunk budget"
            )

        chunks.append(
            render_structural_json_group(tuple(current))
        )
        current = [fragment]

    if current:
        chunks.append(
            render_structural_json_group(tuple(current))
        )

    if any(utf8_size(chunk) > budget for chunk in chunks):
        raise StructuralChunkingError(
            "structural JSON splitter emitted an oversized chunk"
        )

    return tuple(chunks)


def _section_heading(section: str) -> str | None:
    first_line = section.splitlines()[0]

    if not _HEADING_RE.match(first_line):
        return None

    return first_line.lstrip("#").strip()


def split_markdown_sections(
    text: str,
) -> tuple[str, ...]:
    """Split Markdown at heading starts while preserving exact bytes."""

    if not text:
        raise StructuralChunkingError(
            "cannot chunk an empty Markdown document"
        )

    lines = text.splitlines(keepends=True)

    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        if _HEADING_RE.match(line) and current:
            sections.append("".join(current))
            current = []

        current.append(line)

    if current:
        sections.append("".join(current))

    return tuple(sections)


def _split_markdown_blocks(
    section: str,
) -> tuple[str, ...]:
    """Split one Markdown section at blank lines outside fenced code."""

    lines = section.splitlines(keepends=True)

    blocks: list[str] = []
    current: list[str] = []

    fence_character: str | None = None
    fence_length = 0

    for line in lines:
        marker_match = _FENCE_RE.match(line)

        if marker_match:
            marker = marker_match.group(1)

            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif (
                marker[0] == fence_character
                and len(marker) >= fence_length
            ):
                fence_character = None
                fence_length = 0

        current.append(line)

        if fence_character is None and not line.strip():
            blocks.append("".join(current))
            current = []

    if current:
        blocks.append("".join(current))

    return tuple(blocks)


def _pack_markdown_units(
    units: tuple[str, ...],
    *,
    budget: int,
    section_headings: tuple[str, ...],
) -> tuple[MarkdownChunkFragment, ...]:
    chunks: list[MarkdownChunkFragment] = []
    current = ""

    for unit in units:
        if utf8_size(unit) > budget:
            raise StructuralChunkingError(
                "Markdown atomic block exceeds structural chunk budget"
            )

        candidate = current + unit

        if current and utf8_size(candidate) > budget:
            chunks.append(
                MarkdownChunkFragment(
                    text=current,
                    section_headings=section_headings,
                )
            )
            current = unit
            continue

        current = candidate

    if current:
        chunks.append(
            MarkdownChunkFragment(
                text=current,
                section_headings=section_headings,
            )
        )

    return tuple(chunks)


def chunk_markdown_structurally(
    text: str,
    *,
    budget: int = CHUNK_BYTE_BUDGET,
) -> tuple[MarkdownChunkFragment, ...]:
    """Chunk Markdown by headings, then blocks, with zero overlap."""

    if budget <= 0:
        raise ValueError("chunk budget must be positive")

    sections = split_markdown_sections(text)

    chunks: list[MarkdownChunkFragment] = []

    pending_text = ""
    pending_headings: list[str] = []

    for section in sections:
        heading = _section_heading(section)
        section_size = utf8_size(section)

        if section_size <= budget:
            candidate = pending_text + section

            if pending_text and utf8_size(candidate) > budget:
                chunks.append(
                    MarkdownChunkFragment(
                        text=pending_text,
                        section_headings=tuple(
                            pending_headings
                        ),
                    )
                )
                pending_text = ""
                pending_headings = []

            pending_text += section

            if heading is not None:
                pending_headings.append(heading)

            continue

        if pending_text:
            chunks.append(
                MarkdownChunkFragment(
                    text=pending_text,
                    section_headings=tuple(
                        pending_headings
                    ),
                )
            )
            pending_text = ""
            pending_headings = []

        section_headings = (
            (heading,)
            if heading is not None
            else ()
        )

        blocks = _split_markdown_blocks(section)

        chunks.extend(
            _pack_markdown_units(
                blocks,
                budget=budget,
                section_headings=section_headings,
            )
        )

    if pending_text:
        chunks.append(
            MarkdownChunkFragment(
                text=pending_text,
                section_headings=tuple(
                    pending_headings
                ),
            )
        )

    if "".join(chunk.text for chunk in chunks) != text:
        raise StructuralChunkingError(
            "Markdown structural chunking did not preserve exact source text"
        )

    if any(utf8_size(chunk.text) > budget for chunk in chunks):
        raise StructuralChunkingError(
            "Markdown splitter emitted an oversized chunk"
        )

    return tuple(chunks)