"""Superseding Phase 5 operation-resolver protocol after v1 fixture correction."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import NonEmptyStr
from rag_reliability.evaluation.operation_resolver_protocol import (
    OperationResolverFixture,
    Phase5OperationResolverProtocolBase,
    build_phase5_operation_resolver_protocol_v1,
)

_SUPERSEDED_PROTOCOL_SHA256: Literal[
    "373fc8abb9a6bc20c04b788ce1a67c26b468cd2d7f662ddd27d938d1084cf61e"
] = "373fc8abb9a6bc20c04b788ce1a67c26b468cd2d7f662ddd27d938d1084cf61e"

_SUPERSEDED_FIXTURE_IDS = (
    "resolver-list-org-repositories",
    "resolver-create-repository-webhook",
)


class Phase5OperationResolverProtocolV2(Phase5OperationResolverProtocolBase):
    """Correct v1 fixtures without widening the resolver runtime boundary."""

    protocol_version: Literal[
        "phase5-operation-resolver-protocol-v2"
    ] = "phase5-operation-resolver-protocol-v2"

    supersedes_protocol_sha256: Literal[
        "373fc8abb9a6bc20c04b788ce1a67c26b468cd2d7f662ddd27d938d1084cf61e"
    ] = _SUPERSEDED_PROTOCOL_SHA256

    correction_reason: Literal[
        "v1 fixtures referenced operations absent from the frozen runtime catalog"
    ] = "v1 fixtures referenced operations absent from the frozen runtime catalog"

    runtime_catalog_operation_count: Literal[20] = 20

    superseded_fixture_ids: tuple[NonEmptyStr, ...] = _SUPERSEDED_FIXTURE_IDS

    @model_validator(mode="after")
    def validate_supersession(self) -> Self:
        if self.superseded_fixture_ids != _SUPERSEDED_FIXTURE_IDS:
            raise ValueError("resolver v2 superseded fixture identities drifted")

        fixture_ids = {fixture.fixture_id for fixture in self.fixtures}
        if fixture_ids & set(_SUPERSEDED_FIXTURE_IDS):
            raise ValueError("resolver v2 retained a known invalid v1 fixture")

        expected_operations = {
            fixture.expected_operation_id
            for fixture in self.fixtures
            if fixture.expected_operation_id is not None
        }
        if "pulls/list" not in expected_operations:
            raise ValueError("resolver v2 must cover pulls/list")
        if "repos/list-attestations" not in expected_operations:
            raise ValueError("resolver v2 must cover repos/list-attestations")

        return self


def build_phase5_operation_resolver_protocol_v2() -> Phase5OperationResolverProtocolV2:
    """Build the corrected protocol while preserving v1 safety semantics."""

    v1 = build_phase5_operation_resolver_protocol_v1()

    replacements = {
        "resolver-list-org-repositories": OperationResolverFixture(
            fixture_id="resolver-list-pull-requests",
            origin="engineering_boundary_fixture",
            query="How do I list pull requests for a repository?",
            expected_status="resolved",
            expected_operation_id="pulls/list",
            purpose="clear list operation represented in the frozen runtime catalog",
        ),
        "resolver-create-repository-webhook": OperationResolverFixture(
            fixture_id="resolver-list-repository-attestations",
            origin="engineering_boundary_fixture",
            query="How do I list attestations for a repository?",
            expected_status="resolved",
            expected_operation_id="repos/list-attestations",
            purpose="repository subresource operation represented in the frozen runtime catalog",
        ),
    }

    fixtures = tuple(
        replacements.get(fixture.fixture_id, fixture)
        for fixture in v1.fixtures
    )

    return Phase5OperationResolverProtocolV2(
        allowed_corpus_fields=v1.allowed_corpus_fields,
        forbidden_evaluator_fields=v1.forbidden_evaluator_fields,
        fixtures=fixtures,
        acceptance=v1.acceptance,
    )
