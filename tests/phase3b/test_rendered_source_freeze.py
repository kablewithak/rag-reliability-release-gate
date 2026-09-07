from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_reliability.corpus.rendered_source_freeze import (
    Phase3bRenderedSourceFreeze,
    RenderedSourceRecord,
    _write_exact_once,
    rendered_source_manifest_path,
)

_CANDIDATE_SHA = "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"
_CONTENT_SHA = "a" * 64


def _record(index: int) -> RenderedSourceRecord:
    source_id = f"docs-{index:02d}"
    return RenderedSourceRecord(
        source_id=source_id,
        source_path=f"content/rest/{source_id}.md",
        rendered_path=(
            "datasets/source_documents/rendered/phase3b_authored_v1/"
            f"{source_id}.md"
        ),
        source_content_sha256=_CONTENT_SHA,
        rendered_content_sha256=_CONTENT_SHA,
        rendered_byte_count=10,
    )


def test_rendered_source_manifest_path_is_versioned() -> None:
    root = Path("repo")
    assert rendered_source_manifest_path(root) == (
        root / "datasets/source_manifests/phase3b_rendered_source_freeze_v1.json"
    )


def test_rendered_source_freeze_requires_sorted_unique_documents() -> None:
    records = tuple(_record(index) for index in range(10))
    frozen = Phase3bRenderedSourceFreeze(
        freeze_version="phase3b-rendered-source-freeze-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        source_authored_render_candidate_sha256=_CANDIDATE_SHA,
        documents=records,
    )
    assert frozen.normalization_authorized is True

    with pytest.raises(ValidationError):
        Phase3bRenderedSourceFreeze(
            freeze_version="phase3b-rendered-source-freeze-v1",
            snapshot_id="github_rest_v1_2026_09_05",
            source_authored_render_candidate_sha256=_CANDIDATE_SHA,
            documents=tuple(reversed(records)),
        )


def test_write_exact_once_is_idempotent_and_fails_on_drift(tmp_path: Path) -> None:
    path = tmp_path / "rendered.md"
    _write_exact_once(path, b"stable\n")
    _write_exact_once(path, b"stable\n")
    with pytest.raises(ValueError, match="does not match frozen bytes"):
        _write_exact_once(path, b"drift\n")
