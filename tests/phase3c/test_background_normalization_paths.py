from __future__ import annotations

from pathlib import Path

from rag_reliability.corpus.background import (
    Phase3cBackgroundSelectionManifest,
)
from rag_reliability.corpus.phase3c_background_normalization_runner import (
    _operation_filename,
)

_ROOT = Path(__file__).resolve().parents[2]

_SELECTION_PATH = (
    _ROOT
    / "datasets"
    / "source_manifests"
    / "phase3c_background_selection_v1.json"
)


def _selection() -> Phase3cBackgroundSelectionManifest:
    return Phase3cBackgroundSelectionManifest.model_validate_json(
        _SELECTION_PATH.read_bytes()
    )


def test_operation_filename_is_bounded_and_deterministic() -> None:
    operation_id = (
        "repos/custom-properties-for-repos-"
        "create-or-update-repository-values"
    )

    filename = _operation_filename(operation_id)

    assert filename == "2efbebb3f8b832d192e6c0ab.json"
    assert len(filename) == 29
    assert filename == _operation_filename(operation_id)


def test_all_frozen_phase3c_operation_filenames_are_unique() -> None:
    filenames = tuple(
        _operation_filename(item.operation_id)
        for item in _selection().operations
    )

    assert len(filenames) == 459
    assert len(set(filenames)) == 459