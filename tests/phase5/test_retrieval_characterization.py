from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.retrieval_characterization import (
    materialize_phase5_tuning_retrieval_characterization,
)

ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_tuning_retrieval_characterization_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_characterization_is_deterministic() -> None:
    first = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    second = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[1] == _sha256(
        REPORT_PATH
    )


def test_characterization_is_tuning_only() -> None:
    report, _digest = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    assert report.evidence_class == "intervention_tuning_only"
    assert report.tuning_case_count == 18
    assert report.answerable_case_count == 15
    assert report.refusal_case_count == 3

    assert (
        report.development_gold_used_for_characterization
        is False
    )
    assert report.held_out_outcomes_exposed is False


def test_characterization_uses_existing_runtime_components() -> None:
    report, _digest = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    assert report.retriever_id == "lexical-v1"
    assert report.characterization_top_k == 1333
    assert report.source_policy_id == (
        "github-rest-current-v1"
    )
    assert report.corpus_chunk_count == 1333


def test_characterization_curve_is_fixed_and_exact() -> None:
    report, _digest = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    assert tuple(
        point.top_k
        for point in report.top_k_curve
    ) == (
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

    for point in report.top_k_curve:
        assert point.applicable_case_count == 15
        assert (
            point.retrieved_required_evidence_count
            <= point.required_evidence_reference_count
        )


def test_characterization_preserves_corpus_custody() -> None:
    report, _digest = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    assert report.all_chunk_content_hashes_verified is True
    assert (
        report.all_required_evidence_present_in_corpus
        is True
    )


def test_characterization_does_not_select_or_execute() -> None:
    report, _digest = (
        materialize_phase5_tuning_retrieval_characterization(
            ROOT
        )
    )

    assert report.retrieval_configuration_selected is False
    assert (
        report.semantic_runtime_configuration_selected
        is False
    )
    assert report.semantic_runtime_configuration_frozen is False

    assert report.provider_invoked is False
    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False
    assert report.release_eligible is False
