from __future__ import annotations

import hashlib
from functools import cache
from pathlib import Path

from rag_reliability.evaluation.semantic_runtime_development_confirmation import (
    Phase5DevelopmentConfirmationReport,
    materialize_phase5_semantic_runtime_development_confirmation,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT / "artifacts" / "development" / "phase5_semantic_runtime_development_confirmation_v1.json"
)


@cache
def _materialized() -> tuple[
    Phase5DevelopmentConfirmationReport,
    str,
]:
    return materialize_phase5_semantic_runtime_development_confirmation(ROOT)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_development_confirmation_binds_frozen_candidate() -> None:
    report, _digest = _materialized()

    assert report.protocol_sha256 == (
        "b36813907d2f581e6cfd559b96978bb93cc00855655c2204905a0e33126e6931"
    )
    assert report.protocol_freeze_sha256 == (
        "b3401a81900d63cc612fb7855b52a13c9af376efc47a97c1aebda6a17cd273a0"
    )
    assert report.promoted_retrieval_sha256 == (
        "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
    )
    assert report.candidate_retrieval_top_k == 20
    assert report.candidate_context_max_evidence_items == 15
    assert report.candidate_context_max_budget == 69663


def test_development_confirmation_reconciles_decision() -> None:
    report, _digest = _materialized()

    assert report.development_case_count == 24
    assert report.answerable_case_count == 20
    assert report.refusal_case_count == 4
    assert report.required_evidence_reference_count == 25

    integrity_failure = (
        report.fallback_order_mismatch_count > 0 or report.nondeterministic_case_count > 0
    )

    if integrity_failure:
        assert report.confirmation_decision == "STOP_AND_REFRAME"
    elif report.confirmation_gate_passed:
        assert report.confirmation_decision == "CONFIRM"
    else:
        assert report.confirmation_decision == "REJECT"


def test_development_confirmation_preserves_nonclaims() -> None:
    report, _digest = _materialized()

    assert report.development_gold_used_for_confirmation_only is True
    assert report.development_gold_used_for_tuning is False
    assert report.tuning_parameters_changed is False
    assert report.evaluator_fields_passed_to_candidate is False
    assert report.held_out_outcomes_exposed is False
    assert report.provider_invoked is False
    assert report.runtime_retriever_integrated is False
    assert report.runtime_configuration_materialized is False
    assert report.semantic_runtime_capacity_gate_satisfied is False
    assert report.semantic_runtime_configuration_selected is False
    assert report.semantic_runtime_configuration_frozen is False
    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_development_confirmation_artifact_hash_matches_bytes() -> None:
    _report, digest = _materialized()
    assert digest == _sha256(REPORT_PATH)
