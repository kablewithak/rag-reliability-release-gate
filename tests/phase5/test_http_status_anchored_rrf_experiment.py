from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.http_status_anchored_rrf_experiment import (
    Phase5HttpStatusAnchoredRrfConfig,
    Phase5HttpStatusPromotionGate,
    _query_status_codes,
    materialize_phase5_http_status_anchored_rrf_experiment,
)

ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_http_status_anchored_rrf_experiment_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_status_code_extraction_is_bounded() -> None:
    assert _query_status_codes(
        "HTTP 451 and 404 under version 2026-03-10"
    ) == (
        "404",
        "451",
    )

    assert _query_status_codes(
        "version 2026-03-10 without an HTTP code"
    ) == ()


def test_candidate_is_fixed_and_not_swept() -> None:
    config = Phase5HttpStatusAnchoredRrfConfig()

    assert config.status_code_range == "100-599"
    assert config.exact_status_match_required is True
    assert (
        config.non_status_queries_preserve_rrf_order
        is True
    )
    assert config.parameter_sweep_used is False
    assert (
        config.tuning_parameter_optimization_used
        is False
    )


def test_promotion_gate_is_predeclared_against_rrf() -> None:
    gate = Phase5HttpStatusPromotionGate()

    assert gate.full_gold_cases_at_k20_required == 15
    assert gate.micro_gold_recall_at_k20_required == "1.0"
    assert gate.maximum_raw_top_k_allowed == 20
    assert gate.maximum_eligible_items_allowed == 20
    assert (
        gate.maximum_context_prefix_characters_exclusive
        == 102463
    )
    assert gate.regressed_cases_allowed == 0
    assert gate.non_status_order_preservation_required is True


def test_experiment_is_deterministic() -> None:
    first = (
        materialize_phase5_http_status_anchored_rrf_experiment(
            ROOT
        )
    )

    second = (
        materialize_phase5_http_status_anchored_rrf_experiment(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[1] == _sha256(
        REPORT_PATH
    )


def test_experiment_binds_exact_rrf_baseline() -> None:
    report, _digest = (
        materialize_phase5_http_status_anchored_rrf_experiment(
            ROOT
        )
    )

    assert (
        report.rrf_baseline_sha256
        == "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    )

    assert report.rrf_maximum_minimum_raw_top_k == 23
    assert (
        report.rrf_maximum_minimum_eligible_items
        == 21
    )
    assert (
        report.rrf_maximum_context_prefix_characters
        == 102463
    )


def test_experiment_is_tuning_only_and_offline() -> None:
    report, _digest = (
        materialize_phase5_http_status_anchored_rrf_experiment(
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


def test_non_status_queries_preserve_rrf_order() -> None:
    report, _digest = (
        materialize_phase5_http_status_anchored_rrf_experiment(
            ROOT
        )
    )

    assert (
        report.non_status_order_preserved_case_count
        == report.non_status_case_count
    )
    assert report.all_non_status_orders_preserved is True


def test_experiment_does_not_mutate_runtime() -> None:
    report, _digest = (
        materialize_phase5_http_status_anchored_rrf_experiment(
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


def test_gate_result_reconciles() -> None:
    report, _digest = (
        materialize_phase5_http_status_anchored_rrf_experiment(
            ROOT
        )
    )

    assert report.promotion_gate_passed == (
        len(report.promotion_gate_failures) == 0
    )

    assert (
        report.improved_vs_rrf_case_count
        + report.unchanged_vs_rrf_case_count
        + report.regressed_vs_rrf_case_count
        + report.unretrievable_case_count
        == 15
    )
