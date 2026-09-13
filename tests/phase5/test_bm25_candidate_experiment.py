from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    materialize_phase5_bm25_candidate_experiment,
)

ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_bm25_candidate_experiment_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_candidate_config_is_fixed_and_not_swept() -> None:
    config = Phase5Bm25CandidateConfig()

    assert config.retriever_id == (
        "bm25-evaluation-candidate-v1"
    )
    assert config.top_k == 1333
    assert config.k1 == 1.2
    assert config.b == 0.75
    assert config.parameter_sweep_used is False
    assert (
        config.tuning_parameter_optimization_used
        is False
    )


def test_experiment_is_deterministic() -> None:
    first = (
        materialize_phase5_bm25_candidate_experiment(
            ROOT
        )
    )

    second = (
        materialize_phase5_bm25_candidate_experiment(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[1] == _sha256(
        REPORT_PATH
    )


def test_experiment_binds_exact_lexical_baseline() -> None:
    report, _digest = (
        materialize_phase5_bm25_candidate_experiment(
            ROOT
        )
    )

    assert (
        report.baseline_characterization_sha256
        == "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"
    )

    assert report.baseline_maximum_minimum_raw_top_k == 31
    assert (
        report.baseline_maximum_minimum_eligible_items
        == 26
    )
    assert (
        report.baseline_maximum_context_prefix_characters
        == 133880
    )


def test_experiment_is_tuning_only_and_offline() -> None:
    report, _digest = (
        materialize_phase5_bm25_candidate_experiment(
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


def test_experiment_does_not_select_runtime_configuration() -> None:
    report, _digest = (
        materialize_phase5_bm25_candidate_experiment(
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


def test_candidate_curve_uses_same_fixed_cutoffs() -> None:
    report, _digest = (
        materialize_phase5_bm25_candidate_experiment(
            ROOT
        )
    )

    expected = (
        2,
        3,
        5,
        10,
        20,
        50,
        100,
        200,
        500,
        1333,
    )

    assert tuple(
        point.top_k
        for point in report.baseline_top_k_curve
    ) == expected

    assert tuple(
        point.top_k
        for point in report.candidate_top_k_curve
    ) == expected

    assert (
        report.improved_case_count
        + report.unchanged_case_count
        + report.regressed_case_count
        + report.unretrievable_case_count
        == 15
    )
