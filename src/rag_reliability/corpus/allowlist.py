"""Frozen Phase 3A OpenAPI operation allowlist and ingestion authorization custody."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import SemanticOperationFamily
from rag_reliability.corpus.shortlist import Phase3aOperationShortlist

_FAMILY_ORDER: tuple[SemanticOperationFamily, ...] = (
    "actions",
    "issues",
    "pull_requests",
    "repositories_and_repository_webhooks",
)


class AllowlistFamily(ContractModel):
    family: SemanticOperationFamily
    operation_ids: tuple[NonEmptyStr, ...] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> AllowlistFamily:
        if len(self.operation_ids) != len(set(self.operation_ids)):
            raise ValueError("allowlist operation IDs must be unique within a family")
        return self


class Phase3aOperationAllowlist(ContractModel):
    allowlist_version: Literal["phase3a-operation-allowlist-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_shortlist_sha256: Sha256
    selection_status: Literal["frozen_allowlist"]
    ingestion_authorized: Literal[True]
    authorization_scope: Literal[
        "phase3_corpus_ingestion_from_pinned_snapshot_only"
    ]
    release_eligible: Literal[False]
    target_per_family: Literal[5]
    families: tuple[AllowlistFamily, ...] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_family_partition(self) -> Phase3aOperationAllowlist:
        observed_families = tuple(item.family for item in self.families)
        if observed_families != _FAMILY_ORDER:
            raise ValueError("allowlist families must use the frozen semantic-family order")
        all_ids = tuple(
            operation_id
            for family in self.families
            for operation_id in family.operation_ids
        )
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("allowlist operation IDs must be globally unique")
        return self

    @property
    def operation_count(self) -> int:
        return sum(len(item.operation_ids) for item in self.families)


class AllowlistFamilyCount(ContractModel):
    family: SemanticOperationFamily
    operation_count: Literal[5] = 5


class Phase3aIngestionAuthorizationReceipt(ContractModel):
    receipt_version: Literal["phase3a-ingestion-authorization-v1"] = (
        "phase3a-ingestion-authorization-v1"
    )
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_shortlist_sha256: Sha256
    operation_allowlist_sha256: Sha256
    selection_status: Literal["frozen_allowlist"] = "frozen_allowlist"
    ingestion_authorized: Literal[True] = True
    authorization_scope: Literal[
        "phase3_corpus_ingestion_from_pinned_snapshot_only"
    ] = "phase3_corpus_ingestion_from_pinned_snapshot_only"
    release_eligible: Literal[False] = False
    operation_count: Literal[20] = 20
    family_counts: tuple[AllowlistFamilyCount, ...] = Field(min_length=4, max_length=4)


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


def load_operation_allowlist(path: Path) -> tuple[Phase3aOperationAllowlist, Sha256]:
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    return Phase3aOperationAllowlist.model_validate_json(content), digest


def validate_allowlist_against_shortlist(
    allowlist: Phase3aOperationAllowlist,
    shortlist: Phase3aOperationShortlist,
    *,
    shortlist_sha256: Sha256,
) -> None:
    if allowlist.source_shortlist_sha256 != shortlist_sha256:
        raise ValueError("allowlist source shortlist hash does not match observed shortlist")
    if allowlist.snapshot_id != shortlist.snapshot_id:
        raise ValueError("allowlist snapshot does not match shortlist snapshot")

    shortlist_by_family = {
        family: tuple(
            item.operation_id for item in shortlist.items if item.family == family
        )
        for family in _FAMILY_ORDER
    }
    allowlist_by_family = {
        item.family: item.operation_ids for item in allowlist.families
    }
    if allowlist_by_family != shortlist_by_family:
        raise ValueError("frozen allowlist must exactly match the reviewed shortlist")


def build_ingestion_authorization_receipt(
    allowlist: Phase3aOperationAllowlist,
    *,
    allowlist_sha256: Sha256,
) -> Phase3aIngestionAuthorizationReceipt:
    return Phase3aIngestionAuthorizationReceipt(
        snapshot_id=allowlist.snapshot_id,
        source_shortlist_sha256=allowlist.source_shortlist_sha256,
        operation_allowlist_sha256=allowlist_sha256,
        family_counts=tuple(
            AllowlistFamilyCount(family=item.family) for item in allowlist.families
        ),
    )


def authorize_frozen_allowlist(
    shortlist_path: Path,
    allowlist_path: Path,
) -> Phase3aIngestionAuthorizationReceipt:
    shortlist_content, shortlist_sha = _read_verified_json(shortlist_path)
    shortlist = Phase3aOperationShortlist.model_validate_json(shortlist_content)
    allowlist, allowlist_sha = load_operation_allowlist(allowlist_path)
    validate_allowlist_against_shortlist(
        allowlist,
        shortlist,
        shortlist_sha256=shortlist_sha,
    )
    return build_ingestion_authorization_receipt(
        allowlist,
        allowlist_sha256=allowlist_sha,
    )
