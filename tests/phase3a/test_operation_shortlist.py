from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rag_reliability.corpus.selection_review import (
    OperationSelectionReviewItem,
    Phase3aOperationSelectionReview,
    SelectionFamilyTierCount,
    SelectionTierCount,
)
from rag_reliability.corpus.shortlist import (
    build_operation_shortlist,
    load_and_build_operation_shortlist,
)


def _item(
    operation_id: str,
    family: str,
    tier: str,
    classes: tuple[str, ...] = ("schemas",),
) -> OperationSelectionReviewItem:
    return OperationSelectionReviewItem(
        operation_id=operation_id,
        family=family,
        method="get",
        path=f"/{operation_id}",
        selection_tier=tier,
        change_mode="direct_only" if tier == "tier_a_direct" else "referenced_only",
        direct_change_categories=("responses",) if tier == "tier_a_direct" else (),
        reference_component_classes=classes,
        substantive_reference_change=True,
        example_reference_change=False,
    )


def _review() -> Phase3aOperationSelectionReview:
    items: list[OperationSelectionReviewItem] = []
    direct_counts = {
        "actions": 1,
        "issues": 2,
        "pull_requests": 0,
        "repositories_and_repository_webhooks": 5,
    }
    for family, direct_count in direct_counts.items():
        for index in range(direct_count):
            items.append(_item(f"{family}/direct-{index}", family, "tier_a_direct"))
        for index in range(6):
            classes = ("responses", "schemas") if index == 0 else ("schemas",)
            items.append(
                _item(
                    f"{family}/reference-{index}",
                    family,
                    "tier_b_substantive_reference",
                    classes,
                )
            )

    tier_a_count = sum(direct_counts.values())
    tier_b_count = len(items) - tier_a_count
    return Phase3aOperationSelectionReview(
        snapshot_id="github_rest_v1_2026_09_05",
        source_contract_change_review_sha256="1" * 64,
        changed_operation_count=len(items),
        items=tuple(items),
        tier_counts=(
            SelectionTierCount(tier="tier_a_direct", count=tier_a_count),
            SelectionTierCount(tier="tier_b_substantive_reference", count=tier_b_count),
            SelectionTierCount(tier="tier_c_example_only", count=0),
        ),
        family_tier_counts=tuple(
            SelectionFamilyTierCount(
                family=family,
                tier_a_direct=direct_counts[family],
                tier_b_substantive_reference=6,
                tier_c_example_only=0,
            )
            for family in (
                "actions",
                "issues",
                "pull_requests",
                "repositories_and_repository_webhooks",
            )
        ),
    )


def test_shortlist_keeps_all_direct_changes_and_balances_families() -> None:
    report = build_operation_shortlist(_review(), review_sha256="2" * 64)

    assert report.shortlist_count == 20
    assert all(item.selected_count == 5 for item in report.family_counts)
    selected_ids = {item.operation_id for item in report.items}
    for item in _review().items:
        if item.selection_tier == "tier_a_direct":
            assert item.operation_id in selected_ids


def test_shortlist_prefers_response_reference_candidate_before_schema_only() -> None:
    report = build_operation_shortlist(_review(), review_sha256="2" * 64)
    pull_ids = [
        item.operation_id
        for item in report.items
        if item.family == "pull_requests"
    ]

    assert "pull_requests/reference-0" in pull_ids
    assert len(pull_ids) == 5


def test_shortlist_is_deterministic_under_input_reordering() -> None:
    review = _review()
    reversed_review = review.model_copy(update={"items": tuple(reversed(review.items))})

    first = build_operation_shortlist(review, review_sha256="2" * 64)
    second = build_operation_shortlist(reversed_review, review_sha256="2" * 64)

    assert first == second


def test_loader_rejects_invalid_sidecar(tmp_path: Path) -> None:
    review_path = tmp_path / "selection.json"
    content = _review().model_dump_json(indent=2).encode("utf-8")
    review_path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    review_path.with_suffix(".json.sha256").write_text(
        f"{digest[:-1]}0  {review_path.name}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="SHA-256 sidecar mismatch"):
        load_and_build_operation_shortlist(review_path)
