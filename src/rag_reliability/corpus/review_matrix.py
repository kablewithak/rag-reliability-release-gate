"""Deterministic review matrix for Phase 3A OpenAPI contract changes."""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.contract_delta import (
    OperationContractDelta,
    Phase3aOperationContractDeltaReport,
)
from rag_reliability.corpus.models import HttpMethod, SemanticOperationFamily

ChangeMode = Literal["direct_only", "direct_and_referenced", "referenced_only"]
DirectChangeCategory = Literal[
    "description_or_summary",
    "parameters",
    "request_body",
    "responses",
    "security",
    "github_metadata",
    "deprecation",
    "external_docs",
    "other",
]
ReferenceComponentClass = Literal[
    "schemas",
    "parameters",
    "responses",
    "request_bodies",
    "headers",
    "security_schemes",
    "examples",
    "callbacks",
    "links",
    "other",
]


class ReferenceChangeSummary(ContractModel):
    component_class: ReferenceComponentClass
    historical_only_count: int = Field(ge=0)
    current_only_count: int = Field(ge=0)
    changed_shared_count: int = Field(ge=0)

    @property
    def total_count(self) -> int:
        return self.historical_only_count + self.current_only_count + self.changed_shared_count


class OperationContractReviewItem(ContractModel):
    operation_id: NonEmptyStr
    family: SemanticOperationFamily
    method: HttpMethod
    path: NonEmptyStr
    change_mode: ChangeMode
    changed_operation_fields: tuple[NonEmptyStr, ...]
    changed_path_item_fields: tuple[NonEmptyStr, ...]
    direct_change_categories: tuple[DirectChangeCategory, ...]
    reference_change_summaries: tuple[ReferenceChangeSummary, ...]
    historical_contract_sha256: Sha256
    current_contract_sha256: Sha256

    @model_validator(mode="after")
    def validate_change_mode(self) -> OperationContractReviewItem:
        direct = bool(self.changed_operation_fields or self.changed_path_item_fields)
        referenced = any(summary.total_count > 0 for summary in self.reference_change_summaries)
        expected: ChangeMode
        if direct and referenced:
            expected = "direct_and_referenced"
        elif direct:
            expected = "direct_only"
        else:
            expected = "referenced_only"
        if self.change_mode != expected:
            raise ValueError("review change_mode does not match observed change evidence")
        if direct != bool(self.direct_change_categories):
            raise ValueError("direct change categories do not match direct change evidence")
        if not (direct or referenced):
            raise ValueError("review item must contain contract change evidence")
        return self


class ReviewFamilySummary(ContractModel):
    family: SemanticOperationFamily
    changed_operation_count: int = Field(ge=0)
    direct_only_count: int = Field(ge=0)
    direct_and_referenced_count: int = Field(ge=0)
    referenced_only_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_counts(self) -> ReviewFamilySummary:
        if self.changed_operation_count != (
            self.direct_only_count
            + self.direct_and_referenced_count
            + self.referenced_only_count
        ):
            raise ValueError("family review counts do not reconcile")
        return self


class NamedCount(ContractModel):
    name: NonEmptyStr
    count: int = Field(gt=0)


