"""Fail-closed acquisition of exact pinned corpus source files."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from urllib.request import Request, urlopen

from rag_reliability.corpus.models import (
    AcquiredFileReceipt,
    AcquisitionReceipt,
    CorpusSourceSelectionPlan,
    PinnedUpstreamFile,
)

Fetcher = Callable[[str], bytes]


def raw_github_url(item: PinnedUpstreamFile) -> str:
    return (
        "https://raw.githubusercontent.com/"
        f"{item.repository}/{item.commit_sha}/{item.path}"
    )


def git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def _default_fetcher(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "rag-reliability-release-gate/0.1"})
    with urlopen(request, timeout=60) as response:
        return bytes(response.read())


def _cache_path(repo_root: Path, item: PinnedUpstreamFile) -> Path:
    suffix = ".md" if item.media_type == "markdown" else ".yaml"
    return (
        repo_root
        / "datasets"
        / "source_documents"
        / "_upstream_cache"
        / f"{item.expected_git_blob_sha1}{suffix}"
    )


def acquire_file(
    repo_root: Path,
    item: PinnedUpstreamFile,
    fetcher: Fetcher = _default_fetcher,
) -> AcquiredFileReceipt:
    content = fetcher(raw_github_url(item))
    if not content:
        raise ValueError(f"upstream source is empty: {item.source_id}")

    observed_blob = git_blob_sha1(content)
    if observed_blob != item.expected_git_blob_sha1:
        raise ValueError(f"git blob identity mismatch: {item.source_id}")

    cache_path = _cache_path(repo_root, item)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(content)

    relative_cache_path = cache_path.relative_to(repo_root).as_posix()
    return AcquiredFileReceipt(
        source_id=item.source_id,
        repository=item.repository,
        commit_sha=item.commit_sha,
        path=item.path,
        expected_git_blob_sha1=item.expected_git_blob_sha1,
        observed_git_blob_sha1=observed_blob,
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
        cache_path=relative_cache_path,
    )


def acquire_selection(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    fetcher: Fetcher = _default_fetcher,
) -> AcquisitionReceipt:
    receipts = tuple(acquire_file(repo_root, item, fetcher) for item in plan.files)
    return AcquisitionReceipt(
        receipt_version="phase3a-acquisition-receipt-v1",
        snapshot_id=plan.snapshot_id,
        files=receipts,
    )
