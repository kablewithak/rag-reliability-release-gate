from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.operation_resolver_protocol_v2 import (
    Phase5OperationResolverProtocolV2,
    build_phase5_operation_resolver_protocol_v2,
)


def test_v2_records_exact_v1_supersession() -> None:
    protocol = build_phase5_operation_resolver_protocol_v2()

    assert protocol.supersedes_protocol_sha256 == (
        "373fc8abb9a6bc20c04b788ce1a67c26b468cd2d7f662ddd27d938d1084cf61e"
    )
    assert protocol.runtime_catalog_operation_count == 20
    assert protocol.superseded_fixture_ids == (
        "resolver-list-org-repositories",
        "resolver-create-repository-webhook",
    )


def test_v2_replacements_are_inside_runtime_catalog_contract() -> None:
    protocol = build_phase5_operation_resolver_protocol_v2()
    fixtures = {fixture.fixture_id: fixture for fixture in protocol.fixtures}

    assert "resolver-list-org-repositories" not in fixtures
    assert "resolver-create-repository-webhook" not in fixtures

    assert fixtures["resolver-list-pull-requests"].expected_operation_id == "pulls/list"
    assert fixtures["resolver-list-repository-attestations"].expected_operation_id == (
        "repos/list-attestations"
    )


def test_v2_preserves_v1_safety_and_acceptance_boundary() -> None:
    protocol = build_phase5_operation_resolver_protocol_v2()

    assert protocol.semantic_runtime_input_fields == ("query",)
    assert protocol.provider_calls_allowed is False
    assert protocol.parameter_sweep_allowed is False
    assert protocol.held_out_outcomes_exposed is False
    assert protocol.development_gold_used is False
    assert protocol.runtime_retriever_changed is False
    assert protocol.retrieval_configuration_selected is False
    assert protocol.baseline_execution_authorized is False
    assert protocol.acceptance.false_confident_resolution_tolerance == 0
    assert protocol.acceptance.nondeterministic_fixture_tolerance == 0
    assert protocol.acceptance.minimum_resolved_fixture_count == 5


def test_v2_cannot_reintroduce_superseded_fixture_by_payload_tampering() -> None:
    protocol = build_phase5_operation_resolver_protocol_v2()
    payload = protocol.model_dump(mode="json")
    payload["fixtures"][4]["fixture_id"] = "resolver-list-org-repositories"

    with pytest.raises(ValidationError, match="known invalid v1 fixture"):
        Phase5OperationResolverProtocolV2.model_validate(payload)
