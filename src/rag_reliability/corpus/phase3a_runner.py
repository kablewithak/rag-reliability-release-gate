"""Acquire frozen Phase 3A inputs and emit a candidate operation catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.acquisition import acquire_selection
from rag_reliability.corpus.catalog import build_operation_catalog
from rag_reliability.corpus.models import CorpusSourceSelectionPlan


def _write_json(path: Path, payload: object) -> str:
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
        "--plan",
        type=Path,
        default=Path("datasets/source_manifests/phase3a_source_selection_v1.json"),
    )
    parser.add_argument(
        "--receipt-output",
        type=Path,
        default=Path("artifacts/development/phase3a_acquisition_receipt_v1.json"),
    )
    parser.add_argument(
        "--catalog-output",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_catalog_candidate_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    plan_path = repo_root / args.plan
    plan = CorpusSourceSelectionPlan.model_validate_json(
        plan_path.read_text(encoding="utf-8")
    )
    receipt = acquire_selection(repo_root, plan)

    by_source_id = {item.source_id: item for item in receipt.files}
    current_receipt = by_source_id["openapi-current-2026-03-10"]
    historical_receipt = by_source_id["openapi-historical-2022-11-28"]
    current_bytes = (repo_root / current_receipt.cache_path).read_bytes()
    historical_bytes = (repo_root / historical_receipt.cache_path).read_bytes()

    catalog = build_operation_catalog(
        current_receipt,
        current_bytes,
        historical_receipt,
        historical_bytes,
    )

    receipt_path = repo_root / args.receipt_output
    catalog_path = repo_root / args.catalog_output
    receipt_sha = _write_json(receipt_path, receipt.model_dump(mode="json"))
    catalog_sha = _write_json(catalog_path, catalog.model_dump(mode="json"))

    current_counts: dict[str, int] = {}
    for operation in catalog.current.operations:
        family = operation.semantic_family_candidate
        current_counts[family] = current_counts.get(family, 0) + 1

    historical_counts: dict[str, int] = {}
    for operation in catalog.historical.operations:
        family = operation.semantic_family_candidate
        historical_counts[family] = historical_counts.get(family, 0) + 1

    print("PHASE3A_SNAPSHOT_ID=github_rest_v1_2026_09_05")
    print(f"PHASE3A_ACQUIRED_FILE_COUNT={len(receipt.files)}")
    print(f"PHASE3A_CURRENT_OPERATION_COUNT={len(catalog.current.operations)}")
    print(f"PHASE3A_HISTORICAL_OPERATION_COUNT={len(catalog.historical.operations)}")
    print(f"PHASE3A_CURRENT_FAMILY_COUNTS={json.dumps(current_counts, sort_keys=True)}")
    print(
        "PHASE3A_HISTORICAL_FAMILY_COUNTS="
        f"{json.dumps(historical_counts, sort_keys=True)}"
    )
    print("PHASE3A_SELECTION_STATUS=candidate_only")
    print("PHASE3A_INGESTION_AUTHORIZED=false")
    print(f"PHASE3A_ACQUISITION_RECEIPT_SHA256={receipt_sha}")
    print(f"PHASE3A_OPERATION_CATALOG_SHA256={catalog_sha}")


if __name__ == "__main__":
    main()
