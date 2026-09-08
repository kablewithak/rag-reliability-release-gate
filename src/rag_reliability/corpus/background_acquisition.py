"""Evidence-bound source custody for the Phase 3C background corpus."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.acquisition import (
    Fetcher,
    acquire_file,
    git_blob_sha1,
)
from rag_reliability.corpus.background_normalized import (
    BACKGROUND_SELECTION_SHA256,
    SOURCE_SELECTION_SHA256,
)
from rag_reliability.corpus.models import (
    AcquiredFileReceipt,
    AcquisitionReceipt,
    PinnedUpstreamFile,
)

PHASE3B_ACQUISITION_RECEIPT_SHA256: Literal[
    "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"
] = "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"

SourceCustodyMode = Literal[
    "verified_phase3b_cache_reuse",
    "fresh_network_acquisition",
]

_EXPECTED_SOURCE_ID = "openapi-current-2026-03-10"
_EXPECTED_REPOSITORY = "github/rest-api-description"
_EXPECTED_COMMIT = "3cef12e8a02d612ad032473d4fb87266f2befeae"
_EXPECTED_PATH = (
    "descriptions/api.github.com/"
    "api.github.com.2026-03-10.yaml"
)
_EXPECTED_BLOB_SHA1 = "a6c606f584dd8f7a17802a47ef8db8d167a44345"
_EXPECTED_CONTENT_SHA256 = (
    "6ffbf0b998af0b35763ab2defb9eaef90029887dce23514c84dabe0f3a339b3d"
)
_EXPECTED_BYTE_COUNT = 9750362
_EXPECTED_CACHE_PATH = (
    "datasets/source_documents/_upstream_cache/"
    "a6c606f584dd8f7a17802a47ef8db8d167a44345.yaml"
)


class Phase3cBackgroundSourceCustodyReceipt(ContractModel):
    """Proof of the exact immutable bytes used by Phase 3C."""

    receipt_version: Literal[
        "phase3c-background-source-custody-receipt-v1"
    ] = "phase3c-background-source-custody-receipt-v1"

    snapshot_id: Literal["github_rest_v1_2026_09_05"]

    source_selection_sha256: Literal[
        "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
    ] = SOURCE_SELECTION_SHA256

    background_selection_sha256: Literal[
        "d2cc4ade659534973915ad26b10daad8173a9eeba5eeaebc6de42b6d848708aa"
    ] = BACKGROUND_SELECTION_SHA256

    phase3b_acquisition_receipt_sha256: Literal[
        "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"
    ] = PHASE3B_ACQUISITION_RECEIPT_SHA256

    custody_mode: SourceCustodyMode
    source: AcquiredFileReceipt

    @model_validator(mode="after")
    def validate_frozen_source(
        self,
    ) -> Phase3cBackgroundSourceCustodyReceipt:
        source = self.source

        if source.source_id != _EXPECTED_SOURCE_ID:
            raise ValueError("Phase 3C source ID does not match frozen identity")
        if source.repository != _EXPECTED_REPOSITORY:
            raise ValueError("Phase 3C repository does not match frozen identity")
        if source.commit_sha != _EXPECTED_COMMIT:
            raise ValueError("Phase 3C commit does not match frozen identity")
        if source.path != _EXPECTED_PATH:
            raise ValueError("Phase 3C path does not match frozen identity")
        if source.expected_git_blob_sha1 != _EXPECTED_BLOB_SHA1:
            raise ValueError("Phase 3C expected Git blob does not match frozen identity")
        if source.observed_git_blob_sha1 != _EXPECTED_BLOB_SHA1:
            raise ValueError("Phase 3C observed Git blob does not match frozen identity")
        if source.content_sha256 != _EXPECTED_CONTENT_SHA256:
            raise ValueError("Phase 3C content SHA-256 does not match frozen identity")
        if source.byte_count != _EXPECTED_BYTE_COUNT:
            raise ValueError("Phase 3C byte count does not match frozen identity")
        if source.cache_path != _EXPECTED_CACHE_PATH:
            raise ValueError("Phase 3C cache path does not match frozen identity")

        return self


def _phase3b_current_source(
    receipt: AcquisitionReceipt,
) -> AcquiredFileReceipt:
    matches = tuple(
        item
        for item in receipt.files
        if item.source_id == _EXPECTED_SOURCE_ID
    )

    if len(matches) != 1:
        raise ValueError(
            "accepted Phase 3B receipt must contain exactly one current OpenAPI source"
        )

    return matches[0]


def _validate_plan_alignment(
    source: PinnedUpstreamFile,
    accepted: AcquiredFileReceipt,
) -> None:
    if source.source_id != accepted.source_id:
        raise ValueError("source plan and accepted receipt source IDs differ")
    if source.repository != accepted.repository:
        raise ValueError("source plan and accepted receipt repositories differ")
    if source.commit_sha != accepted.commit_sha:
        raise ValueError("source plan and accepted receipt commits differ")
    if source.path != accepted.path:
        raise ValueError("source plan and accepted receipt paths differ")
    if source.expected_git_blob_sha1 != accepted.expected_git_blob_sha1:
        raise ValueError("source plan and accepted receipt Git blobs differ")


def cache_content_matches_receipt(
    content: bytes,
    receipt: AcquiredFileReceipt,
) -> bool:
    """Return whether bytes exactly satisfy a prior acquisition receipt."""

    if not content:
        return False

    return (
        len(content) == receipt.byte_count
        and hashlib.sha256(content).hexdigest() == receipt.content_sha256
        and git_blob_sha1(content) == receipt.expected_git_blob_sha1
        and receipt.observed_git_blob_sha1 == receipt.expected_git_blob_sha1
    )


def resolve_background_source(
    repo_root: Path,
    source: PinnedUpstreamFile,
    phase3b_receipt: AcquisitionReceipt,
    *,
    phase3b_receipt_sha256: Sha256,
    fetcher: Fetcher | None = None,
) -> tuple[Phase3cBackgroundSourceCustodyReceipt, bytes]:
    """Reuse accepted immutable bytes when valid; otherwise reacquire them."""

    if phase3b_receipt_sha256 != PHASE3B_ACQUISITION_RECEIPT_SHA256:
        raise ValueError(
            "Phase 3B acquisition receipt SHA-256 does not match accepted evidence"
        )

    accepted = _phase3b_current_source(phase3b_receipt)
    _validate_plan_alignment(source, accepted)

    cache_path = repo_root / accepted.cache_path

    if cache_path.is_file():
        cached = cache_path.read_bytes()

        if cache_content_matches_receipt(cached, accepted):
            custody = Phase3cBackgroundSourceCustodyReceipt(
                snapshot_id=phase3b_receipt.snapshot_id,
                custody_mode="verified_phase3b_cache_reuse",
                source=accepted,
            )
            return custody, cached

    if fetcher is None:
        acquired = acquire_file(repo_root, source)
    else:
        acquired = acquire_file(repo_root, source, fetcher)

    _validate_plan_alignment(source, acquired)

    if (
        acquired.content_sha256 != accepted.content_sha256
        or acquired.byte_count != accepted.byte_count
        or acquired.observed_git_blob_sha1 != accepted.observed_git_blob_sha1
    ):
        raise ValueError(
            "fresh Phase 3C acquisition does not match accepted immutable source"
        )

    content = (repo_root / acquired.cache_path).read_bytes()

    if not cache_content_matches_receipt(content, acquired):
        raise ValueError(
            "fresh Phase 3C cache failed post-acquisition identity verification"
        )

    custody = Phase3cBackgroundSourceCustodyReceipt(
        snapshot_id=phase3b_receipt.snapshot_id,
        custody_mode="fresh_network_acquisition",
        source=acquired,
    )

    return custody, content