from __future__ import annotations

import asyncio
from functools import lru_cache
from pathlib import Path

import pytest

from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.evaluation.b0_authorization_models import (
    B0AuthorizationError,
    B0FileBinding,
    Phase5B0ExecutionAuthorizationV1,
)
from rag_reliability.evaluation.b0_execution_preflight import (
    _verify_file_bindings,
    preflight_execution_slot_with_objects,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
    _build_materialization,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    Phase5B0RuntimeProjectionV1,
    load_phase5_b0_runtime_projection,
)
from rag_reliability.evaluation.b0_specimen_authorization import (
    load_coverage,
)

ROOT = Path(__file__).resolve().parents[2]
_AUTHORIZATION_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_b0_execution_authorization_v1.json"
)


@lru_cache(maxsize=1)
def _ci_portable_objects() -> tuple[
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
    Phase5B0RuntimeProjectionV1,
    RuntimeCaseInput,
]:
    authorization = Phase5B0ExecutionAuthorizationV1.model_validate_json(
        _AUTHORIZATION_PATH.read_bytes()
    )
    coverage = load_coverage(ROOT)

    fixture, rebuilt_coverage = asyncio.run(
        _build_materialization(ROOT)
    )

    if fixture is None:
        raise AssertionError("deterministic B0 fixture did not materialize in memory")

    if rebuilt_coverage != coverage:
        raise AssertionError(
            "in-memory B0 coverage does not match tracked frozen coverage"
        )

    projection = load_phase5_b0_runtime_projection(ROOT)
    case = projection.development.cases[0]

    return authorization, coverage, fixture, projection, case


def test_primary_slot_preflight_passes_for_exact_authorized_case() -> None:
    authorization, coverage, fixture, projection, case = _ci_portable_objects()

    slot = preflight_execution_slot_with_objects(
        authorization=authorization,
        coverage=coverage,
        fixture=fixture,
        arm="primary",
        case_id=case.case_id,
        role=projection.development.role,
        query=case.query,
        started_slot_ids=set(),
        primary_batch_valid_and_custodied=False,
    )

    assert slot.arm == "primary"
    assert slot.case_id == case.case_id


def test_protected_role_is_rejected() -> None:
    authorization, coverage, fixture, _projection, case = _ci_portable_objects()

    with pytest.raises(B0AuthorizationError, match="unauthorized role"):
        preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="primary",
            case_id=case.case_id,
            role="held_out_release_case",
            query=case.query,
            started_slot_ids=set(),
            primary_batch_valid_and_custodied=False,
        )


def test_consumed_slot_is_rejected() -> None:
    authorization, coverage, fixture, projection, case = _ci_portable_objects()
    slot_id = f"primary:{case.case_id}"

    with pytest.raises(B0AuthorizationError, match="already consumed"):
        preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="primary",
            case_id=case.case_id,
            role=projection.development.role,
            query=case.query,
            started_slot_ids={slot_id},
            primary_batch_valid_and_custodied=False,
        )


def test_exhausted_budget_is_rejected() -> None:
    authorization, coverage, fixture, projection, case = _ci_portable_objects()
    started = {slot.slot_id for slot in authorization.slots}

    with pytest.raises(B0AuthorizationError, match="budget exhausted"):
        preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="primary",
            case_id=case.case_id,
            role=projection.development.role,
            query=case.query,
            started_slot_ids=started,
            primary_batch_valid_and_custodied=False,
        )


def test_replication_before_valid_primary_custody_is_rejected() -> None:
    authorization, coverage, fixture, projection, case = _ci_portable_objects()

    with pytest.raises(B0AuthorizationError, match="valid, custodied G5N primary"):
        preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="replication",
            case_id=case.case_id,
            role=projection.development.role,
            query=case.query,
            started_slot_ids=set(),
            primary_batch_valid_and_custodied=False,
        )


def test_wrong_query_is_rejected_before_provider() -> None:
    authorization, coverage, fixture, projection, case = _ci_portable_objects()

    with pytest.raises(B0AuthorizationError, match="query does not match"):
        preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="primary",
            case_id=case.case_id,
            role=projection.development.role,
            query="unauthorized replacement query",
            started_slot_ids=set(),
            primary_batch_valid_and_custodied=False,
        )


def test_bound_file_drift_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "bound.txt"
    target.write_text("changed", encoding="utf-8")

    with pytest.raises(B0AuthorizationError, match="bound file drifted"):
        _verify_file_bindings(
            tmp_path,
            (
                B0FileBinding(
                    path="bound.txt",
                    sha256=(
                        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    ),
                ),
            ),
        )
