"""Pre-execution protocol for the Phase 5 runtime operation resolver.

This module freezes the resolver question, legal runtime inputs, prohibited
 evaluator inputs, fixed characterization fixtures, and acceptance semantics
before resolver implementation or retrieval-ranking mutation.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr

_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
_TUNING_SUITE_SHA256: Literal[
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
] = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
_RRF_INCUMBENT_SHA256: Literal[
    "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
] = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"

_ALLOWED_CORPUS_FIELDS = (
    "chunk_kind",
    "linked_operation_ids",
    "semantic_families",
    "evidence_scope.source_state",
    "evidence_scope.authority_level",
    "evidence_scope.data_role",
    "operation_core.content.method",
    "operation_core.content.path",
    "operation_core.content.operation.operationId",
    "operation_core.content.operation.summary",
)

_FORBIDDEN_EVALUATOR_FIELDS = (
    "required_source_ids",
    "required_evidence_ids",
    "gold_facts",
    "expected_response_mode",
    "evaluation_role_as_retrieval_truth",
    "gold_operation_id",
    "scoring_labels",
    "held_out_outcomes",
    "post_run_evaluator_annotations",
)


ResolverExpectation = Literal[
    "resolved",
    "ambiguous",
    "unresolved",
]
FixtureOrigin = Literal[
    "engineering_boundary_fixture",
    "frozen_tuning_diagnostic",
]


class OperationResolverFixture(ContractModel):
    """One fixed engineering characterization fixture."""

    fixture_id: NonEmptyStr
    origin: FixtureOrigin
    query: NonEmptyStr
    expected_status: ResolverExpectation
    expected_operation_id: NonEmptyStr | None = None
    purpose: NonEmptyStr

    @model_validator(mode="after")
    def validate_expectation(self) -> Self:
        if self.expected_status == "resolved":
            if self.expected_operation_id is None:
                raise ValueError(
                    "resolved resolver fixture requires expected_operation_id"
                )
            return self

        if self.expected_operation_id is not None:
            raise ValueError(
                "ambiguous/unresolved fixture cannot prescribe one operation"
            )

        return self


class OperationResolverAcceptanceContract(ContractModel):
    """Predeclared resolver acceptance and stopping contract."""

    false_confident_resolution_tolerance: Literal[0] = 0
    evaluator_leakage_tolerance: Literal[0] = 0
    nondeterministic_fixture_tolerance: Literal[0] = 0
    deterministic_repeat_count: Literal[3] = 3
    minimum_resolved_fixture_count: Literal[5] = 5

    resolution_coverage_is_descriptive: Literal[True] = True
    one_hundred_percent_resolution_required: Literal[False] = False

    ambiguous_runtime_behavior: Literal[
        "retain_generic_rrf_path"
    ] = "retain_generic_rrf_path"
    unresolved_runtime_behavior: Literal[
        "retain_generic_rrf_path"
    ] = "retain_generic_rrf_path"

    stop_if_safe_resolution_not_demonstrated: Literal[True] = True
    retrieval_promotion_authorized: Literal[False] = False


class Phase5OperationResolverProtocolBase(ContractModel):
    """Frozen-intent protocol preceding operation-resolver implementation."""

    protocol_status: Literal[
        "draft_unfrozen"
    ] = "draft_unfrozen"

    question: Literal[
        "Can operation identity be derived legally and deterministically "
        "from runtime-visible information?"
    ] = (
        "Can operation identity be derived legally and deterministically "
        "from runtime-visible information?"
    )

    chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = _CHUNK_MANIFEST_SHA256

    tuning_suite_sha256: Literal[
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
    ] = _TUNING_SUITE_SHA256

    rrf_incumbent_artifact_sha256: Literal[
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    ] = _RRF_INCUMBENT_SHA256

    semantic_runtime_input_fields: tuple[NonEmptyStr, ...] = (
        "query",
    )
    case_id_used_for_semantic_resolution: Literal[False] = False

    catalog_source: Literal[
        "frozen_phase3d_current_authoritative_operation_core_chunks"
    ] = "frozen_phase3d_current_authoritative_operation_core_chunks"

    allowed_corpus_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=len(_ALLOWED_CORPUS_FIELDS),
        max_length=len(_ALLOWED_CORPUS_FIELDS),
    )
    forbidden_evaluator_fields: tuple[NonEmptyStr, ...] = Field(
        min_length=len(_FORBIDDEN_EVALUATOR_FIELDS),
        max_length=len(_FORBIDDEN_EVALUATOR_FIELDS),
    )

    fixtures: tuple[OperationResolverFixture, ...] = Field(
        min_length=10,
        max_length=10,
    )
    acceptance: OperationResolverAcceptanceContract

    provider_calls_allowed: Literal[False] = False
    parameter_sweep_allowed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    development_gold_used: Literal[False] = False

    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_protocol_boundary(self) -> Self:
        if self.semantic_runtime_input_fields != ("query",):
            raise ValueError(
                "resolver semantic input must remain query-only"
            )

        if self.allowed_corpus_fields != _ALLOWED_CORPUS_FIELDS:
            raise ValueError(
                "resolver allowed corpus field contract drifted"
            )

        if self.forbidden_evaluator_fields != _FORBIDDEN_EVALUATOR_FIELDS:
            raise ValueError(
                "resolver forbidden evaluator field contract drifted"
            )

        fixture_ids = tuple(
            fixture.fixture_id
            for fixture in self.fixtures
        )
        if len(fixture_ids) != len(set(fixture_ids)):
            raise ValueError(
                "resolver fixture IDs must be unique"
            )

        tuning_diagnostics = tuple(
            fixture
            for fixture in self.fixtures
            if fixture.origin == "frozen_tuning_diagnostic"
        )
        if len(tuning_diagnostics) != 1:
            raise ValueError(
                "resolver protocol must contain exactly one frozen TUNING diagnostic fixture"
            )

        resolved_fixture_count = sum(
            fixture.expected_status == "resolved"
            for fixture in self.fixtures
        )
        if resolved_fixture_count < self.acceptance.minimum_resolved_fixture_count:
            raise ValueError(
                "resolver fixtures do not demonstrate enough useful resolved cases"
            )

        return self



class Phase5OperationResolverProtocolV1(Phase5OperationResolverProtocolBase):
    """Frozen-intent v1 protocol preceding operation-resolver implementation."""

    protocol_version: Literal[
        "phase5-operation-resolver-protocol-v1"
    ] = "phase5-operation-resolver-protocol-v1"


def build_phase5_operation_resolver_protocol_v1() -> Phase5OperationResolverProtocolV1:
    """Build the fixed resolver characterization protocol before implementation."""

    fixtures = (
        OperationResolverFixture(
            fixture_id="resolver-hard-create-in-org-451",
            origin="frozen_tuning_diagnostic",
            query=(
                "A legacy contract for Create an organization repository does not list "
                "HTTP 451. Under the frozen current 2026-03-10 operation contract, is "
                "HTTP 451 now a documented response, and how is that response represented?"
            ),
            expected_status="resolved",
            expected_operation_id="repos/create-in-org",
            purpose="known hard case without exposing evaluator evidence IDs to runtime",
        ),
        OperationResolverFixture(
            fixture_id="resolver-exact-operation-id",
            origin="engineering_boundary_fixture",
            query="For repos/create-in-org, which REST route is used?",
            expected_status="resolved",
            expected_operation_id="repos/create-in-org",
            purpose="exact operation identifier should resolve deterministically",
        ),
        OperationResolverFixture(
            fixture_id="resolver-method-path",
            origin="engineering_boundary_fixture",
            query="Which operation corresponds to POST /orgs/{org}/repos?",
            expected_status="resolved",
            expected_operation_id="repos/create-in-org",
            purpose="method and route are runtime-visible structural identifiers",
        ),
        OperationResolverFixture(
            fixture_id="resolver-create-issue",
            origin="engineering_boundary_fixture",
            query="How do I create an issue for a repository?",
            expected_status="resolved",
            expected_operation_id="issues/create",
            purpose="clear natural-language operation outside the hard-case operation",
        ),
        OperationResolverFixture(
            fixture_id="resolver-list-org-repositories",
            origin="engineering_boundary_fixture",
            query="How do I list repositories for an organization?",
            expected_status="resolved",
            expected_operation_id="repos/list-for-org",
            purpose="same resource family with a different action must remain distinguishable",
        ),
        OperationResolverFixture(
            fixture_id="resolver-create-repository-webhook",
            origin="engineering_boundary_fixture",
            query="How do I create a repository webhook?",
            expected_status="resolved",
            expected_operation_id="repos/create-webhook",
            purpose="operation phrase must discriminate a repository subresource",
        ),
        OperationResolverFixture(
            fixture_id="resolver-generic-create-repository",
            origin="engineering_boundary_fixture",
            query="How do I create a repository?",
            expected_status="ambiguous",
            purpose="generic repository creation must not force one scope",
        ),
        OperationResolverFixture(
            fixture_id="resolver-multi-operation-compare",
            origin="engineering_boundary_fixture",
            query=(
                "Compare creating a repository in an organization with creating one "
                "for the authenticated user."
            ),
            expected_status="ambiguous",
            purpose="multi-operation queries must not collapse to one confident operation",
        ),
        OperationResolverFixture(
            fixture_id="resolver-status-only",
            origin="engineering_boundary_fixture",
            query="Is HTTP 451 documented?",
            expected_status="unresolved",
            purpose="status-code rarity alone must not select an operation",
        ),
        OperationResolverFixture(
            fixture_id="resolver-operation-free-guidance",
            origin="engineering_boundary_fixture",
            query="What authentication headers are required for GitHub REST API requests?",
            expected_status="unresolved",
            purpose="operation-free guidance must retain generic retrieval",
        ),
    )

    return Phase5OperationResolverProtocolV1(
        allowed_corpus_fields=_ALLOWED_CORPUS_FIELDS,
        forbidden_evaluator_fields=_FORBIDDEN_EVALUATOR_FIELDS,
        fixtures=fixtures,
        acceptance=OperationResolverAcceptanceContract(),
    )
