"""Deterministic selection worksheet for Phase 3A changed OpenAPI operations."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import HttpMethod, SemanticOperationFamily
from rag_reliability.corpus.review_matrix import (
    OperationContractReviewItem,
    Phase3aContractChangeReview,
)

SelectionTier = Literal["tier_a_direct", "tier_b_substantive_reference", "tier_c_example_only"]

_SUBSTANTIVE_REFERENCE_CLASSES = frozenset(
    {
        "schemas",
        "parameters",
        "responses",
        "request_bodies",
        "headers",
        "security_schemes",
        "callbacks",
        "links",
        "other",
    }
)


class OperationSelectionReviewItem(ContractModel):
    operation_id: NonEmptyStr
    family: SemanticOperationFamily
    method: HttpMethod
    path: NonEmptyStr
    selection_tier: SelectionTier
    change_mode: Literal["direct_only", "direct_and_referenced", "referenced_only"]
    direct_change_categories: tuple[NonEmptyStr, ...]
    reference_component_classes: tuple[NonEmptyStr, ...]
    substantive_reference_change: bool
    example_reference_change: bool

    @model_validator(mode="after")
    def validate_tier(self) -> OperationSelectionReviewItem:
        direct = self.change_mode in {"direct_only", "direct_and_referenced"}
        if direct and self.selection_tier != "tier_a_direct":
            raise ValueError("direct contract change must be Tier A")
        if not direct and self.substantive_reference_change:
            if self.selection_tier != "tier_b_substantive_reference":
                raise ValueError("substantive referenced change must be Tier B")
        if not direct and not self.substantive_reference_change:
            if self.selection_tier != "tier_c_example_only":
                raise ValueError("example-only referenced change must be Tier C")
        return self


class SelectionTierCount(ContractModel):
    tier: SelectionTier
    count: int = Field(ge=0)


class SelectionFamilyTierCount(ContractModel):
    family: SemanticOperationFamily
    tier_a_direct: int = Field(ge=0)
    tier_b_substantive_reference: int = Field(ge=0)
    tier_c_example_only: int = Field(ge=0)

    @property
    def total_count(self) -> int:
        return self.tier_a_direct + self.tier_b_substantive_reference + self.tier_c_example_only


class Phase3aOperationSelectionReview(ContractModel):
    report_version: Literal["phase3a-operation-selection-review-v1"] = (
        "phase3a-operation-selection-review-v1"
    )
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_contract_change_review_sha256: Sha256
    review_status: Literal["selection_review"] = "selection_review"
    selection_status: Literal["candidate_only"] = "candidate_only"
    ingestion_authorized: Literal[False] = False
    release_eligible: Literal[False] = False
    changed_operation_count: int = Field(ge=0)
    items: tuple[OperationSelectionReviewItem, ...]
    tier_counts: tuple[SelectionTierCount, ...] = Field(min_length=3, max_length=3)
    family_tier_counts: tuple[SelectionFamilyTierCount, ...] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_counts(self) -> Phase3aOperationSelectionReview:
        if len(self.items) != self.changed_operation_count:
            raise ValueError("selection review item count does not reconcile")
        if sum(item.count for item in self.tier_counts) != self.changed_operation_count:
            raise ValueError("selection tier counts do not reconcile")
        family_total = sum(item.total_count for item in self.family_tier_counts)
        if family_total != self.changed_operation_count:
            raise ValueError("family tier counts do not reconcile")
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


def _reference_classes(item: OperationContractReviewItem) -> tuple[str, ...]:
    return tuple(sorted(summary.component_class for summary in item.reference_change_summaries))


def _selection_tier(item: OperationContractReviewItem) -> SelectionTier:
    if item.change_mode in {"direct_only", "direct_and_referenced"}:
        return "tier_a_direct"
    substantive = any(
        summary.component_class in _SUBSTANTIVE_REFERENCE_CLASSES
        and summary.total_count > 0
        for summary in item.reference_change_summaries
    )
    if substantive:
        return "tier_b_substantive_reference"
    return "tier_c_example_only"


def _selection_item(item: OperationContractReviewItem) -> OperationSelectionReviewItem:
    reference_classes = _reference_classes(item)
    substantive = any(name in _SUBSTANTIVE_REFERENCE_CLASSES for name in reference_classes)
    return OperationSelectionReviewItem(
        operation_id=item.operation_id,
        family=item.family,
        method=item.method,
        path=item.path,
        selection_tier=_selection_tier(item),
        change_mode=item.change_mode,
        direct_change_categories=tuple(item.direct_change_categories),
        reference_component_classes=reference_classes,
        substantive_reference_change=substantive,
        example_reference_change="examples" in reference_classes,
    )


def build_operation_selection_review(
    review: Phase3aContractChangeReview,
    *,
    review_sha256: Sha256,
) -> Phase3aOperationSelectionReview:
    items = tuple(_selection_item(item) for item in review.review_items)
    tier_counter = Counter(item.selection_tier for item in items)
    tier_order: tuple[SelectionTier, ...] = (
        "tier_a_direct",
        "tier_b_substantive_reference",
        "tier_c_example_only",
    )
    tier_counts = tuple(
        SelectionTierCount(tier=tier, count=tier_counter[tier]) for tier in tier_order
    )

    family_order: tuple[SemanticOperationFamily, ...] = (
        "actions",
        "issues",
        "pull_requests",
        "repositories_and_repository_webhooks",
    )
    family_tier_counts = tuple(
        SelectionFamilyTierCount(
            family=family,
            tier_a_direct=sum(
                1
                for item in items
                if item.family == family and item.selection_tier == "tier_a_direct"
            ),
            tier_b_substantive_reference=sum(
                1
                for item in items
                if item.family == family
                and item.selection_tier == "tier_b_substantive_reference"
            ),
            tier_c_example_only=sum(
                1
                for item in items
                if item.family == family and item.selection_tier == "tier_c_example_only"
            ),
        )
        for family in family_order
    )
    return Phase3aOperationSelectionReview(
        snapshot_id=review.snapshot_id,
        source_contract_change_review_sha256=review_sha256,
        changed_operation_count=len(items),
        items=items,
        tier_counts=tier_counts,
        family_tier_counts=family_tier_counts,
    )


def load_and_build_operation_selection_review(
    review_path: Path,
) -> Phase3aOperationSelectionReview:
    content, digest = _read_verified_json(review_path)
    review = Phase3aContractChangeReview.model_validate_json(content)
    return build_operation_selection_review(review, review_sha256=digest)
