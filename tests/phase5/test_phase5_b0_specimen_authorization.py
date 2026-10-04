from __future__ import annotations

import asyncio
from pathlib import Path

from rag_reliability.evaluation.b0_authorization_models import (
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0SpecimenV1,
    model_sha256,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    _build_materialization,
)
from rag_reliability.evaluation.b0_specimen_authorization import (
    load_coverage,
)

ROOT = Path(__file__).resolve().parents[2]
_SPECIMEN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_b0_specimen_v1.json"
)
_AUTHORIZATION_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_b0_execution_authorization_v1.json"
)


def _frozen_objects() -> tuple[
    Phase5B0SpecimenV1,
    Phase5B0ExecutionAuthorizationV1,
]:
    specimen = Phase5B0SpecimenV1.model_validate_json(
        _SPECIMEN_PATH.read_bytes()
    )
    authorization = Phase5B0ExecutionAuthorizationV1.model_validate_json(
        _AUTHORIZATION_PATH.read_bytes()
    )
    return specimen, authorization


def test_frozen_b0_specimen_authorization_is_execution_ready() -> None:
    specimen, authorization = _frozen_objects()

    assert specimen.baseline_execution_authorized is False
    assert specimen.b0_executed is False
    assert specimen.held_out_included is False
    assert specimen.post_reject_confirmation_included is False

    assert authorization.baseline_execution_authorized is True
    assert authorization.b0_executed is False
    assert authorization.live_provider_calls_authorized == 0
    assert authorization.protected_case_execution_authorized is False

    assert authorization.authorized_case_count == 42
    assert authorization.primary_slot_count == 42
    assert authorization.replication_slot_count == 42
    assert authorization.maximum_total_case_starts == 84
    assert len(authorization.slots) == 84

    assert authorization.specimen_sha256 == model_sha256(specimen)


def test_environment_capture_is_secret_safe() -> None:
    specimen, _authorization = _frozen_objects()

    payload = specimen.environment.model_dump_json()

    assert "HUAWEI_MAAS_API_KEY" not in payload
    assert specimen.environment.live_provider_credentials_required is False
    assert specimen.environment.live_provider_calls_authorized == 0
    assert specimen.environment.secrets_captured is False


def test_primary_and_replication_case_order_match() -> None:
    _specimen, authorization = _frozen_objects()

    primary = tuple(
        slot.case_id
        for slot in authorization.slots
        if slot.arm == "primary"
    )
    replication = tuple(
        slot.case_id
        for slot in authorization.slots
        if slot.arm == "replication"
    )

    assert len(primary) == 42
    assert primary == replication
    assert len(set(primary)) == 42


def test_private_fixture_is_reconstructible_without_publication() -> None:
    specimen, authorization = _frozen_objects()
    tracked_coverage = load_coverage(ROOT)

    fixture, rebuilt_coverage = asyncio.run(
        _build_materialization(ROOT)
    )

    assert fixture is not None
    assert rebuilt_coverage == tracked_coverage
    assert model_sha256(fixture) == specimen.replay_fixture_sha256
    assert model_sha256(fixture) == authorization.replay_fixture_sha256

    assert rebuilt_coverage.evaluator_fields_used_for_fixture_authoring is False
    assert rebuilt_coverage.live_provider_call_count == 0
    assert rebuilt_coverage.protected_roles_accessed is False
