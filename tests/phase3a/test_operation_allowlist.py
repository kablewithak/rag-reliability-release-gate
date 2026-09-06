from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from rag_reliability.corpus.allowlist import (
    Phase3aOperationAllowlist,
    authorize_frozen_allowlist,
    validate_allowlist_against_shortlist,
)
from rag_reliability.corpus.shortlist import (
    OperationShortlistItem,
    Phase3aOperationShortlist,
    ShortlistFamilyCount,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = REPO_ROOT / "datasets" / "source_manifests" / "phase3a_operation_allowlist_v1.json"
SHORTLIST_SHA = "26ca1daa07f469260c0912017c415f4df71b2518f9223ee396ad52144877b335"


def _load_allowlist() -> Phase3aOperationAllowlist:
    return Phase3aOperationAllowlist.model_validate_json(
        ALLOWLIST_PATH.read_text(encoding="utf-8")
    )


def _shortlist_from_allowlist(allowlist: Phase3aOperationAllowlist) -> Phase3aOperationShortlist:
    tier_a_ids = {
        "actions/create-workflow-dispatch",
        "issues/create",
        "issues/update",
        "repos/accept-invitation-for-authenticated-user",
        "repos/create-for-authenticated-user",
        "repos/create-in-org",
        "repos/get-content",
        "repos/list-attestations",
    }
    items: list[OperationShortlistItem] = []
    counts: list[ShortlistFamilyCount] = []
    for family in allowlist.families:
        tier_a_count = 0
        tier_b_count = 0
        for operation_id in family.operation_ids:
            tier_a = operation_id in tier_a_ids
            if tier_a:
                tier_a_count += 1
            if not tier_a:
                tier_b_count += 1
            items.append(
                OperationShortlistItem(
                    operation_id=operation_id,
                    family=family.family,
                    method="get",
                    path=f"/fixture/{operation_id}",
                    selection_tier=(
                        "tier_a_direct" if tier_a else "tier_b_substantive_reference"
                    ),
                    shortlist_reason=(
                        "mandatory_direct_change"
                        if tier_a
                        else "family_balance_substantive_reference"
                    ),
                    direct_change_categories=("responses",) if tier_a else (),
                    reference_component_classes=("schemas",),
                )
            )
        counts.append(
            ShortlistFamilyCount(
                family=family.family,
                selected_count=5,
                tier_a_direct_count=tier_a_count,
                tier_b_substantive_reference_count=tier_b_count,
            )
        )
    return Phase3aOperationShortlist(
        snapshot_id=allowlist.snapshot_id,
        source_selection_review_sha256="0" * 64,
        shortlist_count=20,
        items=tuple(items),
        family_counts=tuple(counts),
    )


def _write_verified_json(path: Path, payload: object) -> str:
    content = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
    )
    return digest


def test_frozen_allowlist_has_twenty_unique_balanced_operations() -> None:
    allowlist = _load_allowlist()
    all_ids = [
        operation_id
        for family in allowlist.families
        for operation_id in family.operation_ids
    ]

    assert allowlist.operation_count == 20
    assert len(all_ids) == len(set(all_ids)) == 20
    assert [len(family.operation_ids) for family in allowlist.families] == [5, 5, 5, 5]
    assert allowlist.ingestion_authorized is True
    assert allowlist.release_eligible is False


def test_allowlist_requires_exact_reviewed_shortlist_membership() -> None:
    allowlist = _load_allowlist()
    shortlist = _shortlist_from_allowlist(allowlist)

    validate_allowlist_against_shortlist(
        allowlist,
        shortlist,
        shortlist_sha256=allowlist.source_shortlist_sha256,
    )

    changed_items = list(shortlist.items)
    changed_items[0] = changed_items[0].model_copy(update={"operation_id": "actions/not-reviewed"})
    changed = shortlist.model_copy(update={"items": tuple(changed_items)})

    with pytest.raises(ValueError, match="exactly match"):
        validate_allowlist_against_shortlist(
            allowlist,
            changed,
            shortlist_sha256=allowlist.source_shortlist_sha256,
        )


def test_allowlist_rejects_shortlist_hash_drift() -> None:
    allowlist = _load_allowlist()
    shortlist = _shortlist_from_allowlist(allowlist)

    with pytest.raises(ValueError, match="source shortlist hash"):
        validate_allowlist_against_shortlist(
            allowlist,
            shortlist,
            shortlist_sha256="f" * 64,
        )


def test_authorization_receipt_binds_shortlist_and_allowlist_hashes(tmp_path: Path) -> None:
    allowlist = _load_allowlist()
    shortlist = _shortlist_from_allowlist(allowlist)
    shortlist_path = tmp_path / "shortlist.json"
    observed_shortlist_sha = _write_verified_json(
        shortlist_path,
        shortlist.model_dump(mode="json"),
    )

    rewritten_allowlist = allowlist.model_copy(
        update={"source_shortlist_sha256": observed_shortlist_sha}
    )
    allowlist_path = tmp_path / "allowlist.json"
    allowlist_path.write_text(
        json.dumps(rewritten_allowlist.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    observed_allowlist_sha = hashlib.sha256(allowlist_path.read_bytes()).hexdigest()

    receipt = authorize_frozen_allowlist(shortlist_path, allowlist_path)

    assert receipt.source_shortlist_sha256 == observed_shortlist_sha
    assert receipt.operation_allowlist_sha256 == observed_allowlist_sha
    assert receipt.operation_count == 20
    assert receipt.ingestion_authorized is True
    assert receipt.release_eligible is False
