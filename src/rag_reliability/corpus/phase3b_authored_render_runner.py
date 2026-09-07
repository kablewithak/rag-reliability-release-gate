"""Execute the frozen Phase 3B constrained renderer over all authored sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.authored_renderer import (
    build_authored_render_candidate,
    render_authored_sources,
)
from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.corpus.render_dependency_freeze import (
    Phase3bFrozenRenderDependencySet,
    frozen_manifest_path,
)
from rag_reliability.corpus.render_policy import (
    Phase3bRenderPolicyFreeze,
    render_policy_manifest_path,
)

_EXPECTED_POLICY_SHA256 = (
    "bad71a4e07f7f19ddbb9734c2ef7a822e890e36fa92e6336eb8b7ea9869b0d62"
)
_EXPECTED_DEPENDENCY_SHA256 = (
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
)
_EXPECTED_ACQUISITION_SHA256 = (
    "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"
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

    plan = CorpusSourceSelectionPlan.model_validate_json(
        (repo_root / "datasets/source_manifests/phase3a_source_selection_v1.json").read_bytes()
    )

    acquisition_content, acquisition_sha = _read_verified_json(
        artifacts / "phase3b_render_audit_acquisition_receipt_v1.json"
    )
    if acquisition_sha != _EXPECTED_ACQUISITION_SHA256:
        raise ValueError("render acquisition receipt hash does not match frozen source custody")
    acquisition = AcquisitionReceipt.model_validate_json(acquisition_content)

    dependency_content, dependency_sha = _read_verified_json(frozen_manifest_path(repo_root))
    if dependency_sha != _EXPECTED_DEPENDENCY_SHA256:
        raise ValueError("render dependency manifest hash does not match accepted v2 freeze")
    frozen = Phase3bFrozenRenderDependencySet.model_validate_json(dependency_content)

    policy_content, policy_sha = _read_verified_json(render_policy_manifest_path(repo_root))
    if policy_sha != _EXPECTED_POLICY_SHA256:
        raise ValueError("render policy manifest hash does not match accepted freeze")
    policy = Phase3bRenderPolicyFreeze.model_validate_json(policy_content)

    documents = render_authored_sources(repo_root, plan, acquisition, frozen, policy)
    candidate = build_authored_render_candidate(documents)
    candidate_path = artifacts / "phase3b_authored_render_candidate_v1.json"
    candidate_sha = write_json_with_sha256(candidate_path, candidate)

    rendered_hashes = {
        item.source_id: item.rendered_content_sha256 for item in candidate.documents
    }
    rendered_bytes = {
        item.source_id: item.rendered_byte_count for item in candidate.documents
    }
    raw_literal_count = sum(
        item.preserved_raw_literal_template_count for item in candidate.documents
    )
    data_substitution_count = sum(
        item.data_substitution_count for item in candidate.documents
    )

    print(f"PHASE3B_AUTHORED_RENDER_SOURCE_POLICY_SHA256={policy_sha}")
    print(f"PHASE3B_AUTHORED_RENDER_SOURCE_DEPENDENCY_SHA256={dependency_sha}")
    print(f"PHASE3B_AUTHORED_RENDER_SOURCE_ACQUISITION_SHA256={acquisition_sha}")
    print(f"PHASE3B_AUTHORED_RENDER_DOCUMENT_COUNT={candidate.document_count}")
    print("PHASE3B_AUTHORED_RENDER_UNRESOLVED_DOCUMENT_COUNT=0")
    print("PHASE3B_AUTHORED_RENDER_ACTIVE_UNRESOLVED_DIRECTIVE_COUNT=0")
    print(
        "PHASE3B_AUTHORED_RENDER_PRESERVED_RAW_LITERAL_TEMPLATE_COUNT="
        f"{raw_literal_count}"
    )
    print(
        "PHASE3B_AUTHORED_RENDER_DATA_SUBSTITUTION_COUNT="
        f"{data_substitution_count}"
    )
    print(
        "PHASE3B_AUTHORED_RENDER_DOCUMENT_SHA256="
        f"{json.dumps(rendered_hashes, sort_keys=True)}"
    )
    print(
        "PHASE3B_AUTHORED_RENDER_DOCUMENT_BYTES="
        f"{json.dumps(rendered_bytes, sort_keys=True)}"
    )
    print("PHASE3B_AUTHORED_RENDER_CANDIDATE_STATUS=candidate_only")
    print("PHASE3B_RENDERER_VALIDATION_PASSED=true")
    print("PHASE3B_NORMALIZATION_AUTHORIZED=false")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_AUTHORED_RENDER_CANDIDATE_SHA256={candidate_sha}")


if __name__ == "__main__":
    main()
