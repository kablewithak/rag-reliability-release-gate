"""Generate the corrected Phase 3B render-semantics review inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.corpus.render_context_review import build_review_source_units
from rag_reliability.corpus.render_dependency_freeze import (
    Phase3bFrozenRenderDependencySet,
    frozen_manifest_path,
)
from rag_reliability.corpus.render_semantics_review import (
    SemanticConstructKind,
    build_render_semantics_review,
)

_EXPECTED_DEPENDENCY_MANIFEST_SHA256 = (
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
)
_EXPECTED_CONTEXT_REVIEW_SHA256 = (
    "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
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


def render_context_review_path(repo_root: Path) -> Path:
    """Return the corrected v2 render-context evidence path."""

    return repo_root / "artifacts" / "development" / "phase3b_render_context_review_v2.json"


def render_semantics_review_path(repo_root: Path) -> Path:
    """Return the corrected v2 render-semantics evidence path."""

    return repo_root / "artifacts" / "development" / "phase3b_render_semantics_review_v2.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    artifacts = repo_root / "artifacts" / "development"

    context_path = render_context_review_path(repo_root)
    _, context_sha = _read_verified_json(context_path)
    if context_sha != _EXPECTED_CONTEXT_REVIEW_SHA256:
        raise ValueError("render context review hash does not match accepted v2 evidence")

    frozen_path = frozen_manifest_path(repo_root)
    frozen_content, frozen_sha = _read_verified_json(frozen_path)
    if frozen_sha != _EXPECTED_DEPENDENCY_MANIFEST_SHA256:
        raise ValueError("render dependency manifest hash does not match reviewed v2 freeze")
    frozen = Phase3bFrozenRenderDependencySet.model_validate_json(frozen_content)

    plan = CorpusSourceSelectionPlan.model_validate_json(
        (repo_root / "datasets/source_manifests/phase3a_source_selection_v1.json").read_bytes()
    )
    acquisition = AcquisitionReceipt.model_validate_json(
        (artifacts / "phase3b_render_audit_acquisition_receipt_v1.json").read_bytes()
    )
    units = build_review_source_units(repo_root, plan, acquisition, frozen)
    review = build_render_semantics_review(
        units,
        frozen,
        source_render_context_review_sha256=context_sha,
        source_dependency_manifest_sha256=frozen_sha,
    )

    output = render_semantics_review_path(repo_root)
    review_sha = write_json_with_sha256(output, review)

    occurrence_counts: Counter[SemanticConstructKind] = Counter()
    values_by_kind: dict[SemanticConstructKind, list[str]] = {}
    for record in review.records:
        occurrence_counts[record.construct_kind] += record.occurrence_count
        values_by_kind.setdefault(record.construct_kind, []).append(
            f"{record.construct_name}:{record.value}"
        )

    print(f"PHASE3B_RENDER_SEMANTICS_SOURCE_CONTEXT_SHA256={context_sha}")
    print(f"PHASE3B_RENDER_SEMANTICS_SOURCE_DEPENDENCY_SHA256={frozen_sha}")
    print(
        "PHASE3B_RENDER_SEMANTICS_ASSIGNMENT_EXPRESSION_COUNT="
        f"{review.assignment_expression_count}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_ASSIGNMENT_OCCURRENCE_COUNT="
        f"{occurrence_counts['assignment_expression']}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_CONDITIONAL_EXPRESSION_COUNT="
        f"{review.conditional_expression_count}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_CONDITIONAL_OCCURRENCE_COUNT="
        f"{occurrence_counts['conditional_expression']}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_ITERATION_EXPRESSION_COUNT="
        f"{review.iteration_expression_count}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_ITERATION_OCCURRENCE_COUNT="
        f"{occurrence_counts['iteration_expression']}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_VARIANT_ARGUMENT_COUNT="
        f"{review.variant_argument_count}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_PRESENTATION_ARGUMENT_COUNT="
        f"{review.presentation_argument_count}"
    )
    print(f"PHASE3B_RENDER_SEMANTICS_AUTOTITLE_TARGET_COUNT={review.autotitle_target_count}")
    print(
        "PHASE3B_RENDER_SEMANTICS_ASSIGNMENT_EXPRESSIONS="
        f"{json.dumps(values_by_kind.get('assignment_expression', []), sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_CONDITIONAL_EXPRESSIONS="
        f"{json.dumps(values_by_kind.get('conditional_expression', []), sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_ITERATION_EXPRESSIONS="
        f"{json.dumps(values_by_kind.get('iteration_expression', []), sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_VARIANT_ARGUMENTS="
        f"{json.dumps(values_by_kind.get('variant_argument', []), sort_keys=True)}"
    )
    print(
        "PHASE3B_RENDER_SEMANTICS_PRESENTATION_ARGUMENTS="
        f"{json.dumps(values_by_kind.get('presentation_argument', []), sort_keys=True)}"
    )
    print("PHASE3B_RENDER_SEMANTICS_SUPERSEDES_VERSION=phase3b-render-semantics-review-v1")
    print("PHASE3B_RENDER_SEMANTICS_SUPERSESSION_REASON=liquid_trim_marker_parser_repair")
    print("PHASE3B_RENDER_SEMANTICS_REVIEW_STATUS=candidate_only")
    print("PHASE3B_RENDER_POLICY_FREEZE_REQUIRED=true")
    print("PHASE3B_RENDERING_AUTHORIZED=false")
    print("PHASE3B_FULL_INGESTION_READY=false")
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDER_SEMANTICS_REVIEW_SHA256={review_sha}")


if __name__ == "__main__":
    main()
