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
    RuntimeErrorCode,
    SourceState,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import (
    CitationValidationRequest,
    CitationValidationResult,
    RetrievalRequest,
    RetrievalResult,
    SourceFilterRequest,
    SourceFilterResult,
)
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import (
    CitationValidationExecutionError,
    RetrievalExecutionError,
    SourcePolicyExecutionError,
)
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import IndexedDocument, ReplayEntry
from rag_reliability.runtime.pipeline import DeterministicRagPipeline
from rag_reliability.runtime.provider import ReplayProvider
from rag_reliability.runtime.retrieval import LexicalRetriever


def runtime_config() -> RuntimeConfiguration:
    return RuntimeConfiguration(
        schema_version="1.0",
        retrieval=RetrievalConfig(retriever_id="lexical-v1", top_k=3),
        source_policy=SourcePolicyConfig(policy_id="github-rest-current-v1"),
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
        content="GitHub REST requests can include the X-GitHub-Api-Version header.",
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
    )


class FailingRetriever:
    def __init__(self, config: RetrievalConfig) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        raise RetrievalExecutionError("deterministic retrieval failure")


class FailingSourcePolicyFilter:
    def __init__(self, config: SourcePolicyConfig) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def apply(self, request: SourceFilterRequest) -> SourceFilterResult:
        raise SourcePolicyExecutionError("deterministic source-policy failure")


class FailingCitationValidator:
    def __init__(self, config: CitationConfig) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def validate(
        self,
        request: CitationValidationRequest,
    ) -> CitationValidationResult:
        raise CitationValidationExecutionError(
            "deterministic citation-validation failure"
        )


def standard_provider(config: RuntimeConfiguration, query: str) -> ReplayProvider:
    return ReplayProvider(
        config.provider,
        (
            ReplayEntry(
                query=query,
                answer_text=(
                    "GitHub REST requests can include the X-GitHub-Api-Version header."
                ),
                cited_source_ids=("source-current",),
            ),
        ),
    )


def test_retrieval_failure_returns_error_outcome_and_trace() -> None:
    config = runtime_config()
    query = "What API version header can GitHub REST requests include?"
    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=FailingRetriever(config.retrieval),
        source_filter=CurrentGithubRestSourcePolicyFilter(config.source_policy),
        context_builder=BoundedContextBuilder(config.context),
        provider=standard_provider(config, query),
        citation_validator=ExactCitationValidator(config.citation),
    )

    execution = asyncio.run(
        pipeline.run(RuntimeCaseInput(case_id="dev-error-001", query=query))
    )

    assert execution.outcome.status == "error"
    assert execution.outcome.error_code is RuntimeErrorCode.RETRIEVAL_ERROR
    assert execution.trace.events[-1].stage is TraceStage.RETRIEVAL
    assert execution.trace.events[-1].status is TraceStatus.ERROR
    assert execution.trace.events[-1].error_code == "retrieval_error"


def test_source_policy_failure_returns_error_outcome_and_trace() -> None:
    config = runtime_config()
    query = "What API version header can GitHub REST requests include?"
    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=LexicalRetriever(config.retrieval, (current_document(),)),
        source_filter=FailingSourcePolicyFilter(config.source_policy),
        context_builder=BoundedContextBuilder(config.context),
        provider=standard_provider(config, query),
        citation_validator=ExactCitationValidator(config.citation),
    )

    execution = asyncio.run(
        pipeline.run(RuntimeCaseInput(case_id="dev-error-002", query=query))
    )

    assert execution.outcome.status == "error"
    assert execution.outcome.error_code is RuntimeErrorCode.SOURCE_POLICY_ERROR
    assert execution.trace.events[-1].stage is TraceStage.FILTERING
    assert execution.trace.events[-1].status is TraceStatus.ERROR
    assert execution.trace.events[-1].error_code == "source_policy_error"


def test_citation_failure_returns_error_outcome_and_trace() -> None:
    config = runtime_config()
    query = "What API version header can GitHub REST requests include?"
    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=LexicalRetriever(config.retrieval, (current_document(),)),
        source_filter=CurrentGithubRestSourcePolicyFilter(config.source_policy),
        context_builder=BoundedContextBuilder(config.context),
        provider=standard_provider(config, query),
        citation_validator=FailingCitationValidator(config.citation),
    )

    execution = asyncio.run(
        pipeline.run(RuntimeCaseInput(case_id="dev-error-003", query=query))
    )

    assert execution.outcome.status == "error"
    assert (
        execution.outcome.error_code
        is RuntimeErrorCode.CITATION_VALIDATION_ERROR
    )
    assert execution.trace.events[-1].stage is TraceStage.CITATION_VALIDATION
    assert execution.trace.events[-1].status is TraceStatus.ERROR
    assert execution.trace.events[-1].error_code == "citation_validation_error"
