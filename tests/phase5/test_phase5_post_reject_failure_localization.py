from __future__ import annotations

import hashlib
from functools import cache
from pathlib import Path

from rag_reliability.evaluation.post_reject_failure_localization import (
    Phase5PostRejectFailureLocalizationReportV1,
    materialize_phase5_post_reject_failure_localization,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "artifacts" / "development" / "phase5_post_reject_failure_localization_v1.json"


@cache
def _materialized() -> tuple[
    Phase5PostRejectFailureLocalizationReportV1,
    str,
]:
    return materialize_phase5_post_reject_failure_localization(ROOT)


def test_failure_localization_opens_exactly_four_rejected_cases() -> None:
    report, _digest = _materialized()

    assert report.failure_case_count == 4
    assert len(report.case_diagnostics) == 4
    assert report.development_spent_for_future_confirmation is True
    assert report.failure_specific_development_evidence_opened is True


def test_failure_localization_reconciles_recomputed_ranks() -> None:
    report, _digest = _materialized()

    for case in report.case_diagnostics:
        assert case.generic_fallback_exact is True
        assert case.missed_required_evidence_count >= 1

        for item in case.evidence:
            if item.missed_top20:
                assert item.candidate_rank > 20


def test_failure_localization_preserves_boundaries() -> None:
    report, _digest = _materialized()

    assert report.held_out_case_content_read is False
    assert report.held_out_outcomes_exposed is False
    assert report.candidate_retuning_performed is False
    assert report.parameter_sweep_performed is False
    assert report.new_candidate_executed is False
    assert report.next_intervention_selected is False
    assert report.provider_invoked is False
    assert report.semantic_runtime_configuration_selected is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_failure_localization_artifact_hash_matches_bytes() -> None:
    _report, digest = _materialized()

    assert digest == hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()
