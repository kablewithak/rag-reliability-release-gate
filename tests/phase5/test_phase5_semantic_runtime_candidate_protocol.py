from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.semantic_runtime_candidate_protocol import (
    Phase5SemanticRuntimeCandidateProtocolV1,
    build_phase5_semantic_runtime_candidate_protocol_v1,
)


def test_candidate_is_exactly_tuning_derived() -> None:
    protocol = build_phase5_semantic_runtime_candidate_protocol_v1()
    candidate = protocol.candidate

    assert candidate.retrieval_top_k == 20
    assert candidate.context_max_evidence_items == 15
    assert candidate.context_max_budget == 69663
    assert candidate.parameter_sweep_used is False
    assert candidate.candidate_count == 1


def test_development_is_confirmation_not_tuning() -> None:
    protocol = build_phase5_semantic_runtime_candidate_protocol_v1()
    gate = protocol.development_confirmation

    assert gate.answerable_development_case_count == 20
    assert gate.required_evidence_reference_count == 25
    assert gate.maximum_raw_top_k_allowed == 20
    assert gate.maximum_eligible_items_allowed == 15
    assert gate.maximum_context_prefix_characters_allowed == 69663
    assert gate.failure_policy == "stop_without_retuning"

    assert protocol.development_gold_used_for_confirmation_only is True
    assert protocol.development_gold_used_for_tuning is False
    assert protocol.tuning_parameters_mutable_after_failure is False


def test_provider_capacity_remains_blocked() -> None:
    gate = build_phase5_semantic_runtime_candidate_protocol_v1().provider_capacity

    assert gate.active_provider_blocker_code == "ModelArts.81111"
    assert gate.public_capacity_documentation_consistent is False
    assert gate.documentation_only_capacity_acceptance_allowed is False
    assert gate.live_capacity_probe_authorized_now is False
    assert gate.retry_or_workaround_authorized is False


def test_protocol_preserves_nonclaims() -> None:
    protocol = build_phase5_semantic_runtime_candidate_protocol_v1()

    assert protocol.runtime_retriever_integrated is False
    assert protocol.runtime_configuration_materialized is False
    assert protocol.semantic_runtime_configuration_selected is False
    assert protocol.semantic_runtime_configuration_frozen is False
    assert protocol.provider_invoked is False
    assert protocol.held_out_outcomes_exposed is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False


def test_protocol_rejects_development_retuning_tamper() -> None:
    protocol = build_phase5_semantic_runtime_candidate_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["development_gold_used_for_tuning"] = True

    with pytest.raises(ValidationError):
        Phase5SemanticRuntimeCandidateProtocolV1.model_validate(payload)


def test_protocol_rejects_live_probe_tamper() -> None:
    protocol = build_phase5_semantic_runtime_candidate_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["provider_capacity"]["live_capacity_probe_authorized_now"] = True

    with pytest.raises(ValidationError):
        Phase5SemanticRuntimeCandidateProtocolV1.model_validate(payload)
