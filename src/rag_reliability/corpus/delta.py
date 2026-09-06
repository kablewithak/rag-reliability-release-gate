"""Deterministic current-vs-historical operation delta review for Phase 3A."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import (
    HttpMethod,
    OperationCatalogEntry,
    Phase3aOperationCatalogCandidate,
    SemanticOperationFamily,
)


class OperationIdentityDelta(ContractModel):
    """Identity change for one operation present in both OpenAPI versions."""

    operation_id: NonEmptyStr
    historical_method: HttpMethod
    historical_path: NonEmptyStr
    historical_family: SemanticOperationFamily
    current_method: HttpMethod
    current_path: NonEmptyStr
    current_family: SemanticOperationFamily
    method_changed: bool
    path_changed: bool
    family_changed: bool

    @model_validator(mode="after")
    def validate_change_flags(self) -> OperationIdentityDelta:
        if self.method_changed != (self.historical_method != self.current_method):
            raise ValueError("method_changed does not match operation identity")
        if self.path_changed != (self.historical_path != self.current_path):
            raise ValueError("path_changed does not match operation identity")
        if self.family_changed != (self.historical_family != self.current_family):
            raise ValueError("family_changed does not match operation identity")
        if not (self.method_changed or self.path_changed or self.family_changed):
            raise ValueError("operation identity delta must contain a real change")
        return self


class OperationDeltaFamilySummary(ContractModel):
    family: SemanticOperationFamily
    current_only_count: int = Field(ge=0)
    historical_only_count: int = Field(ge=0)
    shared_identity_changed_count: int = Field(ge=0)


class Phase3aOperationDeltaReport(ContractModel):
    """Review artifact; never authorizes corpus ingestion by itself."""

    report_version: Literal["phase3a-operation-delta-v1"] = "phase3a-operation-delta-v1"
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_catalog_sha256: Sha256
    source_catalog_version: Literal["phase3a-operation-catalog-candidate-v1"]
    selection_status: Literal["candidate_only"] = "candidate_only"
    ingestion_authorized: Literal[False] = False
    release_eligible: Literal[False] = False
    current_operation_count: int = Field(ge=0)
    historical_operation_count: int = Field(ge=0)
    shared_operation_count: int = Field(ge=0)
    unchanged_shared_operation_count: int = Field(ge=0)
    current_only_operation_ids: tuple[NonEmptyStr, ...]
    historical_only_operation_ids: tuple[NonEmptyStr, ...]
    shared_identity_changes: tuple[OperationIdentityDelta, ...]
    family_summaries: tuple[OperationDeltaFamilySummary, ...] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_counts(self) -> Phase3aOperationDeltaReport:
        if self.current_operation_count != (
            self.shared_operation_count + len(self.current_only_operation_ids)
        ):
            raise ValueError("current operation delta counts do not reconcile")
        if self.historical_operation_count != (
            self.shared_operation_count + len(self.historical_only_operation_ids)
        ):
            raise ValueError("historical operation delta counts do not reconcile")
        if self.shared_operation_count != (
            self.unchanged_shared_operation_count + len(self.shared_identity_changes)
        ):
            raise ValueError("shared operation delta counts do not reconcile")
        families = tuple(item.family for item in self.family_summaries)
        expected = (
            "actions",
            "issues",
            "pull_requests",
            "repositories_and_repository_webhooks",
        )
        if families != expected:
            raise ValueError("operation delta family summaries must use canonical order")
        return self


def _read_expected_sidecar(catalog_path: Path) -> str:
    sidecar_path = catalog_path.with_suffix(catalog_path.suffix + ".sha256")
    line = sidecar_path.read_text(encoding="utf-8").strip()
    parts = line.split()
    if len(parts) != 2 or parts[1] != catalog_path.name:
        raise ValueError("operation catalog SHA-256 sidecar is malformed")
    return parts[0]


def _verified_catalog(catalog_path: Path) -> tuple[Phase3aOperationCatalogCandidate, Sha256]:
    content = catalog_path.read_bytes()
    observed_sha = hashlib.sha256(content).hexdigest()
    expected_sha = _read_expected_sidecar(catalog_path)
    if observed_sha != expected_sha:
        raise ValueError("operation catalog SHA-256 sidecar mismatch")
    catalog = Phase3aOperationCatalogCandidate.model_validate_json(content)
    if catalog.selection_status != "candidate_only":
        raise ValueError("delta review requires a candidate-only operation catalog")
    if catalog.ingestion_authorized or catalog.release_eligible:
        raise ValueError("delta review refuses an already-authorized or release-eligible catalog")
    return catalog, observed_sha


def _by_operation_id(
    operations: tuple[OperationCatalogEntry, ...],
) -> dict[str, OperationCatalogEntry]:
    return {operation.operation_id: operation for operation in operations}


def _family_summary(
    family: SemanticOperationFamily,
    *,
    current_only: tuple[OperationCatalogEntry, ...],
    historical_only: tuple[OperationCatalogEntry, ...],
    identity_changes: tuple[OperationIdentityDelta, ...],
) -> OperationDeltaFamilySummary:
    return OperationDeltaFamilySummary(
        family=family,
        current_only_count=sum(
            1 for operation in current_only if operation.semantic_family_candidate == family
        ),
        historical_only_count=sum(
            1 for operation in historical_only if operation.semantic_family_candidate == family
        ),
        shared_identity_changed_count=sum(
            1
            for change in identity_changes
            if change.current_family == family or change.historical_family == family
        ),
    )


def build_operation_delta_report(
    catalog: Phase3aOperationCatalogCandidate,
    *,
    source_catalog_sha256: Sha256,
) -> Phase3aOperationDeltaReport:
    current = _by_operation_id(catalog.current.operations)
    historical = _by_operation_id(catalog.historical.operations)
    current_ids = set(current)
    historical_ids = set(historical)
    shared_ids = current_ids & historical_ids

    current_only = tuple(current[item] for item in sorted(current_ids - historical_ids))
    historical_only = tuple(
        historical[item] for item in sorted(historical_ids - current_ids)
    )

    identity_changes: list[OperationIdentityDelta] = []
    for operation_id in sorted(shared_ids):
        current_item = current[operation_id]
        historical_item = historical[operation_id]
        method_changed = current_item.method != historical_item.method
        path_changed = current_item.path != historical_item.path
        family_changed = (
            current_item.semantic_family_candidate
            != historical_item.semantic_family_candidate
        )
        if not (method_changed or path_changed or family_changed):
            continue
        identity_changes.append(
            OperationIdentityDelta(
                operation_id=operation_id,
                historical_method=historical_item.method,
                historical_path=historical_item.path,
                historical_family=historical_item.semantic_family_candidate,
                current_method=current_item.method,
                current_path=current_item.path,
                current_family=current_item.semantic_family_candidate,
                method_changed=method_changed,
                path_changed=path_changed,
                family_changed=family_changed,
            )
        )

    changes = tuple(identity_changes)
    families: tuple[SemanticOperationFamily, ...] = (
        "actions",
        "issues",
        "pull_requests",
        "repositories_and_repository_webhooks",
    )
    summaries = tuple(
        _family_summary(
            family,
            current_only=current_only,
            historical_only=historical_only,
            identity_changes=changes,
        )
        for family in families
    )

    return Phase3aOperationDeltaReport(
        snapshot_id=catalog.snapshot_id,
        source_catalog_sha256=source_catalog_sha256,
        source_catalog_version=catalog.catalog_version,
        current_operation_count=len(current),
        historical_operation_count=len(historical),
        shared_operation_count=len(shared_ids),
        unchanged_shared_operation_count=len(shared_ids) - len(changes),
        current_only_operation_ids=tuple(item.operation_id for item in current_only),
        historical_only_operation_ids=tuple(item.operation_id for item in historical_only),
        shared_identity_changes=changes,
        family_summaries=summaries,
    )


def load_and_build_operation_delta(catalog_path: Path) -> Phase3aOperationDeltaReport:
    catalog, digest = _verified_catalog(catalog_path)
    return build_operation_delta_report(catalog, source_catalog_sha256=digest)
