from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.allowlist import Phase3aOperationAllowlist
from rag_reliability.corpus.background import (
    OPERATION_ALLOWLIST_SHA256,
    SOURCE_CATALOG_SHA256,
    Phase3cBackgroundSelectionManifest,
    build_background_selection_manifest,
)
from rag_reliability.corpus.models import Phase3aOperationCatalogCandidate

_ROOT = Path(__file__).resolve().parents[2]

_CATALOG_PATH = (
    _ROOT
    / "artifacts"
    / "development"
    / "phase3a_operation_catalog_candidate_v1.json"
)
_ALLOWLIST_PATH = (
    _ROOT
    / "datasets"
    / "source_manifests"
    / "phase3a_operation_allowlist_v1.json"
)


def _load_inputs() -> tuple[
    Phase3aOperationCatalogCandidate,
    Phase3aOperationAllowlist,
    str,
    str,
]:
    catalog_bytes = _CATALOG_PATH.read_bytes()
    allowlist_bytes = _ALLOWLIST_PATH.read_bytes()

    return (
        Phase3aOperationCatalogCandidate.model_validate_json(catalog_bytes),
        Phase3aOperationAllowlist.model_validate_json(allowlist_bytes),
        hashlib.sha256(catalog_bytes).hexdigest(),
        hashlib.sha256(allowlist_bytes).hexdigest(),
    )


def _build() -> Phase3cBackgroundSelectionManifest:
    catalog, allowlist, catalog_sha256, allowlist_sha256 = _load_inputs()
    return build_background_selection_manifest(
        catalog,
        allowlist,
        catalog_sha256=catalog_sha256,
        allowlist_sha256=allowlist_sha256,
    )


def test_frozen_phase3c_inputs_match_expected_hashes() -> None:
    _, _, catalog_sha256, allowlist_sha256 = _load_inputs()

    assert catalog_sha256 == SOURCE_CATALOG_SHA256
    assert allowlist_sha256 == OPERATION_ALLOWLIST_SHA256


def test_background_selection_uses_all_non_curated_current_operations() -> None:
    catalog, allowlist, catalog_sha256, allowlist_sha256 = _load_inputs()

    manifest = build_background_selection_manifest(
        catalog,
        allowlist,
        catalog_sha256=catalog_sha256,
        allowlist_sha256=allowlist_sha256,
    )

    curated_ids = {
        operation_id
        for family in allowlist.families
        for operation_id in family.operation_ids
    }
    selected_ids = {item.operation_id for item in manifest.operations}

    assert len(catalog.current.operations) == 479
    assert len(curated_ids) == 20
    assert manifest.operation_count == 459
    assert len(manifest.operations) == 459
    assert selected_ids.isdisjoint(curated_ids)
    assert selected_ids | curated_ids == {
        item.operation_id for item in catalog.current.operations
    }


def test_background_selection_has_frozen_real_family_distribution() -> None:
    manifest = _build()

    assert tuple(
        (item.family, item.selected_count)
        for item in manifest.family_counts
    ) == (
        ("actions", 184),
        ("issues", 53),
        ("pull_requests", 24),
        ("repositories_and_repository_webhooks", 198),
    )


def test_background_selection_is_unique_and_deterministically_sorted() -> None:
    manifest = _build()

    operation_ids = tuple(item.operation_id for item in manifest.operations)

    assert operation_ids == tuple(sorted(operation_ids))
    assert len(operation_ids) == len(set(operation_ids))


def test_background_selection_preserves_source_semantics() -> None:
    manifest = _build()

    assert manifest.source_state is SourceState.CURRENT
    assert manifest.authority_level is AuthorityLevel.AUTHORITATIVE
    assert manifest.data_role is DataRole.BACKGROUND_LOAD_SOURCE
    assert manifest.source_api_version == "2026-03-10"


def test_selection_authorizes_normalization_but_not_downstream_phases() -> None:
    manifest = _build()

    assert manifest.normalization_authorized is True
    assert manifest.full_ingestion_ready is False
    assert manifest.chunking_authorized is False
    assert manifest.baseline_authorized is False
    assert manifest.release_eligible is False


def test_manifest_rejects_non_deterministic_operation_order() -> None:
    manifest = _build()
    payload = manifest.model_dump(mode="json")
    payload["operations"] = list(reversed(payload["operations"]))

    with pytest.raises(
        ValidationError,
        match="background operations must be operation-ID sorted",
    ):
        Phase3cBackgroundSelectionManifest.model_validate(payload)


def test_builder_rejects_unfrozen_catalog_hash() -> None:
    catalog, allowlist, _, allowlist_sha256 = _load_inputs()

    with pytest.raises(
        ValueError,
        match="source catalog SHA-256",
    ):
        build_background_selection_manifest(
            catalog,
            allowlist,
            catalog_sha256="0" * 64,
            allowlist_sha256=allowlist_sha256,
        )


def test_builder_rejects_unfrozen_allowlist_hash() -> None:
    catalog, allowlist, catalog_sha256, _ = _load_inputs()

    with pytest.raises(
        ValueError,
        match="operation allowlist SHA-256",
    ):
        build_background_selection_manifest(
            catalog,
            allowlist,
            catalog_sha256=catalog_sha256,
            allowlist_sha256="0" * 64,
        )
