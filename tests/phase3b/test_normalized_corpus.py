from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.corpus import RealSourceRecord
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.normalization import (
    collect_local_reference_closure,
    index_openapi_operations,
    markdown_title,
    normalize_markdown,
    normalize_openapi_operation,
    sha256_text,
    write_exact_text,
)
from rag_reliability.corpus.normalized import NormalizedCorpusDocument


def _provenance(source_family: CorpusSourceFamily) -> RealSourceRecord:
    return RealSourceRecord(
        source_id="source-1",
        source_family=source_family,
        source_url="https://github.com/github/rest-api-description",
        source_license="MIT",
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        source_commit_sha_or_version="3cef12e8a02d612ad032473d4fb87266f2befeae",
        document_version="2026-03-10",
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
        content_sha256="a" * 64,
        title="Example",
        topic_tags=("issues",),
        data_role=DataRole.CORPUS_SOURCE,
    )


def test_normalize_markdown_is_stable() -> None:
    assert normalize_markdown("A  \r\nB\r\n") == "A\nB\n"


def test_markdown_title_prefers_frontmatter_title() -> None:
    source = "---\ntitle: REST API versions\n---\n# Ignored heading\n"
    assert markdown_title(source, "fallback") == "REST API versions"


def test_openapi_operation_collects_transitive_local_references() -> None:
    spec = {
        "paths": {
            "/issues": {
                "post": {
                    "operationId": "issues/create",
                    "responses": {"200": {"$ref": "#/components/responses/Issue"}},
                }
            }
        },
        "components": {
            "responses": {
                "Issue": {
                    "description": "ok",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Issue"}
                        }
                    },
                }
            },
            "schemas": {
                "Issue": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                }
            },
        },
    }

    closure = collect_local_reference_closure(spec, spec["paths"]["/issues"]["post"])
    assert tuple(closure) == (
        "#/components/responses/Issue",
        "#/components/schemas/Issue",
    )

    operation_index = index_openapi_operations(spec)
    assert operation_index["issues/create"] == ("/issues", "post")

    normalized = normalize_openapi_operation(spec, "/issues", "post")
    assert sha256_text(normalized) == sha256_text(normalized)


def test_openapi_index_rejects_duplicate_operation_ids() -> None:
    spec = {
        "paths": {
            "/a": {"get": {"operationId": "duplicate"}},
            "/b": {"get": {"operationId": "duplicate"}},
        }
    }
    with pytest.raises(ValueError, match="duplicate OpenAPI operationId"):
        index_openapi_operations(spec)


def test_exact_writer_rejects_existing_drift(tmp_path: Path) -> None:
    path = tmp_path / "normalized.md"
    digest, byte_count = write_exact_text(path, "expected\n")
    assert digest == sha256_text("expected\n")
    assert byte_count == len(b"expected\n")

    path.write_text("drift\n", encoding="utf-8")
    with pytest.raises(ValueError, match="does not match expected bytes"):
        write_exact_text(path, "expected\n")


def test_manifest_document_is_metadata_only() -> None:
    assert "content" not in NormalizedCorpusDocument.model_fields
    assert "content_path" in NormalizedCorpusDocument.model_fields


def test_openapi_document_requires_complete_operation_identity() -> None:
    provenance = _provenance(CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT)

    with pytest.raises(ValidationError):
        NormalizedCorpusDocument(
            document_id="openapi-current-issues-create",
            document_kind="openapi_operation_contract",
            content_path="datasets/source_documents/normalized/example.json",
            normalized_content_sha256="b" * 64,
            normalized_byte_count=2,
            provenance=provenance,
            semantic_family="issues",
            operation_id="issues/create",
            method="post",
        )


def test_authored_document_rejects_operation_identity() -> None:
    provenance = _provenance(CorpusSourceFamily.GITHUB_REST_AUTHORED_GUIDANCE)

    with pytest.raises(ValidationError):
        NormalizedCorpusDocument(
            document_id="guide-1",
            document_kind="authored_guidance",
            content_path="datasets/source_documents/normalized/guide.md",
            normalized_content_sha256="c" * 64,
            normalized_byte_count=10,
            provenance=provenance,
            semantic_family="issues",
            operation_id="issues/create",
            method="post",
            path="/issues",
        )
