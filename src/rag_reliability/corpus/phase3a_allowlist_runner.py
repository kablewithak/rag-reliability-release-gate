"""Authorize Phase 3 corpus ingestion for the exact frozen operation allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.allowlist import authorize_frozen_allowlist


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
        "--shortlist",
        type=Path,
        default=Path("artifacts/development/phase3a_operation_shortlist_v1.json"),
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=Path("datasets/source_manifests/phase3a_operation_allowlist_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/development/phase3a_ingestion_authorization_v1.json"),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    receipt = authorize_frozen_allowlist(
        repo_root / args.shortlist,
        repo_root / args.allowlist,
    )
    receipt_sha = _write_report(repo_root / args.output, receipt.model_dump(mode="json"))

    family_counts = {
        item.family: item.operation_count for item in receipt.family_counts
    }
    print(f"PHASE3A_ALLOWLIST_SOURCE_SHORTLIST_SHA256={receipt.source_shortlist_sha256}")
    print(f"PHASE3A_OPERATION_ALLOWLIST_SHA256={receipt.operation_allowlist_sha256}")
    print(f"PHASE3A_ALLOWLIST_COUNT={receipt.operation_count}")
    print(f"PHASE3A_ALLOWLIST_FAMILY_COUNTS={json.dumps(family_counts, sort_keys=True)}")
    print("PHASE3A_SELECTION_STATUS=frozen_allowlist")
    print("PHASE3A_INGESTION_AUTHORIZED=true")
    print("PHASE3A_RELEASE_ELIGIBLE=false")
    print(f"PHASE3A_INGESTION_AUTHORIZATION_SHA256={receipt_sha}")


if __name__ == "__main__":
    main()
