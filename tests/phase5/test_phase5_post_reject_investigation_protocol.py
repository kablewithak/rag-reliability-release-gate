from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.post_reject_investigation_protocol import (
    Phase5PostRejectInvestigationProtocolV1,
    build_phase5_post_reject_investigation_protocol_v1,
)


def test_protocol_preserves_pre_localization_boundary() -> None:
    protocol = build_phase5_post_reject_investigation_protocol_v1()

    assert protocol.rejected_candidate.full_gold_case_count_at_k20 == 16
    assert protocol.rejected_candidate.retrieved_required_evidence_count_at_k20 == 21
    assert protocol.rejected_candidate.worst_required_raw_rank == 49
    assert protocol.failure_localization_started is False
    assert protocol.development_spent_for_future_confirmation is False


def test_fresh_confirmation_is_reserved_before_diagnosis() -> None:
    protocol = build_phase5_post_reject_investigation_protocol_v1()
    reservation = protocol.fresh_confirmation

    assert reservation.role_id == "POST_REJECT_CONFIRMATION"
    assert reservation.case_count == 24
    assert reservation.cluster_count == 12
    assert reservation.answerable_case_count == 20
    assert reservation.refusal_case_count == 4

    assert reservation.failure_specific_development_evidence_allowed_during_authoring is False
    assert reservation.intervention_specific_behavior_allowed_during_authoring is False
    assert reservation.must_be_materialized_before_failure_localization is True
    assert reservation.must_be_frozen_before_failure_localization is True


def test_development_becomes_spent_after_localization() -> None:
    boundary = build_phase5_post_reject_investigation_protocol_v1().development_reuse

    assert (
        boundary.state_after_failure_localization_starts
        == "diagnostic_only_spent_for_future_confirmation"
    )
    assert boundary.may_inform_failure_taxonomy_after_reservation is True
    assert boundary.may_inform_next_intervention_after_reservation is True
    assert boundary.may_confirm_intervention_informed_by_its_failures is False
    assert boundary.may_be_relabelled_as_independent_later is False


def test_held_out_remains_quarantined() -> None:
    held_out = build_phase5_post_reject_investigation_protocol_v1().held_out

    assert held_out.outcomes_exposed is False
    assert held_out.case_content_allowed_for_post_reject_authoring is False
    assert held_out.case_content_allowed_for_failure_localization is False
    assert held_out.intervention_design_allowed_to_use_held_out is False
    assert held_out.may_execute_before_semantic_runtime_freeze is False
    assert held_out.may_execute_before_provider_capacity_gate is False


def test_localization_cannot_start_without_fresh_confirmation() -> None:
    protocol = build_phase5_post_reject_investigation_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["failure_localization_started"] = True
    payload["development_spent_for_future_confirmation"] = True

    with pytest.raises(ValidationError):
        Phase5PostRejectInvestigationProtocolV1.model_validate(payload)
