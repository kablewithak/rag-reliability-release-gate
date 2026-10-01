from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.source_companion_rescue_characterization import (
    Phase5SourceCompanionRescueCharacterizationV1,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_source_companion_rescue_characterization_v1.json"
)


def _load_report(
) -> Phase5SourceCompanionRescueCharacterizationV1:
    return (
        Phase5SourceCompanionRescueCharacterizationV1.model_validate_json(
            REPORT_PATH.read_bytes()
        )
    )


def test_source_companion_artifact_and_sidecar_are_self_consistent() -> None:
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


def test_source_companion_disposition_reconciles_with_frozen_gate() -> None:
    report = _load_report()

    passed = (
        report.targeted_cross_cutting_cases_recovered_k20 == 2
        and report.development_k20_regression_count == 0
        and report.tuning_k20_regression_count == 0
        and report.nondeterministic_case_count == 0
        and report.evaluator_leakage_count == 0
    )

    assert report.characterization_passed is passed
    assert report.scientific_disposition == (
        "PASS"
        if passed
        else "REJECT"
    )


def test_source_companion_preserves_sealed_boundaries() -> None:
    report = _load_report()

    assert report.candidate_implemented is True
    assert report.candidate_executed is True

    assert report.composition_authorized is False
    assert report.composed_candidate_executed is False

    assert report.post_reject_confirmation_inspected is False
    assert report.post_reject_confirmation_executed is False
    assert report.held_out_case_content_read is False
    assert report.held_out_outcomes_exposed is False

    assert report.provider_invoked is False
    assert report.runtime_retriever_changed is False
    assert report.retrieval_configuration_selected is False
    assert report.semantic_runtime_configuration_selected is False

    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_source_companion_terminates_at_readiness_review() -> None:
    report = _load_report()

    assert report.baseline_readiness_review_required is True
    assert report.automatic_composition_authorized is False
    assert report.automatic_successor_experiment_authorized is False
