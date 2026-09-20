from __future__ import annotations

from pathlib import Path

from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.evaluation.post_reject_confirmation_freeze import (
    load_and_validate_post_reject_confirmation_suite,
)

ROOT = Path(__file__).resolve().parents[2]


def test_fresh_confirmation_suite_validates() -> None:
    suite = load_and_validate_post_reject_confirmation_suite(ROOT)
    assert suite.case_count == 24
    assert suite.cluster_count == 12
    assert suite.answerable_case_count == 20
    assert suite.refusal_case_count == 4
    assert suite.exact_development_query_reuse_count == 0
    assert suite.exact_tuning_query_reuse_count == 0
    assert suite.held_out_case_content_read is False
    assert suite.failure_specific_development_evidence_opened is False


def test_fresh_confirmation_has_two_cases_per_cluster() -> None:
    suite = load_and_validate_post_reject_confirmation_suite(ROOT)
    clusters = tuple(record.cluster_id for record in suite.records)
    assert len(set(clusters)) == 12
    assert all(clusters.count(cluster_id) == 2 for cluster_id in set(clusters))


def test_fresh_confirmation_refusals_have_no_answer_gold() -> None:
    suite = load_and_validate_post_reject_confirmation_suite(ROOT)
    refusals = tuple(
        record.case
        for record in suite.records
        if record.case.expected_response_mode is ResponseMode.REFUSE
    )
    assert len(refusals) == 4
    for case in refusals:
        assert case.required_fact_ids == ()
        assert case.required_evidence_ids == ()
        assert case.required_source_ids == ()
        assert case.gold_fact_rubric == ()


def test_fresh_confirmation_runtime_projection_is_strict() -> None:
    suite = load_and_validate_post_reject_confirmation_suite(ROOT)
    for record in suite.records:
        runtime = record.case.to_runtime_input()
        assert runtime.case_id == record.case.case_id
        assert runtime.query == record.case.query
