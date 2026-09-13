from __future__ import annotations

import asyncio

import pytest
from pydantic import ValidationError

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
    RefusalReason,
    SourceState,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import (
    ProviderDecision,
    ProviderRefusalDecision,
    ProviderRequest,
)
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.filtering import (
    CurrentGithubRestSourcePolicyFilter,
)
from rag_reliability.runtime.models import IndexedDocument
from rag_reliability.runtime.pipeline import DeterministicRagPipeline
from rag_reliability.runtime.retrieval import LexicalRetriever


def runtime_config() -> RuntimeConfiguration:
    return RuntimeConfiguration(
        schema_version="1.0",
        retrieval=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=3,
        ),
        source_policy=SourcePolicyConfig(
            policy_id="github-rest-current-v1",
        ),
        reranker=None,
        context=ContextConfig(
            builder_id="bounded-context-v1",
            budget_unit_id="characters",
            max_budget=500,
            max_evidence_items=3,
        ),
        provider=ProviderConfig(
            adapter_id="semantic-provider-test-v1",
            model_id="semantic-model-test-v1",
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


def current_document() -> IndexedDocument:
    return IndexedDocument(
        evidence_id="evidence-current",
        source_ids=("source-current",),
        document_ids=("document-current",),
        content=(
            "GitHub REST API version requests may use "
            "the X-GitHub-Api-Version header."
        ),
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )


class RefusingProvider:
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
        return ProviderRefusalDecision(
            reason=RefusalReason.INSUFFICIENT_EVIDENCE,
            message=(
                "The available evidence does not support "
                "the requested conclusion."
            ),
        )


def test_provider_refusal_contract_rejects_runtime_owned_reason() -> None:
    with pytest.raises(
        ValidationError,
        match="provider refusal reason",
    ):
        ProviderRefusalDecision(
            reason=RefusalReason.UNSUPPORTED_CITATION,
            message="Unsupported citation.",
        )


def test_pipeline_accepts_semantic_provider_refusal() -> None:
    config = runtime_config()

    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=LexicalRetriever(
            config.retrieval,
            (current_document(),),
        ),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            config.source_policy
        ),
        context_builder=BoundedContextBuilder(
            config.context
        ),
        provider=RefusingProvider(
            config.provider
        ),
        citation_validator=ExactCitationValidator(
            config.citation
        ),
    )

    execution = asyncio.run(
        pipeline.run(
            RuntimeCaseInput(
                case_id="phase5-provider-refusal-test",
                query="What GitHub REST API version header is used?",
            )
        )
    )

    assert execution.outcome.status == "refusal"
    assert (
        execution.outcome.reason
        is RefusalReason.INSUFFICIENT_EVIDENCE
    )

    assert execution.trace.primary_failure is None

    assert (
        execution.trace.events[-2].stage
        is TraceStage.PROVIDER_GENERATION
    )
    assert (
        execution.trace.events[-2].status
        is TraceStatus.REFUSED
    )

    assert (
        execution.trace.events[-1].stage
        is TraceStage.REFUSAL_FALLBACK
    )
    assert (
        execution.trace.events[-1].status
        is TraceStatus.REFUSED
    )
