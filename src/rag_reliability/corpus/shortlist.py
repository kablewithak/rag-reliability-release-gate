"""Balanced review shortlist for Phase 3A OpenAPI operation selection."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import HttpMethod, SemanticOperationFamily
from rag_reliability.corpus.selection_review import (
    OperationSelectionReviewItem,
    Phase3aOperationSelectionReview,
    SelectionTier,
)

ShortlistReason = Literal[
    "mandatory_direct_change",
    "family_balance_substantive_reference",
]

_FAMILY_ORDER: tuple[SemanticOperationFamily, ...] = (
    "actions",
    "issues",
    "pull_requests",
    "repositories_and_repository_webhooks",
)
_SUBSTANTIVE_CLASS_ORDER = (
    "responses",
    "request_bodies",
    "parameters",
    "schemas",
    "headers",
    "security_schemes",
    "callbacks",
    "links",
    "other",
)


class OperationShortlistItem(ContractModel):
    operation_id: NonEmptyStr
    family: SemanticOperationFamily
    method: HttpMethod
    path: NonEmptyStr
    selection_tier: SelectionTier
    shortlist_reason: ShortlistReason
    direct_change_categories: tuple[NonEmptyStr, ...]
    reference_component_classes: tuple[NonEmptyStr, ...]

    @model_validator(mode="after")
    def validate_reason(self) -> OperationShortlistItem:
        if self.shortlist_reason == "mandatory_direct_change":
            if self.selection_tier != "tier_a_direct":
                raise ValueError("mandatory direct shortlist item must be Tier A")
        if self.shortlist_reason == "family_balance_substantive_reference":
            if self.selection_tier != "tier_b_substantive_reference":
                raise ValueError("family-balance shortlist item must be Tier B")
        return self


class ShortlistFamilyCount(ContractModel):
    family: SemanticOperationFamily
    selected_count: int = Field(ge=0)
    tier_a_direct_count: int = Field(ge=0)
    tier_b_substantive_reference_count: int = Field(ge=0)


class Phase3aOperationShortlist(ContractModel):
    report_version: Literal["phase3a-operation-shortlist-v1"] = (
        "phase3a-operation-shortlist-v1"
    )
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_selection_review_sha256: Sha256
    review_status: Literal["shortlist_review"] = "shortlist_review"
    selection_status: Literal["candidate_only"] = "candidate_only"
    ingestion_authorized: Literal[False] = False
    release_eligible: Literal[False] = False
    target_per_family: Literal[5] = 5
    shortlist_count: int = Field(ge=0)
    items: tuple[OperationShortlistItem, ...]
    family_counts: tuple[ShortlistFamilyCount, ...] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_counts(self) -> Phase3aOperationShortlist:
        if len(self.items) != self.shortlist_count:
            raise ValueError("shortlist item count does not reconcile")
        if sum(item.selected_count for item in self.family_counts) != self.shortlist_count:
            raise ValueError("shortlist family counts do not reconcile")
        for item in self.family_counts:
            if item.selected_count != self.target_per_family:
                raise ValueError("every shortlist family must meet the target count")
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


def _class_presence_key(item: OperationSelectionReviewItem) -> tuple[int, ...]:
    classes = set(item.reference_component_classes)
    presence = tuple(0 if name in classes else 1 for name in _SUBSTANTIVE_CLASS_ORDER)
    return (*presence, -len(classes))


def _tier_b_sort_key(
    item: OperationSelectionReviewItem,
) -> tuple[tuple[int, ...], str]:
    return (_class_presence_key(item), item.operation_id)


def _to_shortlist_item(
    item: OperationSelectionReviewItem,
    reason: ShortlistReason,
) -> OperationShortlistItem:
    return OperationShortlistItem(
        operation_id=item.operation_id,
        family=item.family,
        method=item.method,
        path=item.path,
        selection_tier=item.selection_tier,
        shortlist_reason=reason,
        direct_change_categories=item.direct_change_categories,
        reference_component_classes=item.reference_component_classes,
    )


def build_operation_shortlist(
    review: Phase3aOperationSelectionReview,
    *,
    review_sha256: Sha256,
) -> Phase3aOperationShortlist:
    target_per_family = 5
    selected: list[OperationShortlistItem] = []
    family_counts: list[ShortlistFamilyCount] = []

    for family in _FAMILY_ORDER:
        family_items = tuple(item for item in review.items if item.family == family)
        tier_a = tuple(
            sorted(
                (item for item in family_items if item.selection_tier == "tier_a_direct"),
                key=lambda item: item.operation_id,
            )
        )
        if len(tier_a) > target_per_family:
            raise ValueError(f"Tier A count exceeds shortlist target for family {family}")

        needed = target_per_family - len(tier_a)
        tier_b = tuple(
            sorted(
                (
                    item
                    for item in family_items
                    if item.selection_tier == "tier_b_substantive_reference"
                ),
                key=_tier_b_sort_key,
            )
        )
        if len(tier_b) < needed:
            raise ValueError(f"insufficient Tier B candidates for family {family}")

        selected_a = tuple(
            _to_shortlist_item(item, "mandatory_direct_change") for item in tier_a
        )
        selected_b = tuple(
            _to_shortlist_item(item, "family_balance_substantive_reference")
            for item in tier_b[:needed]
        )
        selected.extend((*selected_a, *selected_b))
        family_counts.append(
            ShortlistFamilyCount(
                family=family,
                selected_count=len(selected_a) + len(selected_b),
                tier_a_direct_count=len(selected_a),
                tier_b_substantive_reference_count=len(selected_b),
            )
        )

    return Phase3aOperationShortlist(
        snapshot_id=review.snapshot_id,
        source_selection_review_sha256=review_sha256,
        shortlist_count=len(selected),
        items=tuple(selected),
        family_counts=tuple(family_counts),
    )


def load_and_build_operation_shortlist(
    review_path: Path,
) -> Phase3aOperationShortlist:
    content, digest = _read_verified_json(review_path)
    review = Phase3aOperationSelectionReview.model_validate_json(content)
    return build_operation_shortlist(review, review_sha256=digest)
