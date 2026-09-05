"""Provider-neutral async runtime component protocols."""

from typing import Protocol, runtime_checkable

from rag_reliability.contracts.runtime import (
    CitationValidationRequest,
    CitationValidationResult,
    ContextBuildRequest,
    ContextBundle,
    ProviderRequest,
    ProviderResponse,
    RerankRequest,
    RerankResult,
    RetrievalRequest,
    RetrievalResult,
    SourceFilterRequest,
    SourceFilterResult,
)


@runtime_checkable
class Retriever(Protocol):
    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Retrieve ranked evidence candidates."""

        ...


@runtime_checkable
class SourcePolicyFilter(Protocol):
    async def apply(self, request: SourceFilterRequest) -> SourceFilterResult:
        """Apply authority, source-state, and scope policy."""

        ...


@runtime_checkable
class Reranker(Protocol):
    async def rerank(self, request: RerankRequest) -> RerankResult:
        """Optionally reorder eligible evidence without changing its provenance."""

        ...


@runtime_checkable
class ContextBuilder(Protocol):
    async def build(self, request: ContextBuildRequest) -> ContextBundle:
        """Build a bounded context bundle from eligible evidence."""

        ...


@runtime_checkable
class ProviderAdapter(Protocol):
    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate through a provider-neutral adapter boundary."""

        ...


@runtime_checkable
class CitationValidator(Protocol):
    async def validate(
        self,
        request: CitationValidationRequest,
    ) -> CitationValidationResult:
        """Validate provider citations and material-claim support."""

        ...
