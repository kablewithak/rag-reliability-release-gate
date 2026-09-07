"""Freeze the corrected Phase 3B render-dependency closure as v2 evidence."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.corpus.render_dependencies import Phase3bRenderDependencyClosureCandidate
from rag_reliability.corpus.render_dependency_freeze import (
    build_freeze_receipt,
    freeze_render_dependencies,
    frozen_manifest_path,
)


def _read_verified_json(path: Path) -> tuple[bytes, str]:
    content = path.read_bytes()
    observed = hashlib.sha256(content).hexdigest()
    sidecar_path = path.with_suffix(path.suffix + ".sha256")
    parts = sidecar_path.read_text(encoding="utf-8").strip().split()
    if len(parts) != 2 or parts[1] != path.name:
        raise ValueError(f"malformed SHA-256 sidecar: {path.name}")
    if parts[0] != observed:
        raise ValueError(f"SHA-256 sidecar mismatch: {path.name}")
    return content, observed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    artifacts = repo_root / "artifacts" / "development"
    candidate_path = artifacts / "phase3b_render_dependency_closure_candidate_v1.json"
    candidate_content, candidate_sha = _read_verified_json(candidate_path)
    candidate = Phase3bRenderDependencyClosureCandidate.model_validate_json(
        candidate_content
    )

    frozen = freeze_render_dependencies(candidate, candidate_sha256=candidate_sha)
    manifest_path = frozen_manifest_path(repo_root)
    manifest_sha = write_json_with_sha256(manifest_path, frozen)

    receipt = build_freeze_receipt(
        frozen,
        frozen_manifest_sha256=manifest_sha,
    )
    receipt_path = artifacts / "phase3b_render_dependency_freeze_receipt_v2.json"
    receipt_sha = write_json_with_sha256(receipt_path, receipt)

    print(
        "PHASE3B_RENDER_DEPENDENCY_FREEZE_SOURCE_AUDIT_SHA256="
        f"{frozen.source_render_audit_sha256}"
    )
    print(f"PHASE3B_RENDER_DEPENDENCY_FREEZE_SOURCE_CLOSURE_SHA256={candidate_sha}")
    print(
        "PHASE3B_RENDER_DEPENDENCY_FREEZE_REFERENCE_COUNT="
        f"{len(frozen.resolved_data_references)}"
    )
    print(f"PHASE3B_RENDER_DEPENDENCY_FREEZE_FILE_COUNT={len(frozen.dependency_files)}")
    print(
        "PHASE3B_RENDER_DEPENDENCY_FREEZE_LIQUID_TAG_COUNT="
        f"{len(frozen.required_liquid_tags)}"
    )
    print(
        "PHASE3B_RENDER_DEPENDENCY_FREEZE_TEMPLATE_VARIABLE_COUNT="
        f"{len(frozen.required_template_variables)}"
    )
    print("PHASE3B_RENDER_DEPENDENCY_FREEZE_TRANSITIVE_REFERENCE_COUNT=0")
    print("PHASE3B_RENDER_DEPENDENCY_FREEZE_SUPERSEDES_VERSION=phase3b-render-dependency-freeze-v1")
    print("PHASE3B_RENDER_DEPENDENCY_FREEZE_SUPERSESSION_REASON=liquid_trim_marker_parser_repair")
    print("PHASE3B_RENDER_DEPENDENCY_FREEZE_STATUS=frozen")
    print("PHASE3B_RENDER_CONTEXT_REVIEW_REQUIRED=true")
    print("PHASE3B_RENDERING_AUTHORIZED=false")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDER_DEPENDENCY_MANIFEST_SHA256={manifest_sha}")
    print(f"PHASE3B_RENDER_DEPENDENCY_FREEZE_RECEIPT_SHA256={receipt_sha}")


if __name__ == "__main__":
    main()
