"""Semantic contract delta review for shared Phase 3A OpenAPI operations."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, cast

import yaml
from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.delta import Phase3aOperationDeltaReport
from rag_reliability.corpus.models import (
    AcquiredFileReceipt,
    AcquisitionReceipt,
    HttpMethod,
    OperationCatalogEntry,
    Phase3aOperationCatalogCandidate,
    SemanticOperationFamily,
)


class OperationContractDelta(ContractModel):
    operation_id: NonEmptyStr
    family: SemanticOperationFamily
    method: HttpMethod
    path: NonEmptyStr
    historical_contract_sha256: Sha256
    current_contract_sha256: Sha256
    changed_operation_fields: tuple[NonEmptyStr, ...]
    changed_path_item_fields: tuple[NonEmptyStr, ...]
    historical_only_ref_paths: tuple[NonEmptyStr, ...]
    current_only_ref_paths: tuple[NonEmptyStr, ...]
    changed_shared_ref_paths: tuple[NonEmptyStr, ...]
    direct_contract_changed: bool
    referenced_contract_changed: bool

    @model_validator(mode="after")
    def validate_change_flags(self) -> OperationContractDelta:
        direct = bool(self.changed_operation_fields or self.changed_path_item_fields)
        referenced = bool(
            self.historical_only_ref_paths
            or self.current_only_ref_paths
            or self.changed_shared_ref_paths
        )
        if self.direct_contract_changed != direct:
            raise ValueError("direct_contract_changed does not match field deltas")
        if self.referenced_contract_changed != referenced:
            raise ValueError("referenced_contract_changed does not match reference deltas")
        if not (direct or referenced):
            raise ValueError("operation contract delta must contain a real change")
        if self.historical_contract_sha256 == self.current_contract_sha256:
            raise ValueError("changed operation contracts must have different fingerprints")
        return self


class ContractDeltaFamilySummary(ContractModel):
    family: SemanticOperationFamily
    operation_count: int = Field(ge=0)
    changed_operation_count: int = Field(ge=0)
    direct_changed_count: int = Field(ge=0)
    referenced_only_changed_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_counts(self) -> ContractDeltaFamilySummary:
        if self.changed_operation_count != (
            self.direct_changed_count + self.referenced_only_changed_count
        ):
            raise ValueError("family contract-delta counts do not reconcile")
        if self.changed_operation_count > self.operation_count:
            raise ValueError("family changed count exceeds operation count")
        return self


class ChangedFieldFrequency(ContractModel):
    field_name: NonEmptyStr
    operation_count: int = Field(gt=0)


class Phase3aOperationContractDeltaReport(ContractModel):
    report_version: Literal["phase3a-operation-contract-delta-v1"] = (
        "phase3a-operation-contract-delta-v1"
    )
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_catalog_sha256: Sha256
    acquisition_receipt_sha256: Sha256
    identity_delta_sha256: Sha256
    selection_status: Literal["candidate_only"] = "candidate_only"
    ingestion_authorized: Literal[False] = False
    release_eligible: Literal[False] = False
    shared_operation_count: int = Field(ge=0)
    changed_operation_count: int = Field(ge=0)
    unchanged_operation_count: int = Field(ge=0)
    direct_changed_count: int = Field(ge=0)
    referenced_only_changed_count: int = Field(ge=0)
    changed_operations: tuple[OperationContractDelta, ...]
    family_summaries: tuple[ContractDeltaFamilySummary, ...] = Field(
        min_length=4,
        max_length=4,
    )
    changed_operation_field_frequency: tuple[ChangedFieldFrequency, ...]
    changed_path_item_field_frequency: tuple[ChangedFieldFrequency, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> Phase3aOperationContractDeltaReport:
        if self.shared_operation_count != (
            self.changed_operation_count + self.unchanged_operation_count
        ):
            raise ValueError("operation contract delta counts do not reconcile")
        if self.changed_operation_count != len(self.changed_operations):
            raise ValueError("changed operation count does not match result length")
        if self.changed_operation_count != (
            self.direct_changed_count + self.referenced_only_changed_count
        ):
            raise ValueError("direct/reference-only counts do not reconcile")
        family_total = sum(summary.operation_count for summary in self.family_summaries)
        if family_total != self.shared_operation_count:
            raise ValueError("family operation counts do not match shared total")
        family_changed = sum(
            summary.changed_operation_count for summary in self.family_summaries
        )
        if family_changed != self.changed_operation_count:
            raise ValueError("family changed counts do not match report total")
        return self


def _read_verified_json(path: Path) -> tuple[bytes, Sha256]:
    content = path.read_bytes()
    observed = hashlib.sha256(content).hexdigest()
    sidecar_path = path.with_suffix(path.suffix + ".sha256")
    parts = sidecar_path.read_text(encoding="utf-8").strip().split()
    if len(parts) != 2 or parts[1] != path.name:
        raise ValueError(f"malformed SHA-256 sidecar: {path.name}")
    if parts[0] != observed:
        raise ValueError(f"SHA-256 sidecar mismatch: {path.name}")
    return content, observed


def _as_mapping(value: object, *, label: str) -> Mapping[object, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _load_openapi(content: bytes) -> Mapping[object, object]:
    loaded = cast(object, yaml.safe_load(content.decode("utf-8")))
    document = _as_mapping(loaded, label="OpenAPI document")
    if document.get("openapi") != "3.0.3":
        raise ValueError("Phase 3A contract delta expects OpenAPI 3.0.3")
    return document


def _canonical_sha256(value: object) -> Sha256:
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _path_metadata(path_item: Mapping[object, object]) -> dict[str, object]:
    ignored = {"delete", "get", "head", "options", "patch", "post", "put", "trace"}
    metadata: dict[str, object] = {}
    for raw_key, value in path_item.items():
        if not isinstance(raw_key, str):
            raise ValueError("OpenAPI path-item keys must be strings")
        if raw_key in ignored:
            continue
        metadata[raw_key] = value
    return metadata


def _operation_body(
    document: Mapping[object, object],
    entry: OperationCatalogEntry,
) -> tuple[Mapping[object, object], dict[str, object]]:
    paths = _as_mapping(document.get("paths"), label="OpenAPI paths")
    path_item = _as_mapping(paths.get(entry.path), label=f"path item {entry.path}")
    operation = _as_mapping(
        path_item.get(entry.method),
        label=f"operation {entry.method.upper()} {entry.path}",
    )
    operation_id = operation.get("operationId")
    if operation_id != entry.operation_id:
        raise ValueError(f"operation identity mismatch for {entry.operation_id}")
    return operation, _path_metadata(path_item)


def _changed_mapping_keys(
    historical: Mapping[object, object] | Mapping[str, object],
    current: Mapping[object, object] | Mapping[str, object],
) -> tuple[str, ...]:
    keys: set[str] = set()
    for raw_key in set(historical) | set(current):
        if not isinstance(raw_key, str):
            raise ValueError("OpenAPI operation keys must be strings")
        if _canonical_sha256(historical.get(raw_key)) != _canonical_sha256(
            current.get(raw_key)
        ):
            keys.add(raw_key)
    return tuple(sorted(keys))


def _collect_local_refs(value: object) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for raw_key, child in value.items():
            if raw_key == "$ref" and isinstance(child, str) and child.startswith("#/"):
                refs.add(child)
            refs.update(_collect_local_refs(child))
        return refs
    if isinstance(value, list):
        for child in value:
            refs.update(_collect_local_refs(child))
    return refs


def _resolve_local_ref(document: Mapping[object, object], ref: str) -> object:
    if not ref.startswith("#/"):
        raise ValueError("only local OpenAPI references are supported")
    node: object = document
    for raw_token in ref[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        mapping = _as_mapping(node, label=f"OpenAPI reference segment {token}")
        if token not in mapping:
            raise ValueError(f"unresolved OpenAPI reference: {ref}")
        node = mapping[token]
    return node


def _reference_fingerprints(
    document: Mapping[object, object],
    seeds: tuple[object, ...],
) -> dict[str, Sha256]:
    pending: set[str] = set()
    for seed in seeds:
        pending.update(_collect_local_refs(seed))

    fingerprints: dict[str, Sha256] = {}
    while pending:
        ref = min(pending)
        pending.remove(ref)
        if ref in fingerprints:
            continue
        target = _resolve_local_ref(document, ref)
        fingerprints[ref] = _canonical_sha256(target)
        pending.update(_collect_local_refs(target) - set(fingerprints))
    return fingerprints


def _contract_fingerprint(
    operation: Mapping[object, object],
    path_metadata: Mapping[str, object],
    refs: Mapping[str, Sha256],
) -> Sha256:
    return _canonical_sha256(
        {
            "operation": operation,
            "path_metadata": path_metadata,
            "reference_fingerprints": dict(sorted(refs.items())),
        }
    )


def _build_delta(
    entry: OperationCatalogEntry,
    historical_document: Mapping[object, object],
    current_document: Mapping[object, object],
) -> OperationContractDelta | None:
    historical_operation, historical_path_metadata = _operation_body(
        historical_document,
        entry,
    )
    current_operation, current_path_metadata = _operation_body(current_document, entry)

    operation_fields = _changed_mapping_keys(historical_operation, current_operation)
    path_fields = _changed_mapping_keys(historical_path_metadata, current_path_metadata)

    historical_refs = _reference_fingerprints(
        historical_document,
        (historical_operation, historical_path_metadata),
    )
    current_refs = _reference_fingerprints(
        current_document,
        (current_operation, current_path_metadata),
    )
    historical_ref_paths = set(historical_refs)
    current_ref_paths = set(current_refs)
    historical_only_refs = tuple(sorted(historical_ref_paths - current_ref_paths))
    current_only_refs = tuple(sorted(current_ref_paths - historical_ref_paths))
    changed_shared_refs = tuple(
        sorted(
            ref
            for ref in historical_ref_paths & current_ref_paths
            if historical_refs[ref] != current_refs[ref]
        )
    )

    historical_fingerprint = _contract_fingerprint(
        historical_operation,
        historical_path_metadata,
        historical_refs,
    )
    current_fingerprint = _contract_fingerprint(
        current_operation,
        current_path_metadata,
        current_refs,
    )
    if historical_fingerprint == current_fingerprint:
        return None

    return OperationContractDelta(
        operation_id=entry.operation_id,
        family=entry.semantic_family_candidate,
        method=entry.method,
        path=entry.path,
        historical_contract_sha256=historical_fingerprint,
        current_contract_sha256=current_fingerprint,
        changed_operation_fields=operation_fields,
        changed_path_item_fields=path_fields,
        historical_only_ref_paths=historical_only_refs,
        current_only_ref_paths=current_only_refs,
        changed_shared_ref_paths=changed_shared_refs,
        direct_contract_changed=bool(operation_fields or path_fields),
        referenced_contract_changed=bool(
            historical_only_refs or current_only_refs or changed_shared_refs
        ),
    )


def _load_source_bytes(
    repo_root: Path,
    receipt: AcquisitionReceipt,
    source_id: str,
) -> bytes:
    matches = tuple(item for item in receipt.files if item.source_id == source_id)
    if len(matches) != 1:
        raise ValueError(f"acquisition receipt must contain exactly one {source_id}")
    item: AcquiredFileReceipt = matches[0]
    content = (repo_root / item.cache_path).read_bytes()
    if hashlib.sha256(content).hexdigest() != item.content_sha256:
        raise ValueError(f"cached source SHA-256 mismatch: {source_id}")
    return content


def _field_frequency(
    changes: tuple[OperationContractDelta, ...],
    attribute: Literal["changed_operation_fields", "changed_path_item_fields"],
) -> tuple[ChangedFieldFrequency, ...]:
    counter: Counter[str] = Counter()
    for change in changes:
        fields = (
            change.changed_operation_fields
            if attribute == "changed_operation_fields"
            else change.changed_path_item_fields
        )
        counter.update(fields)
    return tuple(
        ChangedFieldFrequency(field_name=name, operation_count=count)
        for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    )


def build_operation_contract_delta_report(
    repo_root: Path,
    catalog: Phase3aOperationCatalogCandidate,
    receipt: AcquisitionReceipt,
    identity_delta: Phase3aOperationDeltaReport,
    *,
    catalog_sha256: Sha256,
    receipt_sha256: Sha256,
    identity_delta_sha256: Sha256,
) -> Phase3aOperationContractDeltaReport:
    if (
        catalog.snapshot_id != receipt.snapshot_id
        or catalog.snapshot_id != identity_delta.snapshot_id
    ):
        raise ValueError("Phase 3A evidence snapshot IDs do not match")
    if identity_delta.source_catalog_sha256 != catalog_sha256:
        raise ValueError("identity delta is not bound to the supplied operation catalog")
    if identity_delta.current_only_operation_ids or identity_delta.historical_only_operation_ids:
        raise ValueError("contract delta requires fully shared operation membership")
    if identity_delta.shared_identity_changes:
        raise ValueError("contract delta requires stable shared operation identity")

    current_by_id = {item.operation_id: item for item in catalog.current.operations}
    historical_by_id = {item.operation_id: item for item in catalog.historical.operations}
    if set(current_by_id) != set(historical_by_id):
        raise ValueError("current and historical operation IDs must match")

    current_bytes = _load_source_bytes(repo_root, receipt, "openapi-current-2026-03-10")
    historical_bytes = _load_source_bytes(
        repo_root,
        receipt,
        "openapi-historical-2022-11-28",
    )
    current_document = _load_openapi(current_bytes)
    historical_document = _load_openapi(historical_bytes)

    changes: list[OperationContractDelta] = []
    for operation_id in sorted(current_by_id):
        current_entry = current_by_id[operation_id]
        historical_entry = historical_by_id[operation_id]
        current_identity = (
            current_entry.method,
            current_entry.path,
            current_entry.semantic_family_candidate,
        )
        historical_identity = (
            historical_entry.method,
            historical_entry.path,
            historical_entry.semantic_family_candidate,
        )
        if current_identity != historical_identity:
            raise ValueError(f"catalog identity mismatch for shared operation {operation_id}")
        change = _build_delta(current_entry, historical_document, current_document)
        if change is not None:
            changes.append(change)

    changed_operations = tuple(changes)
    families: tuple[SemanticOperationFamily, ...] = (
        "actions",
        "issues",
        "pull_requests",
        "repositories_and_repository_webhooks",
    )
    summaries: list[ContractDeltaFamilySummary] = []
    for family in families:
        family_entries = tuple(
            item
            for item in current_by_id.values()
            if item.semantic_family_candidate == family
        )
        family_changes = tuple(
            item for item in changed_operations if item.family == family
        )
        direct_changed = sum(1 for item in family_changes if item.direct_contract_changed)
        referenced_only = sum(
            1
            for item in family_changes
            if not item.direct_contract_changed and item.referenced_contract_changed
        )
        summaries.append(
            ContractDeltaFamilySummary(
                family=family,
                operation_count=len(family_entries),
                changed_operation_count=len(family_changes),
                direct_changed_count=direct_changed,
                referenced_only_changed_count=referenced_only,
            )
        )

    direct_changed_count = sum(
        1 for item in changed_operations if item.direct_contract_changed
    )
    referenced_only_changed_count = sum(
        1
        for item in changed_operations
        if not item.direct_contract_changed and item.referenced_contract_changed
    )
    shared_count = len(current_by_id)
    return Phase3aOperationContractDeltaReport(
        snapshot_id=catalog.snapshot_id,
        source_catalog_sha256=catalog_sha256,
        acquisition_receipt_sha256=receipt_sha256,
        identity_delta_sha256=identity_delta_sha256,
        shared_operation_count=shared_count,
        changed_operation_count=len(changed_operations),
        unchanged_operation_count=shared_count - len(changed_operations),
        direct_changed_count=direct_changed_count,
        referenced_only_changed_count=referenced_only_changed_count,
        changed_operations=changed_operations,
        family_summaries=tuple(summaries),
        changed_operation_field_frequency=_field_frequency(
            changed_operations,
            "changed_operation_fields",
        ),
        changed_path_item_field_frequency=_field_frequency(
            changed_operations,
            "changed_path_item_fields",
        ),
    )


def load_and_build_operation_contract_delta(
    repo_root: Path,
    *,
    catalog_path: Path,
    receipt_path: Path,
    identity_delta_path: Path,
) -> Phase3aOperationContractDeltaReport:
    catalog_bytes, catalog_sha = _read_verified_json(catalog_path)
    receipt_bytes, receipt_sha = _read_verified_json(receipt_path)
    identity_bytes, identity_sha = _read_verified_json(identity_delta_path)
    catalog = Phase3aOperationCatalogCandidate.model_validate_json(catalog_bytes)
    receipt = AcquisitionReceipt.model_validate_json(receipt_bytes)
    identity_delta = Phase3aOperationDeltaReport.model_validate_json(identity_bytes)
    return build_operation_contract_delta_report(
        repo_root,
        catalog,
        receipt,
        identity_delta,
        catalog_sha256=catalog_sha,
        receipt_sha256=receipt_sha,
        identity_delta_sha256=identity_sha,
    )
