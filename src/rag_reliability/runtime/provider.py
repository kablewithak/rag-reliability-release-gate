"""Deterministic fake/replay provider for the development slice."""

from rag_reliability.config.identity import ProviderConfig
from rag_reliability.contracts.runtime import ProviderRequest, ProviderResponse
from rag_reliability.runtime.errors import ReplayResponseNotFoundError
from rag_reliability.runtime.models import ReplayEntry


class ReplayProvider:
    """Return predeclared provider responses without external dependencies."""

    def __init__(
        self,
        config: ProviderConfig,
        entries: tuple[ReplayEntry, ...],
    ) -> None:
        queries = tuple(entry.query for entry in entries)
        if len(queries) != len(set(queries)):
            raise ValueError("replay queries must be unique")
        self._config = config
        self._entries = {entry.query: entry for entry in entries}

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        entry = self._entries.get(request.query)
        if entry is None:
            raise ReplayResponseNotFoundError(
                f"no replay response configured for query: {request.query}"
            )

        return ProviderResponse(
            answer_text=entry.answer_text,
            cited_source_ids=entry.cited_source_ids,
        )
