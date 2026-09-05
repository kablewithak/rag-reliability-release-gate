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


class ConfigBoundComponent(Protocol):
    @property
    def configuration_id(self) -> str:
        """Return the exact configuration identity executed by this component."""

        ...


@runtime_checkable
class Retriever(ConfigBoundComponent, Protocol):
    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Retrieve ranked evidence candidates."""

        ...


@runtime_checkable
class SourcePolicyFilter(ConfigBoundComponent, Protocol):
    async def apply(self, request: SourceFilterRequest) -> SourceFilterResult:
        """Apply authority, source-state, and scope policy."""

        ...


@runtime_checkable
class Reranker(ConfigBoundComponent, Protocol):
    async def rerank(self, request: RerankRequest) -> RerankResult:
        """Optionally reorder eligible evidence without changing its provenance."""

        ...


@runtime_checkable
class ContextBuilder(ConfigBoundComponent, Protocol):
    async def build(self, request: ContextBuildRequest) -> ContextBundle:
        """Build a bounded context bundle from eligible evidence."""

        ...


@runtime_checkable
class ProviderAdapter(ConfigBoundComponent, Protocol):
    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate through a provider-neutral adapter boundary."""

        ...


@runtime_checkable
class CitationValidator(ConfigBoundComponent, Protocol):
    async def validate(
        self,
        request: CitationValidationRequest,
    ) -> CitationValidationResult:
        """Validate provider citations and material-claim support."""

        ...
