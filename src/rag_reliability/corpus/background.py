"""Frozen Phase 3C real background-load corpus selection contract."""

from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import AuthorityLevel, DataRole, SourceState
from rag_reliability.corpus.allowlist import Phase3aOperationAllowlist
from rag_reliability.corpus.models import (
    HttpMethod,
    Phase3aOperationCatalogCandidate,
    SemanticOperationFamily,
)

SOURCE_CATALOG_SHA256: Literal[
    "d16fe4774dedef38e96cb021e4ebe03b50e4d8eda9b1fcc679318f6425251fe0"
] = "d16fe4774dedef38e96cb021e4ebe03b50e4d8eda9b1fcc679318f6425251fe0"

OPERATION_ALLOWLIST_SHA256: Literal[
    "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"
] = "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"

_FAMILY_ORDER: tuple[SemanticOperationFamily, ...] = (
    "actions",
    "issues",
    "pull_requests",
    "repositories_and_repository_webhooks",
)

_EXPECTED_FAMILY_COUNTS: tuple[tuple[SemanticOperationFamily, int], ...] = (
    ("actions", 184),
    ("issues", 53),
    ("pull_requests", 24),
    ("repositories_and_repository_webhooks", 198),
)


class BackgroundOperationSelection(ContractModel):
    """One current authoritative OpenAPI operation selected for background load."""

    operation_id: NonEmptyStr
    family: SemanticOperationFamily
    method: HttpMethod
    path: NonEmptyStr


class BackgroundFamilyCount(ContractModel):
    family: SemanticOperationFamily
    selected_count: int = Field(gt=0)


class Phase3cBackgroundSelectionManifest(ContractModel):
    """Hash-bound selection boundary for Phase 3C background normalization."""

    manifest_version: Literal["phase3c-background-selection-v1"] = (
        "phase3c-background-selection-v1"
    )
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_catalog_sha256: Literal[
        "d16fe4774dedef38e96cb021e4ebe03b50e4d8eda9b1fcc679318f6425251fe0"
    ]
    operation_allowlist_sha256: Literal[
        "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"
    ]
    source_api_version: Literal["2026-03-10"] = "2026-03-10"
    selection_policy: Literal[
        "all_current_operations_except_phase3b_curated_allowlist"
    ] = "all_current_operations_except_phase3b_curated_allowlist"

    source_state: SourceState = SourceState.CURRENT
    authority_level: AuthorityLevel = AuthorityLevel.AUTHORITATIVE
    data_role: DataRole = DataRole.BACKGROUND_LOAD_SOURCE

    source_current_operation_count: Literal[479] = 479
    excluded_curated_operation_count: Literal[20] = 20
    operation_count: Literal[459] = 459

    family_counts: tuple[BackgroundFamilyCount, ...] = Field(
        min_length=4,
        max_length=4,
    )
    operations: tuple[BackgroundOperationSelection, ...] = Field(
        min_length=459,
        max_length=459,
    )

    selection_status: Literal["frozen_background_selection"] = (
        "frozen_background_selection"
    )
    normalization_authorized: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_frozen_selection(self) -> Phase3cBackgroundSelectionManifest:
        if self.source_state is not SourceState.CURRENT:
            raise ValueError("Phase 3C background sources must be current")
        if self.authority_level is not AuthorityLevel.AUTHORITATIVE:
            raise ValueError("Phase 3C background sources must be authoritative")
        if self.data_role is not DataRole.BACKGROUND_LOAD_SOURCE:
            raise ValueError("Phase 3C sources must use background_load_source")

        if (
            self.source_current_operation_count
            - self.excluded_curated_operation_count
            != self.operation_count
        ):
            raise ValueError("Phase 3C source and exclusion counts do not reconcile")

        operation_ids = tuple(item.operation_id for item in self.operations)
        if operation_ids != tuple(sorted(operation_ids)):
            raise ValueError("background operations must be operation-ID sorted")
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("background operation IDs must be unique")

        observed_families = tuple(item.family for item in self.family_counts)
        if observed_families != _FAMILY_ORDER:
            raise ValueError("background family counts must use frozen family order")

        expected_counts = tuple(count for _, count in _EXPECTED_FAMILY_COUNTS)
        observed_declared_counts = tuple(
            item.selected_count for item in self.family_counts
        )
        if observed_declared_counts != expected_counts:
            raise ValueError("background family counts do not match frozen counts")

        observed_operation_counts = Counter(
            item.family for item in self.operations
        )
        expected_operation_counts = Counter(dict(_EXPECTED_FAMILY_COUNTS))
        if observed_operation_counts != expected_operation_counts:
            raise ValueError("background operations do not match frozen family counts")

        return self


def build_background_selection_manifest(
    catalog: Phase3aOperationCatalogCandidate,
    allowlist: Phase3aOperationAllowlist,
    *,
    catalog_sha256: Sha256,
    allowlist_sha256: Sha256,
) -> Phase3cBackgroundSelectionManifest:
    """Derive the complete real current background corpus deterministically."""

    if catalog_sha256 != SOURCE_CATALOG_SHA256:
        raise ValueError("source catalog SHA-256 does not match frozen Phase 3C input")
    if allowlist_sha256 != OPERATION_ALLOWLIST_SHA256:
        raise ValueError(
            "operation allowlist SHA-256 does not match frozen Phase 3C input"
        )
    if catalog.snapshot_id != allowlist.snapshot_id:
        raise ValueError("catalog and allowlist snapshot identities do not match")
    if catalog.current.api_version != "2026-03-10":
        raise ValueError("Phase 3C requires the frozen current API version")

    current_ids = {item.operation_id for item in catalog.current.operations}
    curated_ids = {
        operation_id
        for family in allowlist.families
        for operation_id in family.operation_ids
    }

    missing_curated_ids = curated_ids - current_ids
    if missing_curated_ids:
        raise ValueError("frozen curated operation is missing from current catalog")

    selected = tuple(
        BackgroundOperationSelection(
            operation_id=item.operation_id,
            family=item.semantic_family_candidate,
            method=item.method,
            path=item.path,
        )
        for item in sorted(
            (
                item
                for item in catalog.current.operations
                if item.operation_id not in curated_ids
            ),
            key=lambda item: item.operation_id,
        )
    )

    family_counts = Counter(item.family for item in selected)

    return Phase3cBackgroundSelectionManifest(
        snapshot_id=catalog.snapshot_id,
        source_catalog_sha256=SOURCE_CATALOG_SHA256,
        operation_allowlist_sha256=OPERATION_ALLOWLIST_SHA256,
        family_counts=tuple(
            BackgroundFamilyCount(
                family=family,
                selected_count=family_counts[family],
            )
            for family in _FAMILY_ORDER
        ),
        operations=selected,
    )

