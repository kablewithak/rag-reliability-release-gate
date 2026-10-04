from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.b0_specimen_authorization import (
    build_phase5_b0_specimen_and_authorization,
)

ROOT = Path(__file__).resolve().parents[2]


def test_b0_specimen_authorization_builds_without_execution() -> None:
    specimen, authorization = build_phase5_b0_specimen_and_authorization(
        ROOT,
        require_clean_tracked_worktree=False,
    )

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


def test_environment_capture_is_secret_safe() -> None:
    specimen, _authorization = build_phase5_b0_specimen_and_authorization(
        ROOT,
        require_clean_tracked_worktree=False,
    )

    payload = specimen.environment.model_dump_json()

    assert "HUAWEI_MAAS_API_KEY" not in payload
    assert specimen.environment.live_provider_credentials_required is False
    assert specimen.environment.live_provider_calls_authorized == 0
    assert specimen.environment.secrets_captured is False


def test_primary_and_replication_case_order_match() -> None:
    _specimen, authorization = build_phase5_b0_specimen_and_authorization(
        ROOT,
        require_clean_tracked_worktree=False,
    )

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
