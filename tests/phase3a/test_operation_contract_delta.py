from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from rag_reliability.corpus.contract_delta import (
    build_operation_contract_delta_report,
)
from rag_reliability.corpus.delta import build_operation_delta_report
from rag_reliability.corpus.models import (
    AcquiredFileReceipt,
    AcquisitionReceipt,
    ApiVersionOperationCatalog,
    OperationCatalogEntry,
    Phase3aOperationCatalogCandidate,
)


def _openapi(*, description: str, schema_type: str) -> bytes:
    payload = {
        "openapi": "3.0.3",
        "paths": {
            "/repos/{owner}/{repo}/issues": {
                "parameters": [
                    {"$ref": "#/components/parameters/owner"},
                ],
                "get": {
                    "operationId": "issues/list-for-repo",
                    "tags": ["issues"],
                    "description": description,
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/issue"}
                                }
                            }
                        }
                    },
                },
            }
        },
        "components": {
            "parameters": {
                "owner": {
                    "name": "owner",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            },
            "schemas": {
                "issue": {
                    "type": "object",
                    "properties": {"number": {"type": schema_type}},
                }
            },
        },
    }
    return yaml.safe_dump(payload, sort_keys=True).encode("utf-8")


def _entry() -> OperationCatalogEntry:
    return OperationCatalogEntry(
        operation_id="issues/list-for-repo",
        method="get",
        path="/repos/{owner}/{repo}/issues",
        tags=("issues",),
        semantic_family_candidate="issues",
    )


def _catalog() -> Phase3aOperationCatalogCandidate:
    entry = _entry()
    return Phase3aOperationCatalogCandidate(
        catalog_version="phase3a-operation-catalog-candidate-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        current=ApiVersionOperationCatalog(
            api_version="2026-03-10",
            source_id="openapi-current-2026-03-10",
            source_git_blob_sha1="a" * 40,
            operations=(entry,),
        ),
        historical=ApiVersionOperationCatalog(
            api_version="2022-11-28",
            source_id="openapi-historical-2022-11-28",
            source_git_blob_sha1="b" * 40,
            operations=(entry,),
        ),
    )


def _receipt(repo_root: Path, historical: bytes, current: bytes) -> AcquisitionReceipt:
    cache_root = repo_root / "cache"
    cache_root.mkdir(parents=True, exist_ok=True)
    historical_path = cache_root / "historical.yaml"
    current_path = cache_root / "current.yaml"
    historical_path.write_bytes(historical)
    current_path.write_bytes(current)

    def item(source_id: str, path: Path, content: bytes) -> AcquiredFileReceipt:
        return AcquiredFileReceipt(
            source_id=source_id,
            repository="github/rest-api-description",
            commit_sha="c" * 40,
            path=path.name,
            expected_git_blob_sha1="d" * 40,
            observed_git_blob_sha1="d" * 40,
            content_sha256=hashlib.sha256(content).hexdigest(),
            byte_count=len(content),
            cache_path=path.relative_to(repo_root).as_posix(),
        )

    filler = tuple(
        item(f"filler-{index}", current_path, current)
        for index in range(10)
    )
    return AcquisitionReceipt(
        receipt_version="phase3a-acquisition-receipt-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        files=(
            item("openapi-current-2026-03-10", current_path, current),
            item("openapi-historical-2022-11-28", historical_path, historical),
            *filler,
        ),
    )


def _identity_delta(catalog: Phase3aOperationCatalogCandidate):
    return build_operation_delta_report(catalog, source_catalog_sha256="1" * 64)


def test_detects_direct_operation_field_change(tmp_path: Path) -> None:
    historical = _openapi(description="Historical description", schema_type="integer")
    current = _openapi(description="Current description", schema_type="integer")
    catalog = _catalog()
    report = build_operation_contract_delta_report(
        tmp_path,
        catalog,
        _receipt(tmp_path, historical, current),
        _identity_delta(catalog),
        catalog_sha256="1" * 64,
        receipt_sha256="2" * 64,
        identity_delta_sha256="3" * 64,
    )
    assert report.changed_operation_count == 1
    change = report.changed_operations[0]
    assert change.direct_contract_changed is True
    assert change.changed_operation_fields == ("description",)


def test_detects_referenced_schema_change_without_direct_change(tmp_path: Path) -> None:
    historical = _openapi(description="Same", schema_type="integer")
    current = _openapi(description="Same", schema_type="string")
    catalog = _catalog()
    report = build_operation_contract_delta_report(
        tmp_path,
        catalog,
        _receipt(tmp_path, historical, current),
        _identity_delta(catalog),
        catalog_sha256="1" * 64,
        receipt_sha256="2" * 64,
        identity_delta_sha256="3" * 64,
    )
    change = report.changed_operations[0]
    assert change.direct_contract_changed is False
    assert change.referenced_contract_changed is True
    assert change.changed_shared_ref_paths == ("#/components/schemas/issue",)
    assert report.referenced_only_changed_count == 1


def test_unchanged_contract_is_not_reported(tmp_path: Path) -> None:
    historical = _openapi(description="Same", schema_type="integer")
    catalog = _catalog()
    report = build_operation_contract_delta_report(
        tmp_path,
        catalog,
        _receipt(tmp_path, historical, historical),
        _identity_delta(catalog),
        catalog_sha256="1" * 64,
        receipt_sha256="2" * 64,
        identity_delta_sha256="3" * 64,
    )
    assert report.changed_operation_count == 0
    assert report.unchanged_operation_count == 1


def test_cached_source_sha256_mismatch_fails_closed(tmp_path: Path) -> None:
    historical = _openapi(description="Same", schema_type="integer")
    current = _openapi(description="Same", schema_type="string")
    catalog = _catalog()
    receipt = _receipt(tmp_path, historical, current)
    current_item = next(
        item for item in receipt.files if item.source_id == "openapi-current-2026-03-10"
    )
    (tmp_path / current_item.cache_path).write_bytes(b"tampered")

    try:
        build_operation_contract_delta_report(
            tmp_path,
            catalog,
            receipt,
            _identity_delta(catalog),
            catalog_sha256="1" * 64,
            receipt_sha256="2" * 64,
            identity_delta_sha256="3" * 64,
        )
    except ValueError as exc:
        assert "cached source SHA-256 mismatch" in str(exc)
    else:
        raise AssertionError("tampered cached source should fail closed")
