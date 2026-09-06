"""Emit the Phase 3A deterministic contract-change review matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.review_matrix import load_and_build_contract_change_review


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
        "--contract-delta",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_contract_delta_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/development/phase3a_contract_change_review_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = load_and_build_contract_change_review(repo_root / args.contract_delta)
    report_sha = _write_report(repo_root / args.output, report.model_dump(mode="json"))

    print(f"PHASE3A_REVIEW_SOURCE_CONTRACT_DELTA_SHA256={report.source_contract_delta_sha256}")
    print(f"PHASE3A_REVIEW_CHANGED_OPERATION_COUNT={report.changed_operation_count}")
    family_counts = {
        summary.family: summary.changed_operation_count for summary in report.family_summaries
    }
    print(f"PHASE3A_REVIEW_FAMILY_COUNTS={json.dumps(family_counts, sort_keys=True)}")
    mode_counts = {item.name: item.count for item in report.change_mode_counts}
    print(f"PHASE3A_REVIEW_CHANGE_MODE_COUNTS={json.dumps(mode_counts, sort_keys=True)}")
    direct_counts = {item.name: item.count for item in report.direct_category_counts}
    print(f"PHASE3A_REVIEW_DIRECT_CATEGORY_COUNTS={json.dumps(direct_counts, sort_keys=True)}")
    ref_counts = {item.name: item.count for item in report.reference_component_class_counts}
    print(f"PHASE3A_REVIEW_REFERENCE_CLASS_COUNTS={json.dumps(ref_counts, sort_keys=True)}")
    print("PHASE3A_SELECTION_STATUS=candidate_only")
    print("PHASE3A_INGESTION_AUTHORIZED=false")
    print(f"PHASE3A_CONTRACT_CHANGE_REVIEW_SHA256={report_sha}")


if __name__ == "__main__":
    main()
