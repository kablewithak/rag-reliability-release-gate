from pathlib import Path

import pytest

from rag_reliability.contracts.enums import AuthorityLevel, DataRole, SourceState
from rag_reliability.corpus.acquisition import acquire_file, git_blob_sha1, raw_github_url
from rag_reliability.corpus.models import PinnedUpstreamFile


def _entry(
    content: bytes,
    path: str = "content/rest/about-the-rest-api/api-versions.md",
) -> PinnedUpstreamFile:
    return PinnedUpstreamFile(
        source_id="test-source",
        repository="github/docs",
        commit_sha="ec3629a841129ae28189d7bb2274a7b3d40c5095",
        path=path,
        expected_git_blob_sha1=git_blob_sha1(content),
        source_license="CC-BY-4.0",
        media_type="markdown",
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        api_version_or_snapshot="2026-03-10",
        data_role=DataRole.CORPUS_SOURCE,
    )


def test_git_blob_sha1_matches_git_object_format() -> None:
    assert git_blob_sha1(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_raw_url_uses_immutable_commit() -> None:
    item = _entry(b"hello\n")

    url = raw_github_url(item)

    assert item.commit_sha in url
    assert "/main/" not in url
    assert "/master/" not in url


def test_acquisition_verifies_blob_and_writes_only_to_upstream_cache(tmp_path: Path) -> None:
    content = b"frozen source bytes\n"
    item = _entry(content)

    receipt = acquire_file(tmp_path, item, fetcher=lambda _: content)

    cached = tmp_path / receipt.cache_path
    assert cached.read_bytes() == content
    assert receipt.observed_git_blob_sha1 == item.expected_git_blob_sha1
    assert receipt.cache_path.startswith("datasets/source_documents/_upstream_cache/")


def test_acquisition_uses_bounded_content_addressed_cache_path(tmp_path: Path) -> None:
    content = b"frozen source bytes\n"
    item = _entry(
        content,
        path="content/rest/authentication/keeping-your-api-credentials-secure.md",
    )

    receipt = acquire_file(tmp_path, item, fetcher=lambda _: content)

    expected_name = f"{item.expected_git_blob_sha1}.md"
    assert Path(receipt.cache_path).name == expected_name
    assert item.path not in receipt.cache_path
    assert len(receipt.cache_path) < 120
    assert (tmp_path / receipt.cache_path).read_bytes() == content


def test_acquisition_fails_closed_on_blob_mismatch(tmp_path: Path) -> None:
    item = _entry(b"expected\n")

    with pytest.raises(ValueError, match="git blob identity mismatch"):
        acquire_file(tmp_path, item, fetcher=lambda _: b"unexpected\n")
