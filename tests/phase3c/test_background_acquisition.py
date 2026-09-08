from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

import rag_reliability.corpus.background_acquisition as custody
from rag_reliability.corpus.background_acquisition import (
    PHASE3B_ACQUISITION_RECEIPT_SHA256,
    Phase3cBackgroundSourceCustodyReceipt,
    cache_content_matches_receipt,
    resolve_background_source,
)
from rag_reliability.corpus.models import (
    AcquiredFileReceipt,
    AcquisitionReceipt,
    CorpusSourceSelectionPlan,
)

_ROOT = Path(__file__).resolve().parents[2]

_PHASE3B_RECEIPT_PATH = (
    _ROOT
    / "artifacts"
    / "development"
    / "phase3b_normalization_acquisition_receipt_v1.json"
)

_SOURCE_SELECTION_PATH = (
    _ROOT
    / "datasets"
    / "source_manifests"
    / "phase3a_source_selection_v1.json"
)


def _phase3b_receipt() -> AcquisitionReceipt:
    return AcquisitionReceipt.model_validate_json(
        _PHASE3B_RECEIPT_PATH.read_bytes()
    )


def _current_source_record() -> AcquiredFileReceipt:
    receipt = _phase3b_receipt()

    matches = tuple(
        item
        for item in receipt.files
        if item.source_id == "openapi-current-2026-03-10"
    )

    assert len(matches) == 1
    return matches[0]


def _current_plan_source():
    plan = CorpusSourceSelectionPlan.model_validate_json(
        _SOURCE_SELECTION_PATH.read_bytes()
    )

    matches = tuple(
        item
        for item in plan.files
        if item.source_id == "openapi-current-2026-03-10"
    )

    assert len(matches) == 1
    return matches[0]


def test_custody_receipt_accepts_frozen_phase3b_source_record() -> None:
    receipt = Phase3cBackgroundSourceCustodyReceipt(
        snapshot_id="github_rest_v1_2026_09_05",
        custody_mode="verified_phase3b_cache_reuse",
        source=_current_source_record(),
    )

    assert receipt.custody_mode == "verified_phase3b_cache_reuse"
    assert (
        receipt.phase3b_acquisition_receipt_sha256
        == PHASE3B_ACQUISITION_RECEIPT_SHA256
    )


def test_custody_receipt_rejects_content_identity_drift() -> None:
    payload = _current_source_record().model_dump(mode="json")
    payload["content_sha256"] = "0" * 64

    drifted = AcquiredFileReceipt.model_validate(payload)

    with pytest.raises(
        ValidationError,
        match="content SHA-256",
    ):
        Phase3cBackgroundSourceCustodyReceipt(
            snapshot_id="github_rest_v1_2026_09_05",
            custody_mode="verified_phase3b_cache_reuse",
            source=drifted,
        )


def test_cache_content_identity_helper_detects_exact_bytes() -> None:
    content = b"synthetic-cache-bytes"

    receipt = AcquiredFileReceipt(
        source_id="synthetic",
        repository="example/repository",
        commit_sha="1" * 40,
        path="source.yaml",
        expected_git_blob_sha1=custody.git_blob_sha1(content),
        observed_git_blob_sha1=custody.git_blob_sha1(content),
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
        cache_path="cache/source.yaml",
    )

    assert cache_content_matches_receipt(content, receipt) is True
    assert cache_content_matches_receipt(b"drift", receipt) is False


def test_resolver_reuses_verified_cache_without_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    accepted = _current_source_record()
    cache_path = tmp_path / accepted.cache_path
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(b"accepted-cache")

    monkeypatch.setattr(
        custody,
        "cache_content_matches_receipt",
        lambda content, receipt: True,
    )

    def forbidden_fetcher(url: str) -> bytes:
        raise AssertionError("network fetch must not occur")

    receipt, content = resolve_background_source(
        tmp_path,
        _current_plan_source(),
        _phase3b_receipt(),
        phase3b_receipt_sha256=PHASE3B_ACQUISITION_RECEIPT_SHA256,
        fetcher=forbidden_fetcher,
    )

    assert receipt.custody_mode == "verified_phase3b_cache_reuse"
    assert content == b"accepted-cache"