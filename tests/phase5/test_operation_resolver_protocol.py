from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.operation_resolver_protocol import (
    Phase5OperationResolverProtocolV1,
    build_phase5_operation_resolver_protocol_v1,
)


def test_resolver_protocol_binds_runtime_visible_boundary() -> None:
    protocol = build_phase5_operation_resolver_protocol_v1()

    assert protocol.semantic_runtime_input_fields == ("query",)
    assert protocol.case_id_used_for_semantic_resolution is False
    assert protocol.catalog_source == (
        "frozen_phase3d_current_authoritative_operation_core_chunks"
    )

    assert "gold_operation_id" in protocol.forbidden_evaluator_fields
    assert "required_evidence_ids" in protocol.forbidden_evaluator_fields
    assert "held_out_outcomes" in protocol.forbidden_evaluator_fields


def test_resolver_protocol_has_fixed_bounded_characterization() -> None:
    protocol = build_phase5_operation_resolver_protocol_v1()

    assert len(protocol.fixtures) == 10
    assert protocol.parameter_sweep_allowed is False
    assert protocol.provider_calls_allowed is False
    assert protocol.held_out_outcomes_exposed is False
    assert protocol.development_gold_used is False

    tuning_fixtures = tuple(
        fixture
        for fixture in protocol.fixtures
        if fixture.origin == "frozen_tuning_diagnostic"
    )
    assert len(tuning_fixtures) == 1
    assert tuning_fixtures[0].fixture_id == (
        "resolver-hard-create-in-org-451"
    )


def test_resolver_acceptance_is_conservative() -> None:
    protocol = build_phase5_operation_resolver_protocol_v1()
    acceptance = protocol.acceptance

    assert acceptance.false_confident_resolution_tolerance == 0
    assert acceptance.evaluator_leakage_tolerance == 0
    assert acceptance.nondeterministic_fixture_tolerance == 0
    assert acceptance.deterministic_repeat_count == 3
    assert acceptance.minimum_resolved_fixture_count == 5
    assert acceptance.one_hundred_percent_resolution_required is False
    assert acceptance.ambiguous_runtime_behavior == "retain_generic_rrf_path"
    assert acceptance.unresolved_runtime_behavior == "retain_generic_rrf_path"
    assert acceptance.retrieval_promotion_authorized is False


def test_resolver_protocol_binds_rrf_incumbent_without_promoting_it() -> None:
    protocol = build_phase5_operation_resolver_protocol_v1()

    assert protocol.rrf_incumbent_artifact_sha256 == (
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    )
    assert protocol.runtime_retriever_changed is False
    assert protocol.retrieval_configuration_selected is False
    assert protocol.semantic_runtime_configuration_frozen is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.b0_executed is False
    assert protocol.release_eligible is False


def test_resolved_fixture_requires_expected_operation() -> None:
    protocol = build_phase5_operation_resolver_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["fixtures"][0]["expected_operation_id"] = None

    with pytest.raises(
        ValidationError,
        match="resolved resolver fixture requires expected_operation_id",
    ):
        Phase5OperationResolverProtocolV1.model_validate(payload)


def test_forbidden_field_contract_cannot_be_relaxed_by_payload_tampering() -> None:
    protocol = build_phase5_operation_resolver_protocol_v1()
    payload = protocol.model_dump(mode="json")
    payload["forbidden_evaluator_fields"].remove("gold_operation_id")

    with pytest.raises(ValidationError):
        Phase5OperationResolverProtocolV1.model_validate(payload)
