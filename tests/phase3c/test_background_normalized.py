from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from rag_reliability.contracts.corpus import RealSourceRecord
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.background import (
    Phase3cBackgroundSelectionManifest,
)
from rag_reliability.corpus.background_normalized import (
    BACKGROUND_SELECTION_SHA256,
    PHASE3B_NORMALIZED_MANIFEST_SHA256,
    SOURCE_SELECTION_SHA256,
    build_background_normalized_manifest,
)
from rag_reliability.corpus.normalized import NormalizedCorpusDocument

_ROOT = Path(__file__).resolve().parents[2]

_SELECTION_PATH = (
    _ROOT
    / "datasets"
    / "source_manifests"
    / "phase3c_background_selection_v1.json"
)


def _load_selection() -> Phase3cBackgroundSelectionManifest:
    return Phase3cBackgroundSelectionManifest.model_validate_json(
        _SELECTION_PATH.read_bytes()
    )


def _fake_documents() -> tuple[NormalizedCorpusDocument, ...]:
    selection = _load_selection()
    retrieved_at = datetime(2026, 9, 8, tzinfo=UTC)

    documents: list[NormalizedCorpusDocument] = []

    for operation in selection.operations:
        normalized_sha = hashlib.sha256(
            operation.operation_id.encode("utf-8")
        ).hexdigest()

        filename = operation.operation_id.replace("/", "__") + ".json"

        provenance = RealSourceRecord(
            source_id=(
                "openapi-current-2026-03-10:"
                f"{operation.operation_id}"
            ),
            source_family=CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT,
            source_url=(
                "https://raw.githubusercontent.com/"
                "github/rest-api-description/"
                "3cef12e8a02d612ad032473d4fb87266f2befeae/"
                "descriptions/api.github.com/"
                "api.github.com.2026-03-10.yaml"
            ),
            source_license="MIT",
            retrieved_at=retrieved_at,
            source_commit_sha_or_version=(
                "3cef12e8a02d612ad032473d4fb87266f2befeae"
            ),
            document_version="2026-03-10",
            authority_level=AuthorityLevel.AUTHORITATIVE,
            source_state=SourceState.CURRENT,
            product_scope="api.github.com",
            api_version_or_snapshot="2026-03-10",
            content_sha256="a" * 64,
            title=operation.operation_id,
            topic_tags=("rest-api", operation.family),
            data_role=DataRole.BACKGROUND_LOAD_SOURCE,
        )

        documents.append(
            NormalizedCorpusDocument(
                document_id=(
                    "openapi-background-"
                    f"{operation.operation_id.replace('/', '-')}"
                ),
                document_kind="openapi_operation_contract",
                content_path=(
                    "datasets/source_documents/normalized/"
                    "phase3c_background_v1/openapi/current/"
                    f"{operation.family}/{filename}"
                ),
                normalized_content_sha256=normalized_sha,
                normalized_byte_count=1,
                provenance=provenance,
                semantic_family=operation.family,
                operation_id=operation.operation_id,
                method=operation.method,
                path=operation.path,
            )
        )

    return tuple(
        sorted(
            documents,
            key=lambda item: item.document_id,
        )
    )


def _build():
    return build_background_normalized_manifest(
        _load_selection(),
        selection_sha256=BACKGROUND_SELECTION_SHA256,
        phase3b_manifest_sha256=PHASE3B_NORMALIZED_MANIFEST_SHA256,
        source_selection_sha256=SOURCE_SELECTION_SHA256,
        source_custody_receipt_sha256="b" * 64,
        retrieved_at=datetime(2026, 9, 8, tzinfo=UTC),
        documents=_fake_documents(),
    )


def test_completed_background_manifest_reconciles_to_509_documents() -> None:
    manifest = _build()

    assert manifest.background_document_count == 459
    assert len(manifest.documents) == 459
    assert manifest.phase3b_document_count == 50
    assert manifest.full_corpus_document_count == 509


def test_completed_background_manifest_preserves_downstream_stop_gate() -> None:
    manifest = _build()

    assert manifest.background_normalized_ready is True
    assert manifest.full_ingestion_ready is True
    assert manifest.chunking_authorized is False
    assert manifest.baseline_authorized is False
    assert manifest.release_eligible is False


def test_completed_background_manifest_uses_background_source_role() -> None:
    manifest = _build()

    assert all(
        document.provenance.data_role is DataRole.BACKGROUND_LOAD_SOURCE
        for document in manifest.documents
    )
    assert all(
        document.provenance.source_state is SourceState.CURRENT
        for document in manifest.documents
    )


def test_builder_rejects_wrong_phase3b_parent_identity() -> None:
    with pytest.raises(
        ValueError,
        match="Phase 3B normalized manifest SHA-256",
    ):
        build_background_normalized_manifest(
            _load_selection(),
            selection_sha256=BACKGROUND_SELECTION_SHA256,
            phase3b_manifest_sha256="0" * 64,
            source_selection_sha256=SOURCE_SELECTION_SHA256,
            source_custody_receipt_sha256="b" * 64,
            retrieved_at=datetime(2026, 9, 8, tzinfo=UTC),
            documents=_fake_documents(),
        )
