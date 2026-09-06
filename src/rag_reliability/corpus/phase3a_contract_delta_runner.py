"""Emit a semantic contract delta report for shared Phase 3A operations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.contract_delta import load_and_build_operation_contract_delta


def _write_report(path: Path, payload: object) -> str:
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    content = text.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
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
        "--catalog",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_catalog_candidate_v1.json"),
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("artifacts/development/phase3a_acquisition_receipt_v1.json"),
    )
    parser.add_argument(
        "--identity-delta",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_delta_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_contract_delta_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = load_and_build_operation_contract_delta(
        repo_root,
        catalog_path=repo_root / args.catalog,
        receipt_path=repo_root / args.receipt,
        identity_delta_path=repo_root / args.identity_delta,
    )
    report_sha = _write_report(repo_root / args.output, report.model_dump(mode="json"))

    print(f"PHASE3A_CONTRACT_SOURCE_CATALOG_SHA256={report.source_catalog_sha256}")
    print(f"PHASE3A_CONTRACT_ACQUISITION_SHA256={report.acquisition_receipt_sha256}")
    print(f"PHASE3A_CONTRACT_IDENTITY_DELTA_SHA256={report.identity_delta_sha256}")
    print(f"PHASE3A_CONTRACT_SHARED_OPERATION_COUNT={report.shared_operation_count}")
    print(f"PHASE3A_CONTRACT_CHANGED_OPERATION_COUNT={report.changed_operation_count}")
    print(f"PHASE3A_CONTRACT_DIRECT_CHANGED_COUNT={report.direct_changed_count}")
    print(
        "PHASE3A_CONTRACT_REFERENCED_ONLY_CHANGED_COUNT="
        f"{report.referenced_only_changed_count}"
    )
    family_counts = {
        summary.family: summary.changed_operation_count
        for summary in report.family_summaries
    }
    print(f"PHASE3A_CONTRACT_CHANGED_FAMILY_COUNTS={json.dumps(family_counts, sort_keys=True)}")
    print("PHASE3A_SELECTION_STATUS=candidate_only")
    print("PHASE3A_INGESTION_AUTHORIZED=false")
    print(f"PHASE3A_OPERATION_CONTRACT_DELTA_SHA256={report_sha}")


if __name__ == "__main__":
    main()
