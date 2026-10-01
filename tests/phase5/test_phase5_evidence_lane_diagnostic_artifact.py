from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.evidence_lane_diagnostic import (
    Phase5EvidenceLaneDiagnosticV1,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_evidence_lane_diagnostic_v1.json"
)


def _load_report() -> Phase5EvidenceLaneDiagnosticV1:
    return Phase5EvidenceLaneDiagnosticV1.model_validate_json(
        REPORT_PATH.read_bytes()
    )


def test_evidence_lane_artifact_sidecar_is_self_consistent() -> None:
    report = _load_report()

    digest = hashlib.sha256(
        REPORT_PATH.read_bytes()
    ).hexdigest()

    sidecar = REPORT_PATH.with_suffix(
        REPORT_PATH.suffix + ".sha256"
    )

    assert sidecar.read_text(
        encoding="utf-8"
    ).strip() == (
        f"{digest}  {REPORT_PATH.name}"
    )

    assert report.run_validity == "VALID"


def test_evidence_lane_result_preserves_diagnostic_boundary() -> None:
    report = _load_report()

    assert report.diagnostic_implemented is True
    assert report.diagnostic_executed is True

    assert report.runtime_retriever_changed is False
    assert report.corpus_mutated is False
    assert report.chunking_policy_changed is False

    assert report.candidate_implemented is False
    assert report.candidate_executed is False
    assert report.composition_authorized is False

    assert report.post_reject_confirmation_inspected is False
    assert report.post_reject_confirmation_executed is False
    assert report.held_out_case_content_read is False
    assert report.held_out_outcomes_exposed is False

    assert report.provider_invoked is False
    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False


def test_evidence_lane_failed_case_decision_fork_reconciles() -> None:
    report = _load_report()

    failed = tuple(
        item
        for item in report.observations
        if item.role == "development"
        and item.previously_failed_development_case
    )

    assert len(failed) == 4

    recovered = sum(
        item.full_gold_native_lane_k20
        for item in failed
    )

    assert (
        report.failed_development_native_lane_recovered_count
        == recovered
    )

    assert (
        report.stratified_retrieval_candidate_hypothesis_supported
        is (recovered == 4)
    )

    assert report.baseline_readiness_review_required is True
    assert report.automatic_candidate_implementation_authorized is False
