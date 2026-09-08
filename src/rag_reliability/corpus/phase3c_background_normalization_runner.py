"""Materialize and verify the full Phase 3C real background corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import AnyHttpUrl

from rag_reliability.contracts.corpus import RealSourceRecord
from rag_reliability.contracts.enums import (
    CorpusSourceFamily,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.acquisition import raw_github_url
from rag_reliability.corpus.background import (
    Phase3cBackgroundSelectionManifest,
)
from rag_reliability.corpus.background_acquisition import (
    PHASE3B_ACQUISITION_RECEIPT_SHA256,
    resolve_background_source,
)
from rag_reliability.corpus.background_normalized import (
    BACKGROUND_SELECTION_SHA256,
    PHASE3B_NORMALIZED_MANIFEST_SHA256,
    SOURCE_SELECTION_SHA256,
    Phase3cBackgroundNormalizedCorpusReceipt,
    build_background_normalized_manifest,
)
from rag_reliability.corpus.models import (
    AcquisitionReceipt,
    CorpusSourceSelectionPlan,
    PinnedUpstreamFile,
)
from rag_reliability.corpus.normalization import (
    index_openapi_operations,
    normalize_openapi_operation,
    write_exact_text,
)
from rag_reliability.corpus.normalized import (
    NormalizedCorpusDocument,
    Phase3bNormalizedCorpusManifest,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256

_SOURCE_SELECTION_PATH = Path(
    "datasets/source_manifests/phase3a_source_selection_v1.json"
)
_BACKGROUND_SELECTION_PATH = Path(
    "datasets/source_manifests/phase3c_background_selection_v1.json"
)
_PHASE3B_MANIFEST_PATH = Path(
    "datasets/source_manifests/phase3b_normalized_corpus_v1.json"
)

_NORMALIZED_ROOT = Path(
    "datasets/source_documents/normalized/"
    "phase3c_background_v1/openapi/current"
)

_BACKGROUND_MANIFEST_PATH = Path(
    "datasets/source_manifests/"
    "phase3c_background_normalized_corpus_v1.json"
)

_PHASE3B_ACQUISITION_RECEIPT_PATH = Path(
    "artifacts/development/"
    "phase3b_normalization_acquisition_receipt_v1.json"
)

_SOURCE_CUSTODY_RECEIPT_PATH = Path(
    "artifacts/development/"
    "phase3c_background_source_custody_receipt_v1.json"
)

_NORMALIZATION_RECEIPT_PATH = Path(
    "artifacts/development/"
    "phase3c_background_normalized_corpus_receipt_v1.json"
)


def _read_and_hash(path: Path) -> tuple[bytes, str]:
    content = path.read_bytes()
    return content, hashlib.sha256(content).hexdigest()


def _read_verified_json(path: Path) -> tuple[bytes, str]:
    content, digest = _read_and_hash(path)

    sidecar = path.with_suffix(path.suffix + ".sha256")
    parts = sidecar.read_text(encoding="utf-8").strip().split()

    if len(parts) != 2 or parts[1] != path.name:
        raise ValueError(f"malformed SHA-256 sidecar: {path.name}")
    if parts[0] != digest:
        raise ValueError(f"SHA-256 sidecar mismatch: {path.name}")

    return content, digest


def _current_openapi_source(
    plan: CorpusSourceSelectionPlan,
) -> PinnedUpstreamFile:
    matches = tuple(
        item
        for item in plan.files
        if item.media_type == "openapi_yaml"
        and item.source_state is SourceState.CURRENT
    )

    if len(matches) != 1:
        raise ValueError(
            "Phase 3C requires exactly one current OpenAPI source"
        )

    source = matches[0]

    if source.source_id != "openapi-current-2026-03-10":
        raise ValueError("unexpected current OpenAPI source ID")

    return source


def _require_openapi_root(
    content: bytes,
    source_id: str,
) -> Mapping[str, Any]:
    loaded: object = yaml.safe_load(content)

    if not isinstance(loaded, Mapping):
        raise ValueError(
            f"OpenAPI source is not a mapping: {source_id}"
        )

    return loaded


def _operation_filename(operation_id: str) -> str:
    """Return a bounded deterministic filename for one operation ID."""

    digest = hashlib.sha256(
        operation_id.encode("utf-8")
    ).hexdigest()[:24]

    return f"{digest}.json"


def _verify_materialized_files(
    repo_root: Path,
    documents: tuple[NormalizedCorpusDocument, ...],
) -> int:
    verified = 0

    for document in documents:
        content = (repo_root / document.content_path).read_bytes()

        if (
            hashlib.sha256(content).hexdigest()
            != document.normalized_content_sha256
        ):
            raise ValueError(
                f"normalized file SHA-256 mismatch: {document.document_id}"
            )

        if len(content) != document.normalized_byte_count:
            raise ValueError(
                f"normalized file byte-count mismatch: {document.document_id}"
            )

        verified += 1

    return verified


def _build_background_documents(
    repo_root: Path,
    selection: Phase3cBackgroundSelectionManifest,
    source: PinnedUpstreamFile,
    source_content: bytes,
    *,
    source_content_sha256: str,
    retrieved_at: datetime,
) -> tuple[NormalizedCorpusDocument, ...]:
    root = _require_openapi_root(source_content, source.source_id)
    operation_index = index_openapi_operations(root)

    documents: list[NormalizedCorpusDocument] = []

    for selected in selection.operations:
        identity = operation_index.get(selected.operation_id)

        if identity is None:
            raise ValueError(
                "selected Phase 3C operation is missing from current OpenAPI: "
                f"{selected.operation_id}"
            )

        path, method = identity

        if path != selected.path or method != selected.method:
            raise ValueError(
                "selected Phase 3C operation identity drifted: "
                f"{selected.operation_id}"
            )

        normalized = normalize_openapi_operation(
            root,
            path,
            method,
        )

        filename = _operation_filename(selected.operation_id)

        relative = (
            _NORMALIZED_ROOT
            / selected.family
            / filename
        )

        digest, byte_count = write_exact_text(
            repo_root / relative,
            normalized,
        )

        provenance = RealSourceRecord(
            source_id=(
                f"{source.source_id}:{selected.operation_id}"
            ),
            source_family=CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT,
            source_url=AnyHttpUrl(raw_github_url(source)),
            source_license=source.source_license,
            retrieved_at=retrieved_at,
            source_commit_sha_or_version=source.commit_sha,
            document_version=source.api_version_or_snapshot,
            authority_level=source.authority_level,
            source_state=source.source_state,
            product_scope=source.product_scope,
            api_version_or_snapshot=source.api_version_or_snapshot,
            content_sha256=source_content_sha256,
            title=selected.operation_id,
            topic_tags=("rest-api", selected.family),
            data_role=DataRole.BACKGROUND_LOAD_SOURCE,
        )

        documents.append(
            NormalizedCorpusDocument(
                document_id=(
                    "openapi-background-"
                    f"{selected.operation_id.replace('/', '-')}"
                ),
                document_kind="openapi_operation_contract",
                content_path=relative.as_posix(),
                normalized_content_sha256=digest,
                normalized_byte_count=byte_count,
                provenance=provenance,
                semantic_family=selected.family,
                operation_id=selected.operation_id,
                method=selected.method,
                path=selected.path,
            )
        )

    return tuple(
        sorted(
            documents,
            key=lambda item: item.document_id,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    source_selection_bytes, source_selection_sha = _read_and_hash(
        repo_root / _SOURCE_SELECTION_PATH
    )

    if source_selection_sha != SOURCE_SELECTION_SHA256:
        raise ValueError(
            "source selection SHA-256 does not match frozen Phase 3A evidence"
        )

    source_plan = CorpusSourceSelectionPlan.model_validate_json(
        source_selection_bytes
    )

    background_selection_bytes, background_selection_sha = (
        _read_verified_json(
            repo_root / _BACKGROUND_SELECTION_PATH
        )
    )

    if background_selection_sha != BACKGROUND_SELECTION_SHA256:
        raise ValueError(
            "background selection SHA-256 does not match frozen Phase 3C evidence"
        )

    background_selection = (
        Phase3cBackgroundSelectionManifest.model_validate_json(
            background_selection_bytes
        )
    )

    phase3b_bytes, phase3b_sha = _read_verified_json(
        repo_root / _PHASE3B_MANIFEST_PATH
    )

    if phase3b_sha != PHASE3B_NORMALIZED_MANIFEST_SHA256:
        raise ValueError(
            "Phase 3B normalized manifest SHA-256 does not match accepted evidence"
        )

    phase3b_manifest = (
        Phase3bNormalizedCorpusManifest.model_validate_json(
            phase3b_bytes
        )
    )

    phase3b_verified = _verify_materialized_files(
        repo_root,
        phase3b_manifest.documents,
    )

    if phase3b_verified != 50:
        raise ValueError(
            "Phase 3B parent file verification did not reconcile to 50"
        )

    phase3b_acquisition_bytes, phase3b_acquisition_sha = (
        _read_verified_json(
            repo_root / _PHASE3B_ACQUISITION_RECEIPT_PATH
        )
    )

    if (
        phase3b_acquisition_sha
        != PHASE3B_ACQUISITION_RECEIPT_SHA256
    ):
        raise ValueError(
            "Phase 3B acquisition receipt SHA-256 "
            "does not match accepted evidence"
        )

    phase3b_acquisition = AcquisitionReceipt.model_validate_json(
        phase3b_acquisition_bytes
    )

    source = _current_openapi_source(source_plan)

    retrieval_started_at = datetime.now(UTC)

    source_custody, source_content = resolve_background_source(
        repo_root,
        source,
        phase3b_acquisition,
        phase3b_receipt_sha256=phase3b_acquisition_sha,
    )

    retrieval_completed_at = datetime.now(UTC)

    source_custody_sha = write_json_with_sha256(
        repo_root / _SOURCE_CUSTODY_RECEIPT_PATH,
        source_custody,
    )

    observed_source_sha256 = hashlib.sha256(
        source_content
    ).hexdigest()

    if (
        observed_source_sha256
        != source_custody.source.content_sha256
    ):
        raise ValueError(
            "Phase 3C source bytes failed custody SHA-256 verification"
        )

    documents = _build_background_documents(
        repo_root,
        background_selection,
        source,
        source_content,
        source_content_sha256=source_custody.source.content_sha256,
        retrieved_at=retrieval_completed_at,
    )

    background_verified = _verify_materialized_files(
        repo_root,
        documents,
    )

    if background_verified != 459:
        raise ValueError(
            "Phase 3C background verification did not reconcile to 459"
        )

    manifest = build_background_normalized_manifest(
        background_selection,
        selection_sha256=background_selection_sha,
        phase3b_manifest_sha256=phase3b_sha,
        source_selection_sha256=source_selection_sha,
        source_custody_receipt_sha256=source_custody_sha,
        retrieved_at=retrieval_completed_at,
        documents=documents,
    )

    manifest_sha = write_json_with_sha256(
        repo_root / _BACKGROUND_MANIFEST_PATH,
        manifest,
    )

    receipt = Phase3cBackgroundNormalizedCorpusReceipt(
        phase3b_normalized_manifest_sha256=(
            PHASE3B_NORMALIZED_MANIFEST_SHA256
        ),
        background_selection_sha256=BACKGROUND_SELECTION_SHA256,
        source_selection_sha256=SOURCE_SELECTION_SHA256,
        source_custody_receipt_sha256=source_custody_sha,
        normalized_manifest_sha256=manifest_sha,
        retrieval_started_at=retrieval_started_at,
        retrieval_completed_at=retrieval_completed_at,
        family_counts=background_selection.family_counts,
    )

    receipt_sha = write_json_with_sha256(
        repo_root / _NORMALIZATION_RECEIPT_PATH,
        receipt,
    )

    family_counts = {
        item.family: item.selected_count
        for item in background_selection.family_counts
    }

    print(
        "PHASE3C_BACKGROUND_SELECTION_SHA256="
        f"{background_selection_sha}"
    )
    print(
        "PHASE3C_PHASE3B_PARENT_MANIFEST_SHA256="
        f"{phase3b_sha}"
    )
    print(
        "PHASE3C_SOURCE_SELECTION_SHA256="
        f"{source_selection_sha}"
    )
    print(
        "PHASE3C_PHASE3B_ACQUISITION_RECEIPT_SHA256="
        f"{phase3b_acquisition_sha}"
    )
    print(
        "PHASE3C_SOURCE_CUSTODY_MODE="
        f"{source_custody.custody_mode}"
    )
    print(
        "PHASE3C_SOURCE_CUSTODY_RECEIPT_SHA256="
        f"{source_custody_sha}"
    )
    print(
        "PHASE3C_RETRIEVED_AT="
        f"{retrieval_completed_at.isoformat()}"
    )
    print("PHASE3C_PHASE3B_PARENT_DOCUMENT_COUNT=50")
    print(
        "PHASE3C_PHASE3B_PARENT_FILE_IDENTITY_MATCH_COUNT="
        f"{phase3b_verified}"
    )
    print("PHASE3C_BACKGROUND_DOCUMENT_COUNT=459")
    print(
        "PHASE3C_BACKGROUND_FILE_IDENTITY_MATCH_COUNT="
        f"{background_verified}"
    )
    print(
        "PHASE3C_BACKGROUND_FAMILY_COUNTS="
        f"{json.dumps(family_counts, sort_keys=True)}"
    )
    print("PHASE3C_FULL_CORPUS_DOCUMENT_COUNT=509")
    print(
        "PHASE3C_FULL_CORPUS_FILE_IDENTITY_MATCH_COUNT="
        f"{phase3b_verified + background_verified}"
    )
    print("PHASE3C_NORMALIZATION_STATUS=complete")
    print("PHASE3C_BACKGROUND_NORMALIZED_READY=true")
    print("PHASE3C_FULL_INGESTION_READY=true")
    print("PHASE3C_CHUNKING_AUTHORIZED=false")
    print("PHASE3C_BASELINE_AUTHORIZED=false")
    print("PHASE3C_RELEASE_ELIGIBLE=false")
    print(
        "PHASE3C_BACKGROUND_NORMALIZED_MANIFEST_SHA256="
        f"{manifest_sha}"
    )
    print(
        "PHASE3C_BACKGROUND_NORMALIZED_RECEIPT_SHA256="
        f"{receipt_sha}"
    )


if __name__ == "__main__":
    main()