class Phase3aContractChangeReview(ContractModel):
    report_version: Literal["phase3a-contract-change-review-v1"] = (
        "phase3a-contract-change-review-v1"
    )
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_contract_delta_sha256: Sha256
    review_status: Literal["candidate_review"] = "candidate_review"
    selection_status: Literal["candidate_only"] = "candidate_only"
    ingestion_authorized: Literal[False] = False
    release_eligible: Literal[False] = False
    changed_operation_count: int = Field(ge=0)
    review_items: tuple[OperationContractReviewItem, ...]
    family_summaries: tuple[ReviewFamilySummary, ...] = Field(min_length=4, max_length=4)
    change_mode_counts: tuple[NamedCount, ...]
    direct_category_counts: tuple[NamedCount, ...]
    reference_component_class_counts: tuple[NamedCount, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> Phase3aContractChangeReview:
        if self.changed_operation_count != len(self.review_items):
            raise ValueError("review item count does not match changed_operation_count")
        if sum(item.changed_operation_count for item in self.family_summaries) != (
            self.changed_operation_count
        ):
            raise ValueError("family review counts do not match changed_operation_count")
        if sum(item.count for item in self.change_mode_counts) != self.changed_operation_count:
            raise ValueError("change mode counts do not match changed_operation_count")
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


def _direct_category(field_name: str) -> DirectChangeCategory:
    mapping: dict[str, DirectChangeCategory] = {
        "description": "description_or_summary",
        "summary": "description_or_summary",
        "parameters": "parameters",
        "requestBody": "request_body",
        "responses": "responses",
        "security": "security",
        "x-github": "github_metadata",
        "deprecated": "deprecation",
        "externalDocs": "external_docs",
    }
    return mapping.get(field_name, "other")


def _direct_categories(change: OperationContractDelta) -> tuple[DirectChangeCategory, ...]:
    categories = {
        _direct_category(field)
        for field in (*change.changed_operation_fields, *change.changed_path_item_fields)
    }
    return tuple(sorted(categories))


def _reference_component_class(ref_path: str) -> ReferenceComponentClass:
    prefixes: tuple[tuple[str, ReferenceComponentClass], ...] = (
        ("#/components/schemas/", "schemas"),
        ("#/components/parameters/", "parameters"),
        ("#/components/responses/", "responses"),
        ("#/components/requestBodies/", "request_bodies"),
        ("#/components/headers/", "headers"),
        ("#/components/securitySchemes/", "security_schemes"),
        ("#/components/examples/", "examples"),
        ("#/components/callbacks/", "callbacks"),
        ("#/components/links/", "links"),
    )
    for prefix, component_class in prefixes:
        if ref_path.startswith(prefix):
            return component_class
    return "other"


def _reference_summaries(change: OperationContractDelta) -> tuple[ReferenceChangeSummary, ...]:
    historical: Counter[ReferenceComponentClass] = Counter(
        _reference_component_class(path) for path in change.historical_only_ref_paths
    )
    current: Counter[ReferenceComponentClass] = Counter(
        _reference_component_class(path) for path in change.current_only_ref_paths
    )
    shared: Counter[ReferenceComponentClass] = Counter(
        _reference_component_class(path) for path in change.changed_shared_ref_paths
    )
    classes = sorted(set(historical) | set(current) | set(shared))
    return tuple(
        ReferenceChangeSummary(
            component_class=component_class,
            historical_only_count=historical[component_class],
            current_only_count=current[component_class],
            changed_shared_count=shared[component_class],
        )
        for component_class in classes
    )


def _change_mode(change: OperationContractDelta) -> ChangeMode:
    if change.direct_contract_changed and change.referenced_contract_changed:
        return "direct_and_referenced"
    if change.direct_contract_changed:
        return "direct_only"
    return "referenced_only"


def _review_item(change: OperationContractDelta) -> OperationContractReviewItem:
    return OperationContractReviewItem(
        operation_id=change.operation_id,
        family=change.family,
        method=change.method,
        path=change.path,
        change_mode=_change_mode(change),
        changed_operation_fields=change.changed_operation_fields,
        changed_path_item_fields=change.changed_path_item_fields,
        direct_change_categories=_direct_categories(change),
        reference_change_summaries=_reference_summaries(change),
        historical_contract_sha256=change.historical_contract_sha256,
        current_contract_sha256=change.current_contract_sha256,
    )


def _named_counts(values: Iterable[str]) -> tuple[NamedCount, ...]:
    counter = Counter(values)
    return tuple(
        NamedCount(name=name, count=count)
        for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    )


def build_contract_change_review(
    contract_delta: Phase3aOperationContractDeltaReport,
    *,
    contract_delta_sha256: Sha256,
) -> Phase3aContractChangeReview:
    review_items = tuple(_review_item(change) for change in contract_delta.changed_operations)
    families: tuple[SemanticOperationFamily, ...] = (
        "actions",
        "issues",
        "pull_requests",
        "repositories_and_repository_webhooks",
    )
    family_summaries: list[ReviewFamilySummary] = []
    for family in families:
        items = tuple(item for item in review_items if item.family == family)
        family_summaries.append(
            ReviewFamilySummary(
                family=family,
                changed_operation_count=len(items),
                direct_only_count=sum(1 for item in items if item.change_mode == "direct_only"),
                direct_and_referenced_count=sum(
                    1 for item in items if item.change_mode == "direct_and_referenced"
                ),
                referenced_only_count=sum(
                    1 for item in items if item.change_mode == "referenced_only"
                ),
            )
        )

    modes = [item.change_mode for item in review_items]
    direct_categories = [
        category for item in review_items for category in item.direct_change_categories
    ]
    component_classes = [
        summary.component_class
        for item in review_items
        for summary in item.reference_change_summaries
        for _ in range(summary.total_count)
    ]
    return Phase3aContractChangeReview(
        snapshot_id=contract_delta.snapshot_id,
        source_contract_delta_sha256=contract_delta_sha256,
        changed_operation_count=len(review_items),
        review_items=review_items,
        family_summaries=tuple(family_summaries),
        change_mode_counts=_named_counts(modes),
        direct_category_counts=_named_counts(direct_categories),
        reference_component_class_counts=_named_counts(component_classes),
    )


def load_and_build_contract_change_review(
    contract_delta_path: Path,
) -> Phase3aContractChangeReview:
    content, digest = _read_verified_json(contract_delta_path)
    contract_delta = Phase3aOperationContractDeltaReport.model_validate_json(content)
    return build_contract_change_review(contract_delta, contract_delta_sha256=digest)
