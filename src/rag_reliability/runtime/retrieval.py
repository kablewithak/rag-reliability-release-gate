"""Deterministic lexical retrieval for the Phase 2 development slice."""

import re

from rag_reliability.config.identity import RetrievalConfig
from rag_reliability.contracts.runtime import (
    RetrievalRequest,
    RetrievalResult,
    RetrievedEvidence,
)
from rag_reliability.runtime.models import IndexedDocument

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def _tokens(text: str) -> frozenset[str]:
    return frozenset(_TOKEN_PATTERN.findall(text.casefold()))


class LexicalRetriever:
    """Simple deterministic overlap retriever with stable tie-breaking."""

    def __init__(
        self,
        config: RetrievalConfig,
        documents: tuple[IndexedDocument, ...],
    ) -> None:
        self._config = config
        self._documents = documents

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        query_tokens = _tokens(request.query)
        if not query_tokens:
            return RetrievalResult(items=())

        scored: list[tuple[float, IndexedDocument]] = []
        for document in self._documents:
            document_tokens = _tokens(document.content)
            overlap = len(query_tokens & document_tokens)
            if overlap == 0:
                continue
            score = overlap / len(query_tokens)
            scored.append((score, document))

        scored.sort(key=lambda item: (-item[0], item[1].source_id))
        limit = min(request.top_k, self._config.top_k)

        items = tuple(
            RetrievedEvidence(
                source_id=document.source_id,
                content=document.content,
                rank=rank,
                score=score,
                authority_level=document.authority_level,
                source_state=document.source_state,
                product_scope=document.product_scope,
                api_version_or_snapshot=document.api_version_or_snapshot,
                synthetic_overlay=document.synthetic_overlay,
                eligible_as_final_citation=document.eligible_as_final_citation,
            )
            for rank, (score, document) in enumerate(scored[:limit], start=1)
        )
        return RetrievalResult(items=items)
