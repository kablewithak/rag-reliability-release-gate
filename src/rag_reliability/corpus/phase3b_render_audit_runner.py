"""Run the Phase 3B authored-source renderability audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rag_reliability.corpus.acquisition import acquire_selection
from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_audit import (
    build_authored_renderability_audit,
    sorted_unique,
    write_json_with_sha256,
)


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _write_acquisition_receipt(path: Path, receipt: AcquisitionReceipt) -> str:
    content = _stable_json_bytes(receipt.model_dump(mode="json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    sidecar = path.with_suffix(path.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {path.name}\n", encoding="utf-8", newline="\n")
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    plan_path = (
        repo_root
        / "datasets"
        / "source_manifests"
        / "phase3a_source_selection_v1.json"
    )
    plan = CorpusSourceSelectionPlan.model_validate_json(plan_path.read_bytes())

    receipt = acquire_selection(repo_root, plan)

    artifacts = repo_root / "artifacts" / "development"
    acquisition_path = artifacts / "phase3b_render_audit_acquisition_receipt_v1.json"
    acquisition_sha = _write_acquisition_receipt(acquisition_path, receipt)

    audit = build_authored_renderability_audit(
        repo_root,
        plan,
        receipt,
        acquisition_receipt_sha256=acquisition_sha,
    )
    audit_path = artifacts / "phase3b_authored_renderability_audit_v1.json"
    audit_sha = write_json_with_sha256(audit_path, audit)

    data_refs = sorted_unique(
        ref
        for item in audit.documents
        for ref in item.data_references
    )
    liquid_tags = sorted_unique(
        tag
        for item in audit.documents
        for tag in item.liquid_tags
    )
    template_variables = sorted_unique(
        variable
        for item in audit.documents
        for variable in item.template_variables
    )

    print(f"PHASE3B_RENDER_AUDIT_ACQUIRED_FILE_COUNT={len(receipt.files)}")
    print(f"PHASE3B_RENDER_AUDIT_AUTHORED_DOCUMENT_COUNT={audit.document_count}")
    print(
        "PHASE3B_RENDER_AUDIT_UNRESOLVED_DOCUMENT_COUNT="
        f"{audit.unresolved_document_count}"
    )
    print(
        "PHASE3B_RENDER_AUDIT_UNRESOLVED_DIRECTIVE_COUNT="
        f"{audit.total_unresolved_directive_count}"
    )
    print(
        "PHASE3B_RENDER_AUDIT_UNIQUE_DATA_REFERENCE_COUNT="
        f"{audit.unique_data_reference_count}"
    )
    print(
        "PHASE3B_RENDER_AUDIT_DATA_REFERENCES="
        f"{json.dumps(data_refs)}"
    )
    print(
        "PHASE3B_RENDER_AUDIT_LIQUID_TAGS="
        f"{json.dumps(liquid_tags)}"
    )
    print(
        "PHASE3B_RENDER_AUDIT_TEMPLATE_VARIABLES="
        f"{json.dumps(template_variables)}"
    )
    print(
        "PHASE3B_RENDER_DEPENDENCY_FREEZE_REQUIRED="
        f"{str(audit.render_dependency_freeze_required).lower()}"
    )
    print(
        "PHASE3B_FULL_INGESTION_READY="
        f"{str(audit.full_ingestion_ready).lower()}"
    )
    print("PHASE3B_CHUNKING_AUTHORIZED=false")
    print("PHASE3B_BASELINE_AUTHORIZED=false")
    print(f"PHASE3B_RENDER_AUDIT_ACQUISITION_SHA256={acquisition_sha}")
    print(f"PHASE3B_RENDER_AUDIT_SHA256={audit_sha}")


if __name__ == "__main__":
    main()
