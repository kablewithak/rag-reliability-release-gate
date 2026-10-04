from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.b0_runtime_projection import (
    _project_payload,
    load_phase5_b0_runtime_projection,
)

ROOT = Path(__file__).resolve().parents[2]


def test_b0_projection_contains_only_case_id_and_query() -> None:
    projection = load_phase5_b0_runtime_projection(
        ROOT
    )

    assert len(projection.development.cases) == 24
    assert len(projection.tuning.cases) == 18

    all_cases = (
        *projection.development.cases,
        *projection.tuning.cases,
    )

    assert len(all_cases) == 42
    assert len({case.case_id for case in all_cases}) == 42

    for case in all_cases:
        assert set(case.model_dump()) == {
            "case_id",
            "query",
        }


def test_projection_output_is_invariant_to_forbidden_case_fields() -> None:
    base = {
        "case_count": 1,
        "records": [
            {
                "case": {
                    "case_id": "case-a",
                    "query": "What is supported?",
                    "gold_fact_rubric": ["gold-a"],
                    "required_evidence_ids": ["evidence-a"],
                    "expected_response_mode": "answer",
                }
            }
        ],
    }

    changed = {
        "case_count": 1,
        "records": [
            {
                "case": {
                    "case_id": "case-a",
                    "query": "What is supported?",
                    "gold_fact_rubric": ["completely-different-gold"],
                    "required_evidence_ids": ["different-evidence"],
                    "expected_response_mode": "refuse",
                    "scoring_notes": "also changed",
                }
            }
        ],
    }

    assert _project_payload(
        base,
        expected_case_count=1,
    ) == _project_payload(
        changed,
        expected_case_count=1,
    )
