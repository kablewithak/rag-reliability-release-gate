from __future__ import annotations

from rag_reliability.corpus.models import SemanticOperationFamily
from rag_reliability.corpus.review_matrix import (
    OperationContractReviewItem,
    Phase3aContractChangeReview,
    ReferenceChangeSummary,
    ReviewFamilySummary,
)
from rag_reliability.corpus.selection_review import build_operation_selection_review

_SHA = "a" * 64


def _item(
    operation_id: str,
    family: SemanticOperationFamily,
    *,
    change_mode: str,
    direct_categories: tuple[str, ...] = (),
    references: tuple[ReferenceChangeSummary, ...] = (),
) -> OperationContractReviewItem:
    changed_fields = ("responses",) if change_mode != "referenced_only" else ()
    return OperationContractReviewItem.model_validate(
        {
            "operation_id": operation_id,
            "family": family,
            "method": "get",
            "path": f"/{operation_id}",
            "change_mode": change_mode,
            "changed_operation_fields": changed_fields,
            "changed_path_item_fields": (),
            "direct_change_categories": direct_categories,
            "reference_change_summaries": references,
            "historical_contract_sha256": _SHA,
            "current_contract_sha256": "b" * 64,
        }
    )


def _review(items: tuple[OperationContractReviewItem, ...]) -> Phase3aContractChangeReview:
    families: tuple[SemanticOperationFamily, ...] = (
        "actions",
        "issues",
        "pull_requests",
        "repositories_and_repository_webhooks",
    )
    summaries = tuple(
        ReviewFamilySummary(
            family=family,
            changed_operation_count=sum(1 for item in items if item.family == family),
            direct_only_count=sum(
                1
                for item in items
                if item.family == family and item.change_mode == "direct_only"
            ),
            direct_and_referenced_count=sum(
                1
                for item in items
                if item.family == family and item.change_mode == "direct_and_referenced"
            ),
            referenced_only_count=sum(
                1
                for item in items
                if item.family == family and item.change_mode == "referenced_only"
            ),
        )
        for family in families
    )
    return Phase3aContractChangeReview.model_validate(
        {
            "snapshot_id": "github_rest_v1_2026_09_05",
            "source_contract_delta_sha256": _SHA,
            "changed_operation_count": len(items),
            "review_items": items,
            "family_summaries": summaries,
            "change_mode_counts": [
                {"name": "direct_only", "count": 1},
                {"name": "referenced_only", "count": 2},
            ],
            "direct_category_counts": [{"name": "responses", "count": 1}],
            "reference_component_class_counts": [
                {"name": "schemas", "count": 1},
                {"name": "examples", "count": 1},
            ],
        }
    )


def test_selection_review_separates_direct_substantive_and_example_only() -> None:
    items = (
        _item(
            "issues/direct",
            "issues",
            change_mode="direct_only",
            direct_categories=("responses",),
        ),
        _item(
            "actions/schema",
            "actions",
            change_mode="referenced_only",
            references=(
                ReferenceChangeSummary(
                    component_class="schemas",
                    historical_only_count=0,
                    current_only_count=0,
                    changed_shared_count=1,
                ),
            ),
        ),
        _item(
            "pulls/example",
            "pull_requests",
            change_mode="referenced_only",
            references=(
                ReferenceChangeSummary(
                    component_class="examples",
                    historical_only_count=0,
                    current_only_count=0,
                    changed_shared_count=1,
                ),
            ),
        ),
    )
    report = build_operation_selection_review(_review(items), review_sha256="c" * 64)

    assert [item.selection_tier for item in report.items] == [
        "tier_a_direct",
        "tier_b_substantive_reference",
        "tier_c_example_only",
    ]
    assert report.ingestion_authorized is False
    assert report.release_eligible is False


def test_selection_review_preserves_all_changed_operations() -> None:
    items = (
        _item(
            "issues/direct",
            "issues",
            change_mode="direct_only",
            direct_categories=("responses",),
        ),
        _item(
            "actions/schema",
            "actions",
            change_mode="referenced_only",
            references=(
                ReferenceChangeSummary(
                    component_class="schemas",
                    historical_only_count=0,
                    current_only_count=0,
                    changed_shared_count=1,
                ),
            ),
        ),
        _item(
            "pulls/example",
            "pull_requests",
            change_mode="referenced_only",
            references=(
                ReferenceChangeSummary(
                    component_class="examples",
                    historical_only_count=0,
                    current_only_count=0,
                    changed_shared_count=1,
                ),
            ),
        ),
    )
    report = build_operation_selection_review(_review(items), review_sha256="c" * 64)

    assert report.changed_operation_count == 3
    assert sum(item.count for item in report.tier_counts) == 3
    assert sum(item.total_count for item in report.family_tier_counts) == 3
