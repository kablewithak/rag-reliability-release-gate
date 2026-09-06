from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rag_reliability.corpus.contract_delta import (
    OperationContractDelta,
    Phase3aOperationContractDeltaReport,
)
from rag_reliability.corpus.review_matrix import (
    build_contract_change_review,
    load_and_build_contract_change_review,
)

_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64


def _change(
    operation_id: str,
    family: str,
    *,
    operation_fields: tuple[str, ...] = (),
    historical_refs: tuple[str, ...] = (),
    current_refs: tuple[str, ...] = (),
    changed_refs: tuple[str, ...] = (),
) -> OperationContractDelta:
    return OperationContractDelta(
        operation_id=operation_id,
        family=family,
        method="get",
        path=f"/test/{operation_id}",
        historical_contract_sha256=_SHA_A,
        current_contract_sha256=_SHA_B,
        changed_operation_fields=operation_fields,
        changed_path_item_fields=(),
        historical_only_ref_paths=historical_refs,
        current_only_ref_paths=current_refs,
        changed_shared_ref_paths=changed_refs,
        direct_contract_changed=bool(operation_fields),
        referenced_contract_changed=bool(historical_refs or current_refs or changed_refs),
    )


def _report(changes: tuple[OperationContractDelta, ...]) -> Phase3aOperationContractDeltaReport:
    family_counts = {
        "actions": 0,
        "issues": 0,
        "pull_requests": 0,
        "repositories_and_repository_webhooks": 0,
    }
    direct_counts = family_counts.copy()
    referenced_only_counts = family_counts.copy()
    for change in changes:
        family_counts[change.family] += 1
        if change.direct_contract_changed:
            direct_counts[change.family] += 1
        else:
            referenced_only_counts[change.family] += 1

    from rag_reliability.corpus.contract_delta import ContractDeltaFamilySummary

    summaries = tuple(
        ContractDeltaFamilySummary(
            family=family,
            operation_count=family_counts[family],
            changed_operation_count=family_counts[family],
            direct_changed_count=direct_counts[family],
            referenced_only_changed_count=referenced_only_counts[family],
        )
        for family in (
            "actions",
            "issues",
            "pull_requests",
            "repositories_and_repository_webhooks",
        )
    )
    direct_total = sum(1 for change in changes if change.direct_contract_changed)
    referenced_only_total = sum(1 for change in changes if not change.direct_contract_changed)
    return Phase3aOperationContractDeltaReport(
        snapshot_id="github_rest_v1_2026_09_05",
        source_catalog_sha256=_SHA_C,
        acquisition_receipt_sha256=_SHA_C,
        identity_delta_sha256=_SHA_C,
        shared_operation_count=len(changes),
        changed_operation_count=len(changes),
        unchanged_operation_count=0,
        direct_changed_count=direct_total,
        referenced_only_changed_count=referenced_only_total,
        changed_operations=changes,
        family_summaries=summaries,
        changed_operation_field_frequency=(),
        changed_path_item_field_frequency=(),
    )


def test_review_classifies_direct_and_reference_changes() -> None:
    changes = (
        _change("issues/get", "issues", operation_fields=("description",)),
        _change(
            "pulls/get",
            "pull_requests",
            operation_fields=("responses",),
            changed_refs=("#/components/schemas/pull-request",),
        ),
        _change(
            "actions/get",
            "actions",
            changed_refs=("#/components/parameters/per-page",),
        ),
        _change(
            "repos/get",
            "repositories_and_repository_webhooks",
            current_refs=("#/components/responses/new-response",),
        ),
    )

    review = build_contract_change_review(_report(changes), contract_delta_sha256=_SHA_C)

    modes = {item.operation_id: item.change_mode for item in review.review_items}
    assert modes == {
        "actions/get": "referenced_only",
        "issues/get": "direct_only",
        "pulls/get": "direct_and_referenced",
        "repos/get": "referenced_only",
    }
    assert review.changed_operation_count == 4
    assert review.ingestion_authorized is False


def test_review_classifies_direct_categories_and_reference_components() -> None:
    change = _change(
        "issues/get",
        "issues",
        operation_fields=("description", "x-github", "requestBody"),
        historical_refs=("#/components/schemas/old",),
        current_refs=("#/components/responses/new",),
        changed_refs=("#/components/headers/rate",),
    )

    review = build_contract_change_review(_report((change,)), contract_delta_sha256=_SHA_C)
    item = review.review_items[0]

    assert item.direct_change_categories == (
        "description_or_summary",
        "github_metadata",
        "request_body",
    )
    ref_classes = {summary.component_class for summary in item.reference_change_summaries}
    assert ref_classes == {"headers", "responses", "schemas"}


def test_review_preserves_hash_only_contract_custody() -> None:
    change = _change("issues/get", "issues", operation_fields=("responses",))
    review = build_contract_change_review(_report((change,)), contract_delta_sha256=_SHA_C)
    payload = review.model_dump(mode="json")
    serialized = str(payload)

    assert "raw_openapi" not in serialized
    assert "historical_contract_sha256" in serialized
    assert "current_contract_sha256" in serialized
    assert review.release_eligible is False


def test_loader_rejects_contract_delta_sidecar_mismatch(tmp_path: Path) -> None:
    change = _change("issues/get", "issues", operation_fields=("responses",))
    report = _report((change,))
    path = tmp_path / "contract_delta.json"
    content = report.model_dump_json().encode("utf-8")
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{'0' * 64}  {path.name}\n",
        encoding="utf-8",
    )

    assert digest != "0" * 64
    with pytest.raises(ValueError, match="SHA-256 sidecar mismatch"):
        load_and_build_contract_change_review(path)
