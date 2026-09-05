import asyncio

import pytest

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
    SourceState,
    TraceStage,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import ComponentConfigurationMismatchError
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import IndexedDocument, ReplayEntry
from rag_reliability.runtime.pipeline import DeterministicRagPipeline
from rag_reliability.runtime.provider import ReplayProvider
from rag_reliability.runtime.retrieval import LexicalRetriever


def config() -> RuntimeConfiguration:
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


def current_document() -> IndexedDocument:
    return IndexedDocument(
        source_id="source-current",
        content=(
            "GitHub REST requests can include the X-GitHub-Api-Version header."
        ),
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )


def pipeline(
    runtime_config: RuntimeConfiguration,
    *,
    entries: tuple[ReplayEntry, ...],
    documents: tuple[IndexedDocument, ...] | None = None,
) -> DeterministicRagPipeline:
    documents = documents if documents is not None else (current_document(),)
    return DeterministicRagPipeline(
        config=runtime_config,
        retriever=LexicalRetriever(runtime_config.retrieval, documents),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            runtime_config.source_policy
        ),
        context_builder=BoundedContextBuilder(runtime_config.context),
        provider=ReplayProvider(runtime_config.provider, entries),
        citation_validator=ExactCitationValidator(runtime_config.citation),
    )


def test_pipeline_returns_supported_answer_and_trace() -> None:
    runtime_config = config()
    query = "What API version header can GitHub REST requests include?"
    answer = "GitHub REST requests can include the X-GitHub-Api-Version header."
    execution = asyncio.run(
        pipeline(
            runtime_config,
            entries=(
                ReplayEntry(
                    query=query,
                    answer_text=answer,
                    cited_source_ids=("source-current",),
                ),
            ),
        ).run(RuntimeCaseInput(case_id="dev-001", query=query))
    )

    assert execution.outcome.status == "answer"
    assert execution.outcome.answer_text == answer
    assert execution.trace.configuration_id == runtime_config.configuration_id
    assert tuple(event.stage for event in execution.trace.events) == (
        TraceStage.RETRIEVAL,
        TraceStage.FILTERING,
        TraceStage.CONTEXT_ASSEMBLY,
        TraceStage.PROVIDER_GENERATION,
        TraceStage.CITATION_VALIDATION,
    )
    assert execution.trace.primary_failure is None


def test_pipeline_refuses_when_no_current_authoritative_evidence_exists() -> None:
    runtime_config = config()
    historical = IndexedDocument(
        source_id="source-old",
        content="GitHub REST requests can include an API version header.",
        authority_level=AuthorityLevel.HISTORICAL,
        source_state=SourceState.HISTORICAL_COMPARISON,
        product_scope="api.github.com",
        api_version_or_snapshot="2022-11-28",
    )
    execution = asyncio.run(
        pipeline(
            runtime_config,
            entries=(),
            documents=(historical,),
        ).run(
            RuntimeCaseInput(
                case_id="dev-002",
                query="What API version header can GitHub REST requests include?",
            )
        )
    )

    assert execution.outcome.status == "refusal"
    assert execution.outcome.reason is RefusalReason.INSUFFICIENT_EVIDENCE
    assert execution.trace.events[-1].stage is TraceStage.REFUSAL_FALLBACK


def test_pipeline_refuses_unsupported_provider_citation() -> None:
    runtime_config = config()
    query = "What API version header can GitHub REST requests include?"
    execution = asyncio.run(
        pipeline(
            runtime_config,
            entries=(
                ReplayEntry(
                    query=query,
                    answer_text="Unsupported answer text.",
                    cited_source_ids=("source-current",),
                ),
            ),
        ).run(RuntimeCaseInput(case_id="dev-003", query=query))
    )

    assert execution.outcome.status == "refusal"
    assert execution.outcome.reason is RefusalReason.UNSUPPORTED_CITATION
    assert execution.trace.primary_failure is FailureLabel.CITATION_NOT_SUPPORTED


def test_pipeline_rejects_component_configuration_mismatch() -> None:
    runtime_config = config()
    wrong_retrieval = RetrievalConfig(
        retriever_id="other-retriever-v1",
        top_k=3,
    )

    with pytest.raises(ComponentConfigurationMismatchError):
        DeterministicRagPipeline(
            config=runtime_config,
            retriever=LexicalRetriever(
                wrong_retrieval,
                (current_document(),),
            ),
            source_filter=CurrentGithubRestSourcePolicyFilter(
                runtime_config.source_policy
            ),
            context_builder=BoundedContextBuilder(runtime_config.context),
            provider=ReplayProvider(runtime_config.provider, ()),
            citation_validator=ExactCitationValidator(
                runtime_config.citation
            ),
        )
