"""Emit a deterministic review artifact for Phase 3A operation deltas."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.delta import load_and_build_operation_delta


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
        "--output",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_delta_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = load_and_build_operation_delta(repo_root / args.catalog)
    report_sha = _write_report(repo_root / args.output, report.model_dump(mode="json"))

    print(f"PHASE3A_DELTA_SOURCE_CATALOG_SHA256={report.source_catalog_sha256}")
    print(f"PHASE3A_DELTA_CURRENT_ONLY_COUNT={len(report.current_only_operation_ids)}")
    print(
        "PHASE3A_DELTA_HISTORICAL_ONLY_COUNT="
        f"{len(report.historical_only_operation_ids)}"
    )
    print(
        "PHASE3A_DELTA_SHARED_IDENTITY_CHANGED_COUNT="
        f"{len(report.shared_identity_changes)}"
    )
    print(
        "PHASE3A_DELTA_UNCHANGED_SHARED_COUNT="
        f"{report.unchanged_shared_operation_count}"
    )
    print("PHASE3A_SELECTION_STATUS=candidate_only")
    print("PHASE3A_INGESTION_AUTHORIZED=false")
    print(f"PHASE3A_OPERATION_DELTA_SHA256={report_sha}")


if __name__ == "__main__":
    main()
