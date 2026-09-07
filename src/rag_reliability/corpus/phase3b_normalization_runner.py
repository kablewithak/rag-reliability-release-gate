"""Materialize the file-backed Phase 3B normalized corpus slice."""

from __future__ import annotations

import argparse
import hashlib
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import AnyHttpUrl

from rag_reliability.contracts.corpus import RealSourceRecord
from rag_reliability.contracts.enums import CorpusSourceFamily, SourceState
from rag_reliability.corpus.acquisition import acquire_selection, raw_github_url
from rag_reliability.corpus.allowlist import Phase3aOperationAllowlist
from rag_reliability.corpus.models import (
    AcquisitionReceipt,
    CorpusSourceSelectionPlan,
    PinnedUpstreamFile,
    SemanticOperationFamily,
)
from rag_reliability.corpus.normalization import (
    index_openapi_operations,
    markdown_title,
    normalize_markdown,
    normalize_openapi_operation,
    write_exact_text,
)
from rag_reliability.corpus.normalized import (
    OPERATION_ALLOWLIST_SHA256,
    RENDERED_SOURCE_MANIFEST_SHA256,
    SOURCE_SELECTION_SHA256,
    NormalizedCorpusDocument,
    Phase3bNormalizedCorpusManifest,
    Phase3bNormalizedCorpusReceipt,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.corpus.rendered_source_freeze import (
    Phase3bRenderedSourceFreeze,
    rendered_source_manifest_path,
)

_EXPECTED_SELECTION_SHA256: Literal[
    "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
] = "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
_EXPECTED_RENDERED_MANIFEST_SHA256: Literal[
    "974c3ce722e30d630d09360cf115ac4679b2bf09797aa89a8f8af6e5549f5e7f"
] = "974c3ce722e30d630d09360cf115ac4679b2bf09797aa89a8f8af6e5549f5e7f"
_EXPECTED_ALLOWLIST_SHA256: Literal[
    "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"
] = "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"

_NORMALIZED_ROOT = Path("datasets/source_documents/normalized/phase3b_v1")
_NORMALIZED_MANIFEST = Path("datasets/source_manifests/phase3b_normalized_corpus_v1.json")


def _read_verified_json(path: Path) -> tuple[bytes, str]:
    content = path.read_bytes()
    observed = hashlib.sha256(content).hexdigest()
    sidecar = path.with_suffix(path.suffix + ".sha256")
    parts = sidecar.read_text(encoding="utf-8").strip().split()
    if len(parts) != 2 or parts[1] != path.name:
        raise ValueError(f"malformed SHA-256 sidecar: {path.name}")
    if parts[0] != observed:
        raise ValueError(f"SHA-256 sidecar mismatch: {path.name}")
    return content, observed


def _read_and_hash(path: Path) -> tuple[bytes, str]:
    content = path.read_bytes()
    return content, hashlib.sha256(content).hexdigest()


def _source_by_id(plan: CorpusSourceSelectionPlan) -> dict[str, PinnedUpstreamFile]:
    return {item.source_id: item for item in plan.files}


def _source_url(source: PinnedUpstreamFile) -> AnyHttpUrl:
    return AnyHttpUrl(raw_github_url(source))


def _topic_tags_for_authored(source: PinnedUpstreamFile) -> tuple[str, ...]:
    parent = Path(source.path).parent.name
    stem = Path(source.path).stem
    return ("rest-api", parent, stem)


def _build_authored_documents(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    rendered: Phase3bRenderedSourceFreeze,
    *,
    retrieved_at: datetime,
) -> list[NormalizedCorpusDocument]:
    sources = _source_by_id(plan)
    documents: list[NormalizedCorpusDocument] = []

    for record in rendered.documents:
        source = sources.get(record.source_id)
        if source is None or source.media_type != "markdown":
            raise ValueError(
                "rendered source is absent from authored selection: "
                f"{record.source_id}"
            )

        rendered_path = repo_root / record.rendered_path
        rendered_bytes = rendered_path.read_bytes()
        if hashlib.sha256(rendered_bytes).hexdigest() != record.rendered_content_sha256:
            raise ValueError(f"rendered source SHA-256 mismatch: {record.source_id}")

        rendered_text = rendered_bytes.decode("utf-8")
        normalized = normalize_markdown(rendered_text)
        relative = _NORMALIZED_ROOT / "authored" / f"{source.source_id}.md"
        digest, byte_count = write_exact_text(repo_root / relative, normalized)
        title = markdown_title(normalized, source.source_id)

        provenance = RealSourceRecord(
            source_id=source.source_id,
            source_family=CorpusSourceFamily.GITHUB_REST_AUTHORED_GUIDANCE,
            source_url=_source_url(source),
            source_license=source.source_license,
            retrieved_at=retrieved_at,
            source_commit_sha_or_version=source.commit_sha,
            document_version=source.api_version_or_snapshot,
            authority_level=source.authority_level,
            source_state=source.source_state,
            product_scope=source.product_scope,
            api_version_or_snapshot=source.api_version_or_snapshot,
            content_sha256=record.rendered_content_sha256,
            title=title,
            topic_tags=_topic_tags_for_authored(source),
            data_role=source.data_role,
        )
        documents.append(
            NormalizedCorpusDocument(
                document_id=f"authored-{source.source_id}",
                document_kind="authored_guidance",
                content_path=relative.as_posix(),
                normalized_content_sha256=digest,
                normalized_byte_count=byte_count,
                provenance=provenance,
            )
        )

    return documents


def _require_openapi_root(content: bytes, source_id: str) -> Mapping[str, Any]:
    loaded: object = yaml.safe_load(content)
    if not isinstance(loaded, Mapping):
        raise ValueError(f"OpenAPI source is not a mapping: {source_id}")
    return loaded


def _allowlist_family_map(
    allowlist: Phase3aOperationAllowlist,
) -> dict[str, SemanticOperationFamily]:
    observed: dict[str, SemanticOperationFamily] = {}
    for family in allowlist.families:
        for operation_id in family.operation_ids:
            if operation_id in observed:
                raise ValueError(f"duplicate allowlist operation ID: {operation_id}")
            observed[operation_id] = family.family
    if len(observed) != 20:
        raise ValueError("Phase 3B normalization requires exactly 20 allowlisted operations")
    return observed


def _state_path(source: PinnedUpstreamFile) -> Literal["current", "historical"]:
    if source.source_state is SourceState.CURRENT:
        return "current"
    if source.source_state is SourceState.HISTORICAL_COMPARISON:
        return "historical"
    raise ValueError(f"unsupported OpenAPI source state: {source.source_state}")


def _build_operation_documents(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    acquisition: AcquisitionReceipt,
    allowlist: Phase3aOperationAllowlist,
    *,
    retrieved_at: datetime,
) -> list[NormalizedCorpusDocument]:
    family_by_operation = _allowlist_family_map(allowlist)
    receipt_by_source = {item.source_id: item for item in acquisition.files}
    documents: list[NormalizedCorpusDocument] = []

    for source in plan.files:
        if source.media_type != "openapi_yaml":
            continue
        receipt = receipt_by_source.get(source.source_id)
        if receipt is None:
            raise ValueError(f"fresh acquisition is missing OpenAPI source: {source.source_id}")

        content = (repo_root / receipt.cache_path).read_bytes()
        if hashlib.sha256(content).hexdigest() != receipt.content_sha256:
            raise ValueError(f"fresh OpenAPI cache SHA-256 mismatch: {source.source_id}")
        root = _require_openapi_root(content, source.source_id)
        operation_index = index_openapi_operations(root)
        state_path = _state_path(source)

        for operation_id, family in sorted(family_by_operation.items()):
            identity = operation_index.get(operation_id)
            if identity is None:
                raise ValueError(
                    f"allowlisted operation missing from {source.api_version_or_snapshot}: "
                    f"{operation_id}"
                )
            path, method = identity
            normalized = normalize_openapi_operation(root, path, method)
            filename = operation_id.replace("/", "__") + ".json"
            relative = _NORMALIZED_ROOT / "openapi" / state_path / family / filename
            digest, byte_count = write_exact_text(repo_root / relative, normalized)

            provenance = RealSourceRecord(
                source_id=f"{source.source_id}:{operation_id}",
                source_family=CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT,
                source_url=_source_url(source),
                source_license=source.source_license,
                retrieved_at=retrieved_at,
                source_commit_sha_or_version=source.commit_sha,
                document_version=source.api_version_or_snapshot,
                authority_level=source.authority_level,
                source_state=source.source_state,
                product_scope=source.product_scope,
                api_version_or_snapshot=source.api_version_or_snapshot,
                content_sha256=receipt.content_sha256,
                title=operation_id,
                topic_tags=("rest-api", family),
                data_role=source.data_role,
            )
            documents.append(
                NormalizedCorpusDocument(
                    document_id=f"openapi-{state_path}-{operation_id.replace('/', '-')}",
                    document_kind="openapi_operation_contract",
                    content_path=relative.as_posix(),
                    normalized_content_sha256=digest,
                    normalized_byte_count=byte_count,
                    provenance=provenance,
                    semantic_family=family,
                    operation_id=operation_id,
                    method=method,
                    path=path,
                )
            )

    return documents


def _verify_materialized_files(repo_root: Path, manifest: Phase3bNormalizedCorpusManifest) -> None:
    for document in manifest.documents:
        content = (repo_root / document.content_path).read_bytes()
        observed_sha = hashlib.sha256(content).hexdigest()
        if observed_sha != document.normalized_content_sha256:
            raise ValueError(f"normalized file SHA-256 mismatch: {document.document_id}")
        if len(content) != document.normalized_byte_count:
            raise ValueError(f"normalized file byte-count mismatch: {document.document_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    artifacts = repo_root / "artifacts" / "development"

    selection_path = repo_root / "datasets/source_manifests/phase3a_source_selection_v1.json"
    selection_content, selection_sha = _read_and_hash(selection_path)
    if selection_sha != _EXPECTED_SELECTION_SHA256 or selection_sha != SOURCE_SELECTION_SHA256:
        raise ValueError("source selection hash does not match frozen Phase 3A evidence")
    plan = CorpusSourceSelectionPlan.model_validate_json(selection_content)

    rendered_content, rendered_sha = _read_verified_json(rendered_source_manifest_path(repo_root))
    if (
        rendered_sha != _EXPECTED_RENDERED_MANIFEST_SHA256
        or rendered_sha != RENDERED_SOURCE_MANIFEST_SHA256
    ):
        raise ValueError("rendered source manifest hash does not match accepted freeze")
    rendered = Phase3bRenderedSourceFreeze.model_validate_json(rendered_content)
    if not rendered.normalization_authorized:
        raise ValueError("rendered source freeze does not authorize normalization")

    allowlist_path = repo_root / "datasets/source_manifests/phase3a_operation_allowlist_v1.json"
    allowlist_content, allowlist_sha = _read_and_hash(allowlist_path)
    if allowlist_sha != _EXPECTED_ALLOWLIST_SHA256 or allowlist_sha != OPERATION_ALLOWLIST_SHA256:
        raise ValueError("operation allowlist hash does not match frozen Phase 3A evidence")
    allowlist = Phase3aOperationAllowlist.model_validate_json(allowlist_content)
    if not allowlist.ingestion_authorized:
        raise ValueError("operation allowlist does not authorize pinned-snapshot ingestion")

    retrieval_started_at = datetime.now(UTC)
    fresh_acquisition = acquire_selection(repo_root, plan)
    retrieval_completed_at = datetime.now(UTC)
    acquisition_path = artifacts / "phase3b_normalization_acquisition_receipt_v1.json"
    acquisition_sha = write_json_with_sha256(acquisition_path, fresh_acquisition)

    documents = _build_authored_documents(
        repo_root,
        plan,
        rendered,
        retrieved_at=retrieval_completed_at,
    )
    documents.extend(
        _build_operation_documents(
            repo_root,
            plan,
            fresh_acquisition,
            allowlist,
            retrieved_at=retrieval_completed_at,
        )
    )

    manifest = Phase3bNormalizedCorpusManifest(
        manifest_version="phase3b-normalized-corpus-manifest-v1",
        snapshot_id=plan.snapshot_id,
        source_selection_sha256=_EXPECTED_SELECTION_SHA256,
        source_rendered_manifest_sha256=_EXPECTED_RENDERED_MANIFEST_SHA256,
        operation_allowlist_sha256=_EXPECTED_ALLOWLIST_SHA256,
        source_acquisition_receipt_sha256=acquisition_sha,
        retrieved_at=retrieval_completed_at,
        documents=tuple(sorted(documents, key=lambda item: item.document_id)),
    )
    _verify_materialized_files(repo_root, manifest)

    manifest_path = repo_root / _NORMALIZED_MANIFEST
    manifest_sha = write_json_with_sha256(manifest_path, manifest)
    receipt = Phase3bNormalizedCorpusReceipt(
        receipt_version="phase3b-normalized-corpus-receipt-v1",
        source_selection_sha256=_EXPECTED_SELECTION_SHA256,
        source_rendered_manifest_sha256=_EXPECTED_RENDERED_MANIFEST_SHA256,
        operation_allowlist_sha256=_EXPECTED_ALLOWLIST_SHA256,
        source_acquisition_receipt_sha256=acquisition_sha,
        normalized_manifest_sha256=manifest_sha,
        retrieval_started_at=retrieval_started_at,
        retrieval_completed_at=retrieval_completed_at,
    )
    receipt_path = artifacts / "phase3b_normalized_corpus_receipt_v1.json"
    receipt_sha = write_json_with_sha256(receipt_path, receipt)

    print(f"PHASE3B_NORMALIZATION_SOURCE_SELECTION_SHA256={selection_sha}")
    print(f"PHASE3B_NORMALIZATION_SOURCE_RENDERED_SHA256={rendered_sha}")
    print(f"PHASE3B_NORMALIZATION_SOURCE_ALLOWLIST_SHA256={allowlist_sha}")
    print(f"PHASE3B_NORMALIZATION_ACQUISITION_SHA256={acquisition_sha}")
    print(f"PHASE3B_NORMALIZATION_RETRIEVED_AT={retrieval_completed_at.isoformat()}")
    print("PHASE3B_NORMALIZED_DOCUMENT_COUNT=50")
    print("PHASE3B_NORMALIZED_AUTHORED_DOCUMENT_COUNT=10")
    print("PHASE3B_NORMALIZED_CURRENT_OPERATION_COUNT=20")
    print("PHASE3B_NORMALIZED_HISTORICAL_OPERATION_COUNT=20")
    print("PHASE3B_NORMALIZED_FILE_IDENTITY_MATCH_COUNT=50")
    print("PHASE3B_NORMALIZATION_STATUS=complete")
    print("PHASE3B_NORMALIZED_CORPUS_READY=true")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_NORMALIZED_MANIFEST_SHA256={manifest_sha}")
    print(f"PHASE3B_NORMALIZED_RECEIPT_SHA256={receipt_sha}")


if __name__ == "__main__":
    main()
