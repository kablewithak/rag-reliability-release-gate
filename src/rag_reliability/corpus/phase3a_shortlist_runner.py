"""Emit the balanced Phase 3A operation shortlist for human review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.shortlist import load_and_build_operation_shortlist


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
        default=Path("artifacts/development/phase3a_operation_selection_review_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_shortlist_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = load_and_build_operation_shortlist(repo_root / args.review)
    report_sha = _write_report(repo_root / args.output, report.model_dump(mode="json"))

    print(
        "PHASE3A_SHORTLIST_SOURCE_SELECTION_REVIEW_SHA256="
        f"{report.source_selection_review_sha256}"
    )
    print(f"PHASE3A_SHORTLIST_COUNT={report.shortlist_count}")
    family_counts = {
        item.family: {
            "selected": item.selected_count,
            "tier_a_direct": item.tier_a_direct_count,
            "tier_b_substantive_reference": item.tier_b_substantive_reference_count,
        }
        for item in report.family_counts
    }
    print(f"PHASE3A_SHORTLIST_FAMILY_COUNTS={json.dumps(family_counts, sort_keys=True)}")
    shortlist_ids = {
        family: [item.operation_id for item in report.items if item.family == family]
        for family in (
            "actions",
            "issues",
            "pull_requests",
            "repositories_and_repository_webhooks",
        )
    }
    print(f"PHASE3A_SHORTLIST_IDS={json.dumps(shortlist_ids, sort_keys=True)}")
    print("PHASE3A_SELECTION_STATUS=candidate_only")
    print("PHASE3A_INGESTION_AUTHORIZED=false")
    print(f"PHASE3A_OPERATION_SHORTLIST_SHA256={report_sha}")


if __name__ == "__main__":
    main()
