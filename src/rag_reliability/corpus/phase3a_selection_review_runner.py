"""Emit the Phase 3A operation-selection review worksheet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.selection_review import load_and_build_operation_selection_review


def _write_report(path: Path, payload: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
    )
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("artifacts/development/phase3a_contract_change_review_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_selection_review_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = load_and_build_operation_selection_review(repo_root / args.review)
    report_sha = _write_report(repo_root / args.output, report.model_dump(mode="json"))

    print(
        "PHASE3A_SELECTION_REVIEW_SOURCE_SHA256="
        f"{report.source_contract_change_review_sha256}"
    )
    print(f"PHASE3A_SELECTION_REVIEW_OPERATION_COUNT={report.changed_operation_count}")
    tier_counts = {item.tier: item.count for item in report.tier_counts}
    print(f"PHASE3A_SELECTION_REVIEW_TIER_COUNTS={json.dumps(tier_counts, sort_keys=True)}")
    family_counts = {
        item.family: {
            "tier_a_direct": item.tier_a_direct,
            "tier_b_substantive_reference": item.tier_b_substantive_reference,
            "tier_c_example_only": item.tier_c_example_only,
        }
        for item in report.family_tier_counts
    }
    print(
        "PHASE3A_SELECTION_REVIEW_FAMILY_TIER_COUNTS="
        f"{json.dumps(family_counts, sort_keys=True)}"
    )
    direct_ids = [
        item.operation_id for item in report.items if item.selection_tier == "tier_a_direct"
    ]
    print(f"PHASE3A_SELECTION_REVIEW_TIER_A_IDS={json.dumps(direct_ids)}")
    print("PHASE3A_SELECTION_STATUS=candidate_only")
    print("PHASE3A_INGESTION_AUTHORIZED=false")
    print(f"PHASE3A_OPERATION_SELECTION_REVIEW_SHA256={report_sha}")


if __name__ == "__main__":
    main()
