"""Freeze exact rendered authored bytes before Phase 3B normalization."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.acquisition import git_blob_sha1
from rag_reliability.corpus.authored_renderer import (
    ConstrainedAuthoredRenderer,
    Phase3bAuthoredRenderCandidate,
    RenderContractError,
    RenderErrorCode,
    build_frozen_data_reference_map,
    count_active_unresolved_directives,
)
from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_dependency_freeze import Phase3bFrozenRenderDependencySet
from rag_reliability.corpus.render_policy import Phase3bRenderPolicyFreeze

_AUTHORED_RENDER_CANDIDATE_SHA256: Literal[
    "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"
] = "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"

_RENDER_ROOT = Path("datasets/source_documents/rendered/phase3b_authored_v1")
_MANIFEST_PATH = Path("datasets/source_manifests/phase3b_rendered_source_freeze_v1.json")


class RenderedSourceRecord(ContractModel):
    """Identity of one exact rendered authored document."""

    source_id: NonEmptyStr
    source_path: NonEmptyStr
    rendered_path: NonEmptyStr
    source_content_sha256: Sha256
    rendered_content_sha256: Sha256
    rendered_byte_count: int = Field(gt=0)
    active_unresolved_directive_count: Literal[0] = 0


class Phase3bRenderedSourceFreeze(ContractModel):
    """Durable rendered-source boundary consumed by normalization."""

    freeze_version: Literal["phase3b-rendered-source-freeze-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_authored_render_candidate_sha256: Literal[
        "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"
    ]
    document_count: Literal[10] = 10
    identity_match_count: Literal[10] = 10
    unresolved_document_count: Literal[0] = 0
    documents: tuple[RenderedSourceRecord, ...] = Field(min_length=10, max_length=10)
    freeze_status: Literal["frozen"] = "frozen"
    normalization_authorized: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_documents(self) -> Phase3bRenderedSourceFreeze:
        ids = tuple(item.source_id for item in self.documents)
        if len(ids) != len(set(ids)):
            raise ValueError("rendered source freeze contains duplicate source IDs")
        if ids != tuple(sorted(ids)):
            raise ValueError("rendered source freeze documents must be source-ID sorted")
        paths = tuple(item.rendered_path for item in self.documents)
        if len(paths) != len(set(paths)):
            raise ValueError("rendered source freeze contains duplicate rendered paths")
        return self


class Phase3bRenderedSourceFreezeReceipt(ContractModel):
    """Small custody receipt for the rendered-source freeze."""

    receipt_version: Literal["phase3b-rendered-source-freeze-receipt-v1"]
    source_authored_render_candidate_sha256: Literal[
        "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"
    ]
    rendered_source_manifest_sha256: Sha256
    document_count: Literal[10] = 10
    identity_match_count: Literal[10] = 10
    freeze_status: Literal["frozen"] = "frozen"
    normalization_authorized: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False


def rendered_source_manifest_path(repo_root: Path) -> Path:
    """Return the durable rendered-source freeze manifest path."""

    return repo_root / _MANIFEST_PATH


def _write_exact_once(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"existing rendered file does not match frozen bytes: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def freeze_rendered_authored_sources(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    acquisition: AcquisitionReceipt,
    frozen_dependencies: Phase3bFrozenRenderDependencySet,
    policy: Phase3bRenderPolicyFreeze,
    candidate: Phase3bAuthoredRenderCandidate,
    *,
    candidate_sha256: str,
) -> Phase3bRenderedSourceFreeze:
    """Re-render once, prove byte identity, and materialize exact tracked sources."""

    if candidate_sha256 != _AUTHORED_RENDER_CANDIDATE_SHA256:
        raise ValueError("authored render candidate hash does not match accepted evidence")

    expected = {item.source_id: item for item in candidate.documents}
    receipt_by_source = {item.source_id: item for item in acquisition.files}
    renderer = ConstrainedAuthoredRenderer(
        policy,
        build_frozen_data_reference_map(repo_root, frozen_dependencies),
    )
    records: list[RenderedSourceRecord] = []

    for source in plan.files:
        if source.media_type != "markdown":
            continue
        expected_record = expected.get(source.source_id)
        receipt = receipt_by_source.get(source.source_id)
        if expected_record is None or receipt is None:
            raise ValueError(f"render custody missing source: {source.source_id}")

        source_bytes = (repo_root / receipt.cache_path).read_bytes()
        source_sha256 = hashlib.sha256(source_bytes).hexdigest()
        if source_sha256 != expected_record.source_content_sha256:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"source SHA-256 drift: {source.source_id}",
            )
        if git_blob_sha1(source_bytes) != receipt.observed_git_blob_sha1:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"source git blob drift: {source.source_id}",
            )

        rendered, _ = renderer.render(source_bytes.decode("utf-8"))
        rendered_bytes = rendered.encode("utf-8")
        rendered_sha256 = hashlib.sha256(rendered_bytes).hexdigest()
        if rendered_sha256 != expected_record.rendered_content_sha256:
            raise ValueError(f"rendered SHA-256 drift: {source.source_id}")
        if len(rendered_bytes) != expected_record.rendered_byte_count:
            raise ValueError(f"rendered byte-count drift: {source.source_id}")
        if count_active_unresolved_directives(rendered) != 0:
            raise ValueError(f"rendered directives remain active: {source.source_id}")

        rendered_rel = _RENDER_ROOT / f"{source.source_id}.md"
        rendered_path = repo_root / rendered_rel
        _write_exact_once(rendered_path, rendered_bytes)
        if hashlib.sha256(rendered_path.read_bytes()).hexdigest() != rendered_sha256:
            raise ValueError(f"materialized rendered bytes failed verification: {source.source_id}")

        records.append(
            RenderedSourceRecord(
                source_id=source.source_id,
                source_path=source.path,
                rendered_path=rendered_rel.as_posix(),
                source_content_sha256=source_sha256,
                rendered_content_sha256=rendered_sha256,
                rendered_byte_count=len(rendered_bytes),
            )
        )

    ordered = tuple(sorted(records, key=lambda item: item.source_id))
    if len(ordered) != 10:
        raise ValueError("rendered source freeze requires exactly 10 authored documents")

    return Phase3bRenderedSourceFreeze(
        freeze_version="phase3b-rendered-source-freeze-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        source_authored_render_candidate_sha256=_AUTHORED_RENDER_CANDIDATE_SHA256,
        documents=ordered,
    )
