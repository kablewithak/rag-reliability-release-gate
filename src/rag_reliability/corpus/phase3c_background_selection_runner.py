"""Freeze the deterministic Phase 3C background-operation selection manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.contracts.base import Sha256
from rag_reliability.corpus.allowlist import Phase3aOperationAllowlist
from rag_reliability.corpus.background import (
    Phase3cBackgroundSelectionManifest,
    build_background_selection_manifest,
)
from rag_reliability.corpus.models import Phase3aOperationCatalogCandidate
from rag_reliability.corpus.normalization import write_exact_text


def _read_and_hash(path: Path) -> tuple[bytes, Sha256]:
    content = path.read_bytes()
    return content, hashlib.sha256(content).hexdigest()


def load_and_build_background_selection(
    catalog_path: Path,
    allowlist_path: Path,
) -> Phase3cBackgroundSelectionManifest:
    catalog_bytes, catalog_sha256 = _read_and_hash(catalog_path)
    allowlist_bytes, allowlist_sha256 = _read_and_hash(allowlist_path)

    catalog = Phase3aOperationCatalogCandidate.model_validate_json(catalog_bytes)
    allowlist = Phase3aOperationAllowlist.model_validate_json(allowlist_bytes)

    return build_background_selection_manifest(
        catalog,
        allowlist,
        catalog_sha256=catalog_sha256,
        allowlist_sha256=allowlist_sha256,
    )


def write_background_selection_manifest(
    manifest: Phase3cBackgroundSelectionManifest,
    output_path: Path,
) -> Sha256:
    content = (
        json.dumps(
            manifest.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    digest, _ = write_exact_text(output_path, content)

    sidecar_path = output_path.with_suffix(output_path.suffix + ".sha256")
    write_exact_text(
        sidecar_path,
        f"{digest}  {output_path.name}\n",
    )

    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(
            "artifacts/development/"
            "phase3a_operation_catalog_candidate_v1.json"
        ),
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=Path(
            "datasets/source_manifests/"
            "phase3a_operation_allowlist_v1.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "datasets/source_manifests/"
            "phase3c_background_selection_v1.json"
        ),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    manifest = load_and_build_background_selection(
        repo_root / args.catalog,
        repo_root / args.allowlist,
    )

    manifest_sha256 = write_background_selection_manifest(
        manifest,
        repo_root / args.output,
    )

    family_counts = {
        item.family: item.selected_count for item in manifest.family_counts
    }

    print(f"PHASE3C_BACKGROUND_SELECTION_SHA256={manifest_sha256}")
    print(
        "PHASE3C_SOURCE_CATALOG_SHA256="
        f"{manifest.source_catalog_sha256}"
    )
    print(
        "PHASE3C_OPERATION_ALLOWLIST_SHA256="
        f"{manifest.operation_allowlist_sha256}"
    )
    print(
        "PHASE3C_BACKGROUND_OPERATION_COUNT="
        f"{manifest.operation_count}"
    )
    print(
        "PHASE3C_BACKGROUND_FAMILY_COUNTS="
        f"{json.dumps(family_counts, sort_keys=True)}"
    )
    print(f"PHASE3C_SELECTION_STATUS={manifest.selection_status}")
    print("PHASE3C_NORMALIZATION_AUTHORIZED=true")
    print("PHASE3C_FULL_INGESTION_READY=false")
    print("PHASE3C_CHUNKING_AUTHORIZED=false")
    print("PHASE3C_BASELINE_AUTHORIZED=false")
    print("PHASE3C_RELEASE_ELIGIBLE=false")


if __name__ == "__main__":
    main()
