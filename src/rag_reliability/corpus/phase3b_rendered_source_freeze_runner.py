"""Materialize and freeze exact Phase 3B rendered authored sources."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Literal

from rag_reliability.corpus.authored_renderer import Phase3bAuthoredRenderCandidate
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
from rag_reliability.corpus.rendered_source_freeze import (
    Phase3bRenderedSourceFreezeReceipt,
    freeze_rendered_authored_sources,
    rendered_source_manifest_path,
)

_EXPECTED_CANDIDATE_SHA256: Literal[
    "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"
] = "1b4464c00db84b7ad909f16be7c4d03d793d243913f833f547a37084e9372912"
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

    candidate_content, candidate_sha = _read_verified_json(
        artifacts / "phase3b_authored_render_candidate_v1.json"
    )
    if candidate_sha != _EXPECTED_CANDIDATE_SHA256:
        raise ValueError("authored render candidate hash does not match accepted evidence")
    candidate = Phase3bAuthoredRenderCandidate.model_validate_json(candidate_content)

    plan = CorpusSourceSelectionPlan.model_validate_json(
        (repo_root / "datasets/source_manifests/phase3a_source_selection_v1.json").read_bytes()
    )

    acquisition_content, acquisition_sha = _read_verified_json(
        artifacts / "phase3b_render_audit_acquisition_receipt_v1.json"
    )
    if acquisition_sha != _EXPECTED_ACQUISITION_SHA256:
        raise ValueError("acquisition receipt hash does not match frozen custody")
    acquisition = AcquisitionReceipt.model_validate_json(acquisition_content)

    dependency_content, dependency_sha = _read_verified_json(frozen_manifest_path(repo_root))
    if dependency_sha != _EXPECTED_DEPENDENCY_SHA256:
        raise ValueError("dependency manifest hash does not match v2 freeze")
    frozen_dependencies = Phase3bFrozenRenderDependencySet.model_validate_json(
        dependency_content
    )

    policy_content, policy_sha = _read_verified_json(render_policy_manifest_path(repo_root))
    if policy_sha != _EXPECTED_POLICY_SHA256:
        raise ValueError("render policy hash does not match frozen policy")
    policy = Phase3bRenderPolicyFreeze.model_validate_json(policy_content)

    frozen = freeze_rendered_authored_sources(
        repo_root,
        plan,
        acquisition,
        frozen_dependencies,
        policy,
        candidate,
        candidate_sha256=candidate_sha,
    )
    manifest_path = rendered_source_manifest_path(repo_root)
    manifest_sha = write_json_with_sha256(manifest_path, frozen)

    receipt = Phase3bRenderedSourceFreezeReceipt(
        receipt_version="phase3b-rendered-source-freeze-receipt-v1",
        source_authored_render_candidate_sha256=_EXPECTED_CANDIDATE_SHA256,
        rendered_source_manifest_sha256=manifest_sha,
    )
    receipt_path = artifacts / "phase3b_rendered_source_freeze_receipt_v1.json"
    receipt_sha = write_json_with_sha256(receipt_path, receipt)

    print(f"PHASE3B_RENDERED_SOURCE_SOURCE_CANDIDATE_SHA256={candidate_sha}")
    print(f"PHASE3B_RENDERED_SOURCE_SOURCE_POLICY_SHA256={policy_sha}")
    print(f"PHASE3B_RENDERED_SOURCE_SOURCE_DEPENDENCY_SHA256={dependency_sha}")
    print(f"PHASE3B_RENDERED_SOURCE_SOURCE_ACQUISITION_SHA256={acquisition_sha}")
    print(f"PHASE3B_RENDERED_SOURCE_DOCUMENT_COUNT={frozen.document_count}")
    print(f"PHASE3B_RENDERED_SOURCE_IDENTITY_MATCH_COUNT={frozen.identity_match_count}")
    print("PHASE3B_RENDERED_SOURCE_UNRESOLVED_DOCUMENT_COUNT=0")
    print("PHASE3B_RENDERED_SOURCE_FREEZE_STATUS=frozen")
    print("PHASE3B_NORMALIZATION_AUTHORIZED=true")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDERED_SOURCE_MANIFEST_SHA256={manifest_sha}")
    print(f"PHASE3B_RENDERED_SOURCE_FREEZE_RECEIPT_SHA256={receipt_sha}")


if __name__ == "__main__":
    main()
