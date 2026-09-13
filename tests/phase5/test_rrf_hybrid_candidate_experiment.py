from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    Phase5RrfPromotionGate,
    materialize_phase5_rrf_hybrid_candidate_experiment,
)

ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_rrf_hybrid_candidate_experiment_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_rrf_candidate_is_fixed_and_not_swept() -> None:
    config = Phase5RrfHybridCandidateConfig()

    assert config.fusion_constant == 60
    assert config.lexical_weight == 1
    assert config.bm25_weight == 1
    assert config.parameter_sweep_used is False
    assert (
        config.tuning_parameter_optimization_used
        is False
    )


def test_promotion_gate_is_predeclared() -> None:
    gate = Phase5RrfPromotionGate()

    assert gate.full_gold_cases_at_k20_required == 15
    assert gate.micro_gold_recall_at_k20_required == "1.0"
    assert gate.maximum_raw_top_k_allowed == 20
    assert gate.maximum_eligible_items_allowed == 20
    assert (
        gate.maximum_context_prefix_characters_exclusive
        == 133880
    )
    assert gate.unretrievable_cases_allowed == 0
    assert gate.filter_ineligible_cases_allowed == 0


def test_rrf_experiment_is_deterministic() -> None:
    first = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            ROOT
        )
    )

    second = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[1] == _sha256(
        REPORT_PATH
    )


def test_rrf_experiment_binds_exact_prior_evidence() -> None:
    report, _digest = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            ROOT
        )
    )

    assert (
        report.lexical_baseline_sha256
        == "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"
    )
    assert (
        report.bm25_experiment_sha256
        == "ef58106aef6087f7e4761df6afbe1e0c3819ffa8304c7b11c4c446faa6437370"
    )


def test_rrf_experiment_is_tuning_only_and_offline() -> None:
    report, _digest = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            ROOT
        )
    )

    assert report.evidence_class == "intervention_tuning_only"
    assert report.tuning_case_count == 18
    assert report.answerable_case_count == 15
    assert report.refusal_case_count == 3

    assert report.development_gold_used is False
    assert report.held_out_outcomes_exposed is False
    assert report.provider_invoked is False


def test_rrf_experiment_does_not_mutate_runtime_state() -> None:
    report, _digest = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            ROOT
        )
    )

    assert report.runtime_retriever_changed is False
    assert report.retrieval_configuration_selected is False
    assert (
        report.semantic_runtime_configuration_selected
        is False
    )

    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_rrf_gate_result_reconciles() -> None:
    report, _digest = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            ROOT
        )
    )

    assert report.promotion_gate_passed == (
        len(report.promotion_gate_failures) == 0
    )

    assert (
        report.improved_vs_lexical_case_count
        + report.unchanged_vs_lexical_case_count
        + report.regressed_vs_lexical_case_count
        + report.unretrievable_case_count
        == 15
    )
