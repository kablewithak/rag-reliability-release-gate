"""Freeze the deterministic Phase 3B authored-doc render policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.phase3b_render_semantics_review_runner import (
    render_context_review_path,
    render_semantics_review_path,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.corpus.render_dependency_freeze import frozen_manifest_path
from rag_reliability.corpus.render_policy import (
    build_render_policy_receipt,
    freeze_render_policy,
    render_policy_manifest_path,
)
from rag_reliability.corpus.render_semantics_review import Phase3bRenderSemanticsReview

_EXPECTED_DEPENDENCY_MANIFEST_SHA256 = (
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
)
_EXPECTED_CONTEXT_REVIEW_SHA256 = (
    "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
)
_EXPECTED_SEMANTICS_REVIEW_SHA256 = (
    "25cae92b748ec1e40674c6813772c2c258b366e47f702da682b00dc0fd912368"
)


def _read_verified_json(path: Path) -> tuple[bytes, str]:
    content = path.read_bytes()
    observed = hashlib.sha256(content).hexdigest()
    sidecar = path.with_suffix(path.suffix + ".sha256")
    parts = sidecar.read_text(encoding="utf-8").strip().split()
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

    _, dependency_sha = _read_verified_json(frozen_manifest_path(repo_root))
    if dependency_sha != _EXPECTED_DEPENDENCY_MANIFEST_SHA256:
        raise ValueError("dependency manifest hash does not match accepted v2 freeze")

    _, context_sha = _read_verified_json(render_context_review_path(repo_root))
    if context_sha != _EXPECTED_CONTEXT_REVIEW_SHA256:
        raise ValueError("render context hash does not match accepted v2 review")

    semantics_content, semantics_sha = _read_verified_json(
        render_semantics_review_path(repo_root)
    )
    if semantics_sha != _EXPECTED_SEMANTICS_REVIEW_SHA256:
        raise ValueError("render semantics hash does not match accepted v2 review")
    semantics = Phase3bRenderSemanticsReview.model_validate_json(semantics_content)

    policy = freeze_render_policy(
        semantics,
        semantics_review_sha256=semantics_sha,
        context_review_sha256=context_sha,
        dependency_manifest_sha256=dependency_sha,
    )
    manifest_path = render_policy_manifest_path(repo_root)
    policy_sha = write_json_with_sha256(manifest_path, policy)

    receipt = build_render_policy_receipt(
        policy,
        render_policy_manifest_sha256=policy_sha,
    )
    receipt_path = artifacts / "phase3b_render_policy_freeze_receipt_v1.json"
    receipt_sha = write_json_with_sha256(receipt_path, receipt)

    truth_table = {
        item.expression: item.result for item in policy.conditional_decisions
    }
    version_rows = {
        item.api_version: item.end_of_support for item in policy.api_version_rows
    }

    print(f"PHASE3B_RENDER_POLICY_SOURCE_DEPENDENCY_SHA256={dependency_sha}")
    print(f"PHASE3B_RENDER_POLICY_SOURCE_CONTEXT_SHA256={context_sha}")
    print(f"PHASE3B_RENDER_POLICY_SOURCE_SEMANTICS_SHA256={semantics_sha}")
    print(f"PHASE3B_RENDER_POLICY_TARGET_HOST={policy.target_host}")
    print(f"PHASE3B_RENDER_POLICY_CURRENT_VERSION={policy.current_version}")
    print(f"PHASE3B_RENDER_POLICY_VERSION_SHORT_NAME={policy.version_short_name}")
    print(
        "PHASE3B_RENDER_POLICY_SUPPORTED_API_VERSIONS="
        f"{json.dumps(policy.supported_api_versions)}"
    )
    print(f"PHASE3B_RENDER_POLICY_LATEST_API_VERSION={policy.latest_api_version}")
    print(f"PHASE3B_RENDER_POLICY_DEFAULT_API_VERSION={policy.default_rest_api_version}")
    print(
        "PHASE3B_RENDER_POLICY_INITIAL_VERSION_DATE="
        f"{policy.initial_rest_versioning_release_date}"
    )
    print(
        "PHASE3B_RENDER_POLICY_INITIAL_VERSION_DATE_LONG="
        f"{policy.initial_rest_versioning_release_date_long}"
    )
    print(
        "PHASE3B_RENDER_POLICY_VERSION_ROWS="
        f"{json.dumps(version_rows, sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_POLICY_CONDITIONAL_TRUTH_TABLE="
        f"{json.dumps(truth_table, sort_keys=True)}"
    )
    print(f"PHASE3B_RENDER_POLICY_SECRET_RESOLUTION={policy.secret_resolution_policy}")
    print(f"PHASE3B_RENDER_POLICY_AUTOTITLE={policy.autotitle_policy}")
    print(
        "PHASE3B_RENDER_POLICY_SITE_RENDERER_EQUIVALENCE_CLAIMED="
        f"{str(policy.site_renderer_equivalence_claimed).lower()}"
    )
    print(f"PHASE3B_RENDER_POLICY_FREEZE_STATUS={policy.freeze_status}")
    print("PHASE3B_RENDERING_AUTHORIZED=true")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDER_POLICY_MANIFEST_SHA256={policy_sha}")
    print(f"PHASE3B_RENDER_POLICY_FREEZE_RECEIPT_SHA256={receipt_sha}")


if __name__ == "__main__":
    main()
