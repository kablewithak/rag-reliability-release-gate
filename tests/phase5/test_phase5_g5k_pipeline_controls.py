from __future__ import annotations

import asyncio

from rag_reliability.config.identity import (
    CitationConfig,
    ContextConfig,
    FallbackConfig,
    ProviderConfig,
    RetrievalConfig,
    RuntimeConfiguration,
    SourcePolicyConfig,
)
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    FailureLabel,
    RefusalReason,
    RuntimeErrorCode,
    SourceState,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.interfaces import ProviderAdapter
from rag_reliability.contracts.runtime import (
    ProviderDecision,
    ProviderRequest,
    RetrievalRequest,
    RetrievalResult,
    RetrievedEvidence,
)
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import (
    ProviderMalformedResponseError,
    ProviderTimeoutError,
)
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import ReplayEntry
from rag_reliability.runtime.pipeline import DeterministicRagPipeline
from rag_reliability.runtime.provider import ReplayProvider


def _config() -> RuntimeConfiguration:
    return RuntimeConfiguration(
        schema_version="phase5-g5k-control-test-v1",
        retrieval=RetrievalConfig(
            retriever_id=(
                "phase5-operation-aware-rrf-stable-partition-v1"
            ),
            top_k=20,
        ),
        source_policy=SourcePolicyConfig(
            policy_id="github-rest-current-v1",
        ),
        reranker=None,
        context=ContextConfig(
            builder_id="bounded-context-v1",
            budget_unit_id="characters",
            max_budget=69663,
            max_evidence_items=15,
        ),
        provider=ProviderConfig(
            adapter_id="replay-provider-v1",
            model_id="replay-model-v1",
            timeout_ms=1000,
            max_retries=0,
        ),
        citation=CitationConfig(
            validator_id="exact-citation-v1",
            require_citations=True,
        ),
        fallback=FallbackConfig(
            policy_id="safe-refusal-v1",
            allow_qualified_answer=False,
        ),
    )


def _item(
    *,
    current: bool = True,
) -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id="g5k-evidence",
        source_ids=("g5k-source",),
        document_ids=("g5k-document",),
        content=(
            "Requests may include the "
            "X-GitHub-Api-Version header."
        ),
        rank=1,
        score=1.0,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=(
            SourceState.CURRENT
            if current
            else SourceState.HISTORICAL_COMPARISON
        ),
        product_scope="api.github.com",
        api_version_or_snapshot=(
            "2026-03-10"
            if current
            else "2022-11-28"
        ),
        synthetic_overlay=False,
        eligible_as_final_citation=True,
    )


class _StaticRetriever:
    def __init__(
        self,
        config: RetrievalConfig,
        item: RetrievedEvidence,
    ) -> None:
        self._config = config
        self._item = item

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        return RetrievalResult(
            items=(self._item,)
        )


class _TimeoutProvider:
    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderDecision:
        raise ProviderTimeoutError(
            "deterministic timeout"
        )


class _MalformedProvider:
    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderDecision:
        raise ProviderMalformedResponseError(
            "deterministic malformed response"
        )


def _pipeline(
    *,
    item: RetrievedEvidence,
    provider: ProviderAdapter,
) -> DeterministicRagPipeline:
    config = _config()

    return DeterministicRagPipeline(
        config=config,
        retriever=_StaticRetriever(
            config.retrieval,
            item,
        ),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            config.source_policy
        ),
        context_builder=BoundedContextBuilder(
            config.context
        ),
        provider=provider,
        citation_validator=ExactCitationValidator(
            config.citation
        ),
    )


def test_source_policy_refusal_remains_safe() -> None:
    config = _config()

    execution = asyncio.run(
        _pipeline(
            item=_item(
                current=False
            ),
            provider=ReplayProvider(
                config.provider,
                (),
            ),
        ).run(
            RuntimeCaseInput(
                case_id="g5k-source-refusal",
                query="g5k fixture query",
            )
        )
    )

    assert execution.outcome.status == "refusal"
    assert (
        execution.outcome.reason
        is RefusalReason.INSUFFICIENT_EVIDENCE
    )


def test_unsupported_citation_becomes_safe_refusal() -> None:
    config = _config()

    provider = ReplayProvider(
        config.provider,
        (
            ReplayEntry(
                query="g5k fixture query",
                answer_text="Unsupported generated claim.",
                cited_evidence_ids=("g5k-evidence",),
            ),
        ),
    )

    execution = asyncio.run(
        _pipeline(
            item=_item(),
            provider=provider,
        ).run(
            RuntimeCaseInput(
                case_id="g5k-unsupported-citation",
                query="g5k fixture query",
            )
        )
    )

    assert execution.outcome.status == "refusal"
    assert (
        execution.outcome.reason
        is RefusalReason.UNSUPPORTED_CITATION
    )
    assert (
        execution.trace.primary_failure
        is FailureLabel.CITATION_NOT_SUPPORTED
    )


def test_provider_timeout_becomes_terminal_error() -> None:
    config = _config()

    execution = asyncio.run(
        _pipeline(
            item=_item(),
            provider=_TimeoutProvider(
                config.provider
            ),
        ).run(
            RuntimeCaseInput(
                case_id="g5k-timeout",
                query="g5k fixture query",
            )
        )
    )

    assert execution.outcome.status == "error"
    assert (
        execution.outcome.error_code
        is RuntimeErrorCode.PROVIDER_TIMEOUT
    )
    assert (
        execution.trace.primary_failure
        is FailureLabel.PROVIDER_TIMEOUT
    )
    assert execution.outcome.retryable is False


def test_provider_malformed_response_becomes_terminal_error() -> None:
    config = _config()

    execution = asyncio.run(
        _pipeline(
            item=_item(),
            provider=_MalformedProvider(
                config.provider
            ),
        ).run(
            RuntimeCaseInput(
                case_id="g5k-malformed",
                query="g5k fixture query",
            )
        )
    )

    assert execution.outcome.status == "error"
    assert (
        execution.outcome.error_code
        is RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE
    )
    assert (
        execution.trace.primary_failure
        is FailureLabel.PROVIDER_MALFORMED_RESPONSE
    )
    assert execution.outcome.retryable is False
