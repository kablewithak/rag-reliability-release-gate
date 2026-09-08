from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rag_reliability.corpus.phase3c_background_selection_runner import (
    load_and_build_background_selection,
    write_background_selection_manifest,
)

_ROOT = Path(__file__).resolve().parents[2]

_CATALOG_PATH = (
    _ROOT
    / "artifacts"
    / "development"
    / "phase3a_operation_catalog_candidate_v1.json"
)
_ALLOWLIST_PATH = (
    _ROOT
    / "datasets"
    / "source_manifests"
    / "phase3a_operation_allowlist_v1.json"
)


def test_runner_builds_frozen_459_operation_selection() -> None:
    manifest = load_and_build_background_selection(
        _CATALOG_PATH,
        _ALLOWLIST_PATH,
    )

    assert manifest.operation_count == 459
    assert len(manifest.operations) == 459
    assert manifest.selection_status == "frozen_background_selection"
    assert manifest.normalization_authorized is True
    assert manifest.full_ingestion_ready is False


def test_runner_writes_manifest_and_matching_sha_sidecar(
    tmp_path: Path,
) -> None:
    manifest = load_and_build_background_selection(
        _CATALOG_PATH,
        _ALLOWLIST_PATH,
    )

    output_path = tmp_path / "phase3c_background_selection_v1.json"

    digest = write_background_selection_manifest(
        manifest,
        output_path,
    )

    observed = hashlib.sha256(output_path.read_bytes()).hexdigest()
    sidecar = output_path.with_suffix(".json.sha256")

    assert digest == observed
    assert sidecar.read_text(encoding="utf-8") == (
        f"{digest}  {output_path.name}\n"
    )

    repeated_digest = write_background_selection_manifest(
        manifest,
        output_path,
    )
    assert repeated_digest == digest


def test_runner_rejects_existing_manifest_drift(
    tmp_path: Path,
) -> None:
    manifest = load_and_build_background_selection(
        _CATALOG_PATH,
        _ALLOWLIST_PATH,
    )

    output_path = tmp_path / "phase3c_background_selection_v1.json"
    output_path.write_text('{"drift": true}\n', encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="does not match expected bytes",
    ):
        write_background_selection_manifest(
            manifest,
            output_path,
        )
