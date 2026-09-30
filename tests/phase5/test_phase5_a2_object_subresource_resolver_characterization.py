from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.a2_object_subresource_resolver_characterization import (
    Phase5A2ObjectSubresourceResolverCharacterizationV1,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_a2_object_subresource_resolver_characterization_v1.json"
)


def _load_report() -> Phase5A2ObjectSubresourceResolverCharacterizationV1:
    return Phase5A2ObjectSubresourceResolverCharacterizationV1.model_validate_json(
        REPORT_PATH.read_bytes()
    )


def test_a2_characterization_artifact_and_sidecar_are_self_consistent() -> None:
    report = _load_report()
    digest = hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()
    sidecar = REPORT_PATH.with_suffix(
        REPORT_PATH.suffix + ".sha256"
    )

    assert sidecar.read_text(encoding="utf-8").strip() == (
        f"{digest}  {REPORT_PATH.name}"
    )
    assert report.run_validity == "VALID"


def test_a2_scientific_disposition_reconciles_with_gate() -> None:
    report = _load_report()

    passed = (
        report.fixed_fixture_expectation_mismatch_count == 0
        and report.fixed_fixture_false_confident_count == 0
        and report.fixed_fixture_nondeterministic_count == 0
        and report.invitation_correct_resolution_count == 2
        and report.development_false_confident_count == 0
        and report.development_nondeterministic_count == 0
    )

    assert report.characterization_passed is passed
    assert report.scientific_disposition == (
        "PASS" if passed else "REJECT"
    )


def test_a2_preserves_sealed_and_runtime_boundaries() -> None:
    report = _load_report()

    assert report.candidate_implemented is True
    assert report.candidate_executed is True

    assert report.hard_coded_invitation_target_used is False
    assert report.evaluator_fields_passed_to_candidate is False
    assert report.parameter_sweep_executed is False
    assert report.provider_invoked is False

    assert report.post_reject_confirmation_inspected is False
    assert report.post_reject_confirmation_executed is False
    assert report.held_out_case_content_read is False
    assert report.held_out_outcomes_exposed is False

    assert report.runtime_resolver_changed is False
    assert report.runtime_retriever_changed is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_a2_terminates_at_baseline_readiness_review() -> None:
    report = _load_report()

    assert report.baseline_readiness_review_required is True
    assert report.automatic_a3_authorized is False
