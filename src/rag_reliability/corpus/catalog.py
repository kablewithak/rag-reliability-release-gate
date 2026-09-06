"""Operation catalog generation from pinned GitHub bundled OpenAPI YAML."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import yaml

from rag_reliability.corpus.models import (
    AcquiredFileReceipt,
    ApiVersionOperationCatalog,
    HttpMethod,
    OperationCatalogEntry,
    Phase3aOperationCatalogCandidate,
    SemanticOperationFamily,
)

_HTTP_METHODS: tuple[HttpMethod, ...] = (
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "trace",
)
_PREFIX_TO_FAMILY: tuple[tuple[str, SemanticOperationFamily], ...] = (
    ("issues/", "issues"),
    ("pulls/", "pull_requests"),
    ("repos/", "repositories_and_repository_webhooks"),
    ("actions/", "actions"),
)


def _as_mapping(value: object, *, label: str) -> Mapping[object, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _as_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _as_tags(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("OpenAPI operation tags must be a list")
    tags: list[str] = []
    for item in value:
        tags.append(_as_string(item, label="OpenAPI operation tag"))
    return tuple(tags)


def _candidate_family(operation_id: str) -> SemanticOperationFamily | None:
    for prefix, family in _PREFIX_TO_FAMILY:
        if operation_id.startswith(prefix):
            return family
    return None


def parse_candidate_operations(openapi_bytes: bytes) -> tuple[OperationCatalogEntry, ...]:
    loaded = cast(object, yaml.safe_load(openapi_bytes.decode("utf-8")))
    document = _as_mapping(loaded, label="OpenAPI document")
    version = document.get("openapi")
    if version != "3.0.3":
        raise ValueError("Phase 3A expects the frozen GitHub OpenAPI 3.0.3 format")

    paths = _as_mapping(document.get("paths"), label="OpenAPI paths")
    operations: list[OperationCatalogEntry] = []

    for raw_path, raw_path_item in paths.items():
        path = _as_string(raw_path, label="OpenAPI path")
        path_item = _as_mapping(raw_path_item, label=f"OpenAPI path item {path}")
        for method in _HTTP_METHODS:
            raw_operation = path_item.get(method)
            if raw_operation is None:
                continue
            operation = _as_mapping(
                raw_operation,
                label=f"OpenAPI operation {method.upper()} {path}",
            )
            operation_id = _as_string(
                operation.get("operationId"),
                label=f"operationId for {method.upper()} {path}",
            )
            family = _candidate_family(operation_id)
            if family is None:
                continue
            operations.append(
                OperationCatalogEntry(
                    operation_id=operation_id,
                    method=method,
                    path=path,
                    tags=_as_tags(operation.get("tags")),
                    semantic_family_candidate=family,
                )
            )

    return tuple(sorted(operations, key=lambda item: item.operation_id))


def build_operation_catalog(
    current_receipt: AcquiredFileReceipt,
    current_bytes: bytes,
    historical_receipt: AcquiredFileReceipt,
    historical_bytes: bytes,
) -> Phase3aOperationCatalogCandidate:
    return Phase3aOperationCatalogCandidate(
        catalog_version="phase3a-operation-catalog-candidate-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        current=ApiVersionOperationCatalog(
            api_version="2026-03-10",
            source_id=current_receipt.source_id,
            source_git_blob_sha1=current_receipt.observed_git_blob_sha1,
            operations=parse_candidate_operations(current_bytes),
        ),
        historical=ApiVersionOperationCatalog(
            api_version="2022-11-28",
            source_id=historical_receipt.source_id,
            source_git_blob_sha1=historical_receipt.observed_git_blob_sha1,
            operations=parse_candidate_operations(historical_bytes),
        ),
    )
