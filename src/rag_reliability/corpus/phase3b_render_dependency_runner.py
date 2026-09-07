"""Run the Phase 3B candidate render-dependency closure discovery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.render_audit import (
    Phase3bAuthoredRenderabilityAudit,
    write_json_with_sha256,
)
from rag_reliability.corpus.render_dependencies import (
    build_render_dependency_closure_candidate,
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
    audit_path = artifacts / "phase3b_authored_renderability_audit_v1.json"
    audit_content, audit_sha = _read_verified_json(audit_path)
    audit = Phase3bAuthoredRenderabilityAudit.model_validate_json(audit_content)

    closure = build_render_dependency_closure_candidate(
        repo_root,
        audit,
        source_render_audit_sha256=audit_sha,
    )
    output_path = artifacts / "phase3b_render_dependency_closure_candidate_v1.json"
    closure_sha = write_json_with_sha256(output_path, closure)

    reusable_file_count = sum(
        item.media_type == "markdown_reusable" for item in closure.dependency_files
    )
    variable_file_count = sum(
        item.media_type == "yaml_variables" for item in closure.dependency_files
    )

    print(f"PHASE3B_RENDER_DEPENDENCY_SOURCE_AUDIT_SHA256={audit_sha}")
    print(
        "PHASE3B_RENDER_DEPENDENCY_DIRECT_REFERENCE_COUNT="
        f"{len(closure.direct_data_references)}"
    )
    print(
        "PHASE3B_RENDER_DEPENDENCY_RESOLVED_REFERENCE_COUNT="
        f"{len(closure.resolved_data_references)}"
    )
    print(
        "PHASE3B_RENDER_DEPENDENCY_TRANSITIVE_REFERENCE_COUNT="
        f"{len(closure.transitive_data_references)}"
    )
    print(f"PHASE3B_RENDER_DEPENDENCY_FILE_COUNT={len(closure.dependency_files)}")
    print(f"PHASE3B_RENDER_DEPENDENCY_REUSABLE_FILE_COUNT={reusable_file_count}")
    print(f"PHASE3B_RENDER_DEPENDENCY_VARIABLE_FILE_COUNT={variable_file_count}")
    print(
        "PHASE3B_RENDER_DEPENDENCY_TRANSITIVE_REFERENCES="
        f"{json.dumps(closure.transitive_data_references)}"
    )
    print(
        "PHASE3B_RENDER_DEPENDENCY_FILE_PATHS="
        f"{json.dumps([item.path for item in closure.dependency_files])}"
    )
    print(
        "PHASE3B_RENDER_REQUIRED_LIQUID_TAGS="
        f"{json.dumps(closure.render_liquid_tags)}"
    )
    print(
        "PHASE3B_RENDER_REQUIRED_TEMPLATE_VARIABLES="
        f"{json.dumps(closure.render_template_variables)}"
    )
    print("PHASE3B_RENDER_DEPENDENCY_FREEZE_STATUS=candidate_only")
    print("PHASE3B_RENDERING_AUTHORIZED=false")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDER_DEPENDENCY_CLOSURE_SHA256={closure_sha}")


if __name__ == "__main__":
    main()
