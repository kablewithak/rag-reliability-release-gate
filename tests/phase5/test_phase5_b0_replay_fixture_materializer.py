from __future__ import annotations

import asyncio
from pathlib import Path

from rag_reliability.config.identity import (
    ContextConfig,
    RetrievalConfig,
    SourcePolicyConfig,
)
from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import (
    ContextBuildRequest,
    ContextBundle,
    RetrievalRequest,
    RetrievalResult,
    RetrievedEvidence,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    B0ReplayFixtureMaterializer,
    _deduplicate_provider_candidates,
    _load_frozen_controls,
    _ProviderCandidate,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    B0ProjectedSuite,
    B0Role,
    Phase5B0RuntimeProjectionV1,
)
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import ContextBudgetExhaustedError
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import ReplayEntry

ROOT = Path(__file__).resolve().parents[2]


def _current_item(
    evidence_id: str = "current-evidence",
    content: str = "Supported current content.",
) -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id=evidence_id,
        source_ids=("source-a",),
        document_ids=("document-a",),
        content=content,
        rank=1,
        score=1.0,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
        synthetic_overlay=False,
        eligible_as_final_citation=True,
    )


def _historical_item() -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id="historical-evidence",
        source_ids=("source-a",),
        document_ids=("document-a",),
        content="Historical content.",
        rank=1,
        score=1.0,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.HISTORICAL_COMPARISON,
        product_scope="api.github.com",
        api_version_or_snapshot="2022-11-28",
        synthetic_overlay=False,
        eligible_as_final_citation=True,
    )


class _StaticRetriever:
    def __init__(
        self,
        items_by_query: dict[str, tuple[RetrievedEvidence, ...]],
    ) -> None:
        self._items_by_query = items_by_query
        self._config = RetrievalConfig(
            retriever_id="test-retriever",
            top_k=20,
        )

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        return RetrievalResult(
            items=self._items_by_query.get(
                request.query,
                (),
            )
        )


class _ContextErrorBuilder:
    def __init__(self) -> None:
        self._config = ContextConfig(
            builder_id="bounded-context-v1",
            budget_unit_id="characters",
            max_budget=69663,
            max_evidence_items=15,
        )

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def build(
        self,
        request: ContextBuildRequest,
    ) -> ContextBundle:
        raise ContextBudgetExhaustedError(
            "synthetic context error"
        )


def _suite(
    *,
    role: B0Role,
    suite_sha: str,
    pairs: tuple[tuple[str, str], ...],
) -> B0ProjectedSuite:
    return B0ProjectedSuite(
        role=role,
        suite_sha256=suite_sha,
        cases=tuple(
            RuntimeCaseInput(
                case_id=case_id,
                query=query,
            )
            for case_id, query in pairs
        ),
    )


def test_equal_duplicate_provider_entries_deduplicate() -> None:
    entry = ReplayEntry(
        query="same query",
        answer_text="same answer",
        cited_evidence_ids=("evidence-a",),
    )

    result = _deduplicate_provider_candidates(
        (
            _ProviderCandidate(
                case_id="case-a",
                query="same query",
                entry=entry,
            ),
            _ProviderCandidate(
                case_id="case-b",
                query="same query",
                entry=entry,
            ),
        )
    )

    assert len(result.entries) == 1
    assert result.distinct_provider_query_count == 1
    assert result.duplicate_provider_case_count == 1
    assert result.duplicate_response_conflict_count == 0


def test_conflicting_duplicate_provider_entries_reject_fixture_entries() -> None:
    result = _deduplicate_provider_candidates(
        (
            _ProviderCandidate(
                case_id="case-a",
                query="same query",
                entry=ReplayEntry(
                    query="same query",
                    answer_text="answer one",
                    cited_evidence_ids=("evidence-a",),
                ),
            ),
            _ProviderCandidate(
                case_id="case-b",
                query="same query",
                entry=ReplayEntry(
                    query="same query",
                    answer_text="answer two",
                    cited_evidence_ids=("evidence-b",),
                ),
            ),
        )
    )

    assert result.entries == ()
    assert result.distinct_provider_query_count == 1
    assert result.duplicate_provider_case_count == 1
    assert result.duplicate_response_conflict_count == 1


def _synthetic_projection(
) -> tuple[
    Phase5B0RuntimeProjectionV1,
    tuple[tuple[str, str], ...],
]:
    protocol = _load_frozen_controls(ROOT)

    development_pairs = tuple(
        (f"dev-{index:02d}", f"dev query {index:02d}")
        for index in range(24)
    )
    tuning_pairs = tuple(
        (f"tuning-{index:02d}", f"tuning query {index:02d}")
        for index in range(18)
    )

    projection = Phase5B0RuntimeProjectionV1(
        development=_suite(
            role="evaluation_development_case",
            suite_sha=protocol.development_suite_sha256,
            pairs=development_pairs,
        ),
        tuning=_suite(
            role="intervention_tuning_case",
            suite_sha=protocol.tuning_suite_sha256,
            pairs=tuning_pairs,
        ),
    )

    return projection, (*development_pairs, *tuning_pairs)


def test_no_eligible_evidence_creates_no_provider_entry() -> None:
    protocol = _load_frozen_controls(ROOT)
    projection, all_pairs = _synthetic_projection()

    items = {
        query: (_historical_item(),)
        for _case_id, query in all_pairs
    }

    materializer = B0ReplayFixtureMaterializer(
        retriever=_StaticRetriever(items),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            SourcePolicyConfig(
                policy_id="github-rest-current-v1"
            )
        ),
        context_builder=BoundedContextBuilder(
            ContextConfig(
                builder_id="bounded-context-v1",
                budget_unit_id="characters",
                max_budget=69663,
                max_evidence_items=15,
            )
        ),
    )

    fixture, coverage = asyncio.run(
        materializer.materialize(
            projection=projection,
            protocol=protocol,
        )
    )

    assert fixture is not None
    assert fixture.entries == ()
    assert coverage.provider_reaching_case_count == 0
    assert coverage.pre_provider_refusal_case_count == 42
    assert coverage.unexpected_prefix_error_count == 0
    assert coverage.fixture_entry_count == 0
    assert coverage.materialization_decision == "PASS"


def test_context_budget_error_is_preserved_as_reject() -> None:
    protocol = _load_frozen_controls(ROOT)
    projection, all_pairs = _synthetic_projection()

    items = {
        query: (_current_item(),)
        for _case_id, query in all_pairs
    }

    materializer = B0ReplayFixtureMaterializer(
        retriever=_StaticRetriever(items),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            SourcePolicyConfig(
                policy_id="github-rest-current-v1"
            )
        ),
        context_builder=_ContextErrorBuilder(),
    )

    fixture, coverage = asyncio.run(
        materializer.materialize(
            projection=projection,
            protocol=protocol,
        )
    )

    assert fixture is None
    assert coverage.materialization_decision == "REJECT"
    assert coverage.unexpected_prefix_error_count == 42
    assert coverage.replay_fixture_materialized is False
    assert coverage.replay_fixture_sha256 is None
