from __future__ import annotations

import asyncio
from pathlib import Path

from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    _build_materialization,
)

ROOT = Path(__file__).resolve().parents[2]


def test_real_b0_materialization_is_deterministic_and_closes_coverage() -> None:
    first_fixture, first_coverage = asyncio.run(
        _build_materialization(
            ROOT
        )
    )
    second_fixture, second_coverage = asyncio.run(
        _build_materialization(
            ROOT
        )
    )

    assert first_fixture == second_fixture
    assert first_coverage == second_coverage

    assert first_coverage.authorized_case_count == 42
    assert (
        first_coverage.provider_reaching_case_count
        + first_coverage.pre_provider_refusal_case_count
        + first_coverage.unexpected_prefix_error_count
        == 42
    )

    assert first_coverage.unexpected_prefix_error_count == 0
    assert first_coverage.query_disposition_conflict_count == 0
    assert first_coverage.duplicate_response_conflict_count == 0

    assert first_coverage.materialization_decision == "PASS"
    assert first_coverage.replay_fixture_materialized is True
    assert first_fixture is not None

    assert (
        len(first_fixture.entries)
        == first_coverage.distinct_provider_query_count
        == first_coverage.fixture_entry_count
    )

    assert first_coverage.live_provider_call_count == 0
    assert first_coverage.evaluator_fields_used_for_fixture_authoring is False
    assert first_coverage.protected_roles_accessed is False

    assert first_coverage.baseline_execution_authorized is False
    assert first_coverage.b0_executed is False
    assert first_coverage.held_out_outcomes_exposed is False
