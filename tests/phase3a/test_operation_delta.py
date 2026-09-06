import hashlib
from pathlib import Path

import pytest

from rag_reliability.corpus.delta import (
    build_operation_delta_report,
    load_and_build_operation_delta,
)
from rag_reliability.corpus.models import (
    ApiVersionOperationCatalog,
    OperationCatalogEntry,
    Phase3aOperationCatalogCandidate,
)


def _operation(
    operation_id: str,
    *,
    method: str,
    path: str,
    family: str,
) -> OperationCatalogEntry:
    return OperationCatalogEntry.model_validate(
        {
            "operation_id": operation_id,
            "method": method,
            "path": path,
            "tags": [family],
            "semantic_family_candidate": family,
        }
    )


def _catalog() -> Phase3aOperationCatalogCandidate:
    return Phase3aOperationCatalogCandidate(
        catalog_version="phase3a-operation-catalog-candidate-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        current=ApiVersionOperationCatalog(
            api_version="2026-03-10",
            source_id="current",
            source_git_blob_sha1="a" * 40,
            operations=(
                _operation(
                    "actions/shared",
                    method="get",
                    path="/repos/{owner}/{repo}/actions/shared-current",
                    family="actions",
                ),
                _operation(
                    "issues/current-only",
                    method="get",
                    path="/repos/{owner}/{repo}/issues/current-only",
                    family="issues",
                ),
                _operation(
                    "pulls/unchanged",
                    method="get",
                    path="/repos/{owner}/{repo}/pulls/{pull_number}",
                    family="pull_requests",
                ),
            ),
        ),
        historical=ApiVersionOperationCatalog(
            api_version="2022-11-28",
            source_id="historical",
            source_git_blob_sha1="b" * 40,
            operations=(
                _operation(
                    "actions/shared",
                    method="get",
                    path="/repos/{owner}/{repo}/actions/shared-historical",
                    family="actions",
                ),
                _operation(
                    "repos/historical-only",
                    method="delete",
                    path="/repos/{owner}/{repo}/historical-only",
                    family="repositories_and_repository_webhooks",
                ),
                _operation(
                    "pulls/unchanged",
                    method="get",
                    path="/repos/{owner}/{repo}/pulls/{pull_number}",
                    family="pull_requests",
                ),
            ),
        ),
    )


def test_delta_detects_membership_and_identity_changes() -> None:
    report = build_operation_delta_report(_catalog(), source_catalog_sha256="c" * 64)

    assert report.current_operation_count == 3
    assert report.historical_operation_count == 3
    assert report.shared_operation_count == 2
    assert report.unchanged_shared_operation_count == 1
    assert report.current_only_operation_ids == ("issues/current-only",)
    assert report.historical_only_operation_ids == ("repos/historical-only",)
    assert len(report.shared_identity_changes) == 1
    assert report.shared_identity_changes[0].operation_id == "actions/shared"
    assert report.shared_identity_changes[0].path_changed is True
    assert report.ingestion_authorized is False
    assert report.release_eligible is False


def test_delta_is_deterministically_sorted() -> None:
    report = build_operation_delta_report(_catalog(), source_catalog_sha256="d" * 64)

    assert report.current_only_operation_ids == tuple(sorted(report.current_only_operation_ids))
    assert report.historical_only_operation_ids == tuple(
        sorted(report.historical_only_operation_ids)
    )
    assert tuple(change.operation_id for change in report.shared_identity_changes) == tuple(
        sorted(change.operation_id for change in report.shared_identity_changes)
    )


def test_loader_rejects_catalog_sha_sidecar_mismatch(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    content = _catalog().model_dump_json(indent=2).encode("utf-8")
    catalog_path.write_bytes(content)
    catalog_path.with_suffix(".json.sha256").write_text(
        f"{'0' * 64}  {catalog_path.name}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="SHA-256 sidecar mismatch"):
        load_and_build_operation_delta(catalog_path)


def test_loader_binds_report_to_verified_catalog_hash(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    content = _catalog().model_dump_json(indent=2).encode("utf-8")
    catalog_path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    catalog_path.with_suffix(".json.sha256").write_text(
        f"{digest}  {catalog_path.name}\n",
        encoding="utf-8",
    )

    report = load_and_build_operation_delta(catalog_path)

    assert report.source_catalog_sha256 == digest
