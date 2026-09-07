"""Generate the Phase 3B render-context review inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.corpus.render_context_review import (
    build_render_context_review,
    build_review_source_units,
)
from rag_reliability.corpus.render_dependency_freeze import (
    Phase3bFrozenRenderDependencySet,
    frozen_manifest_path,
)

_EXPECTED_DEPENDENCY_MANIFEST_SHA256 = (
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
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

    plan = CorpusSourceSelectionPlan.model_validate_json(
        (repo_root / "datasets/source_manifests/phase3a_source_selection_v1.json").read_bytes()
    )
    acquisition = AcquisitionReceipt.model_validate_json(
        (artifacts / "phase3b_render_audit_acquisition_receipt_v1.json").read_bytes()
    )

    frozen_path = frozen_manifest_path(repo_root)
    frozen_content, frozen_sha = _read_verified_json(frozen_path)
    if frozen_sha != _EXPECTED_DEPENDENCY_MANIFEST_SHA256:
        raise ValueError("render dependency manifest hash does not match reviewed freeze")
    frozen = Phase3bFrozenRenderDependencySet.model_validate_json(frozen_content)

    units = build_review_source_units(repo_root, plan, acquisition, frozen)
    review = build_render_context_review(
        units,
        frozen,
        source_dependency_manifest_sha256=frozen_sha,
    )

    output = artifacts / "phase3b_render_context_review_v2.json"
    review_sha = write_json_with_sha256(output, review)

    liquid_counts = {
        record.construct_name: record.occurrence_count
        for record in review.records
        if record.construct_kind == "liquid_tag"
    }
    template_counts = {
        record.construct_name: record.occurrence_count
        for record in review.records
        if record.construct_kind == "template_variable"
    }
    decision_counts = Counter(record.decision_class for record in review.records)

    print(f"PHASE3B_RENDER_CONTEXT_SOURCE_DEPENDENCY_SHA256={frozen_sha}")
    print(f"PHASE3B_RENDER_CONTEXT_SOURCE_UNIT_COUNT={len(units)}")
    print(f"PHASE3B_RENDER_CONTEXT_LIQUID_TAG_COUNT={len(review.required_liquid_tags)}")
    print(
        "PHASE3B_RENDER_CONTEXT_TEMPLATE_VARIABLE_COUNT="
        f"{len(review.required_template_variables)}"
    )
    print(f"PHASE3B_RENDER_CONTEXT_LIQUID_OCCURRENCE_COUNT={review.liquid_occurrence_count}")
    print(
        "PHASE3B_RENDER_CONTEXT_TEMPLATE_OCCURRENCE_COUNT="
        f"{review.template_variable_occurrence_count}"
    )
    print(f"PHASE3B_RENDER_CONTEXT_AUTOTITLE_COUNT={review.autotitle_occurrence_count}")
    print(
        "PHASE3B_RENDER_CONTEXT_LIQUID_COUNTS="
        f"{json.dumps(liquid_counts, sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_CONTEXT_TEMPLATE_COUNTS="
        f"{json.dumps(template_counts, sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_CONTEXT_DECISION_CLASS_COUNTS="
        f"{json.dumps(dict(sorted(decision_counts.items())), sort_keys=True)}"
    )
    print("PHASE3B_RENDER_CONTEXT_REVIEW_STATUS=candidate_only")
    print("PHASE3B_RENDER_CONTEXT_FREEZE_REQUIRED=true")
    print("PHASE3B_RENDERING_AUTHORIZED=false")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDER_CONTEXT_REVIEW_SHA256={review_sha}")


if __name__ == "__main__":
    main()
