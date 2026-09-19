from __future__ import annotations

import hashlib
from functools import cache
from pathlib import Path

from rag_reliability.evaluation.operation_aware_rrf_candidate_experiment import (
    Phase5OperationAwareRrfCandidateExperimentReport,
    materialize_phase5_operation_aware_rrf_candidate_experiment,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT / "artifacts" / "development" / "phase5_operation_aware_rrf_candidate_experiment_v1.json"
)


@cache
def _materialized() -> tuple[
    Phase5OperationAwareRrfCandidateExperimentReport,
    str,
]:
    return materialize_phase5_operation_aware_rrf_candidate_experiment(ROOT)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_candidate_experiment_binds_frozen_controls() -> None:
    report, _digest = _materialized()

    assert report.protocol_sha256 == (
        "d1ddc3cf8920f72612dbddef410d17260ca3b07e9a5d7d380bb8f4cfa3f7cb95"
    )
    assert report.protocol_freeze_receipt_sha256 == (
        "47fcbeacc808168bfd94f399b59b54c88aa4e16d3a7eaa55e8dc6ae4487caa98"
    )
    assert report.incumbent_rrf_sha256 == (
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    )


def test_candidate_experiment_reconciles_gate_and_decision() -> None:
    report, _digest = _materialized()

    assert report.answerable_case_count == 15
    assert report.required_evidence_reference_count == 18
    assert (
        report.resolved_case_count + report.ambiguous_case_count + report.unresolved_case_count
        == 15
    )
    assert report.promotion_gate_passed == (len(report.promotion_gate_failures) == 0)

    integrity_failure = (
        report.fallback_order_mismatch_count > 0 or report.nondeterministic_case_count > 0
    )

    if integrity_failure:
        assert report.experiment_decision == "STOP_AND_REFRAME"
    elif report.promotion_gate_passed:
        assert report.experiment_decision == "PROMOTE"
    else:
        assert report.experiment_decision == "REJECT"


def test_candidate_experiment_preserves_nonclaims() -> None:
    report, _digest = _materialized()

    assert report.evaluator_fields_passed_to_candidate is False
    assert report.development_gold_used is False
    assert report.held_out_outcomes_exposed is False
    assert report.provider_invoked is False
    assert report.runtime_retriever_changed is False
    assert report.retrieval_configuration_selected is False
    assert report.semantic_runtime_capacity_gate_satisfied is False
    assert report.semantic_runtime_configuration_selected is False
    assert report.semantic_runtime_configuration_frozen is False
    assert report.semantic_runtime_promotion_authorized is False
    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_candidate_experiment_artifact_hash_matches_bytes() -> None:
    _report, digest = _materialized()

    assert digest == _sha256(REPORT_PATH)
