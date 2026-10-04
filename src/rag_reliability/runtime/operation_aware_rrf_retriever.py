"""Runtime implementation of the selected Phase 5 operation-aware RRF retriever."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from pathlib import Path

from rag_reliability.config.identity import RetrievalConfig
from rag_reliability.contracts.runtime import (
    RetrievalRequest,
    RetrievalResult,
    RetrievedEvidence,
)
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.runtime.models import IndexedDocument
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_catalog import load_runtime_operation_catalog
from rag_reliability.runtime.operation_resolution import DeterministicOperationResolver
from rag_reliability.runtime.retrieval import LexicalRetriever

_RETRIEVER_ID = "phase5-operation-aware-rrf-stable-partition-v1"
_SELECTED_TOP_K = 20
_FUSION_CONSTANT = 60
_BM25_K1 = 1.2
_BM25_B = 0.75

_CHUNK_MANIFEST_PATH = (
    Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
)
_CHUNK_MANIFEST_SHA256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(_TOKEN_PATTERN.findall(text.casefold()))


def _verified_lineage_map(
    repo_root: Path,
) -> dict[str, tuple[str, ...]]:
    path = repo_root / _CHUNK_MANIFEST_PATH
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()

    if digest != _CHUNK_MANIFEST_SHA256:
        raise ValueError("Phase 3D chunk manifest hash mismatch")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{_CHUNK_MANIFEST_SHA256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError("Phase 3D chunk manifest sidecar mismatch")

    manifest = Phase3dChunkManifest.model_validate_json(content)

    return {
        chunk.chunk_id: tuple(chunk.linked_operation_ids)
        for chunk in manifest.chunks
    }


class OperationAwareRrfRetriever:
    """Execute the selected lexical+BM25 RRF and operation-lineage partition."""

    def __init__(
        self,
        *,
        config: RetrievalConfig,
        documents: tuple[IndexedDocument, ...],
        repo_root: Path,
    ) -> None:
        if config.retriever_id != _RETRIEVER_ID:
            raise ValueError(
                "operation-aware RRF retriever requires the frozen retriever_id"
            )

        if config.top_k != _SELECTED_TOP_K:
            raise ValueError(
                "operation-aware RRF retriever requires frozen top_k=20"
            )

        if len(documents) != 1333:
            raise ValueError(
                "operation-aware RRF retriever requires the frozen 1333-chunk corpus"
            )

        evidence_ids = tuple(document.evidence_id for document in documents)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("runtime retrieval documents require unique evidence IDs")

        lineage = _verified_lineage_map(repo_root)

        if set(lineage) != set(evidence_ids):
            raise ValueError(
                "runtime retrieval documents do not match the frozen chunk manifest"
            )

        self._config = config
        self._documents = documents
        self._lineage = lineage

        self._lexical = LexicalRetriever(
            config=RetrievalConfig(
                retriever_id="lexical-v1",
                top_k=len(documents),
            ),
            documents=documents,
        )

        self._resolver = DeterministicOperationResolver(
            load_runtime_operation_catalog(repo_root)
        )

        tokenized = tuple(_tokens(document.content) for document in documents)
        self._document_tokens = tokenized
        self._document_lengths = tuple(len(tokens) for tokens in tokenized)

        total_length = sum(self._document_lengths)
        if total_length <= 0:
            raise ValueError("BM25 runtime retrieval requires non-empty corpus text")

        self._average_document_length = total_length / len(documents)

        document_frequency: Counter[str] = Counter()
        for tokens in tokenized:
            document_frequency.update(set(tokens))
        self._document_frequency = document_frequency

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        limit = min(request.top_k, self._config.top_k)

        lexical_items = (
            await self._lexical.retrieve(
                RetrievalRequest(
                    query=request.query,
                    top_k=len(self._documents),
                )
            )
        ).items

        bm25_items = self._bm25(request.query)

        fused = self._fuse(
            lexical_items=lexical_items,
            bm25_items=bm25_items,
        )

        resolution = self._resolver.resolve(request.query)

        ranked = stable_partition_by_operation_lineage(
            items=fused,
            resolution=resolution,
            linked_operation_ids_by_evidence_id=self._lineage,
        )

        return RetrievalResult(items=ranked[:limit])

    def _bm25(
        self,
        query: str,
    ) -> tuple[RetrievedEvidence, ...]:
        query_terms = tuple(sorted(set(_tokens(query))))

        if not query_terms:
            return ()

        document_count = len(self._documents)
        scored: list[tuple[float, IndexedDocument]] = []

        for document, tokens, document_length in zip(
            self._documents,
            self._document_tokens,
            self._document_lengths,
            strict=True,
        ):
            frequencies = Counter(tokens)
            score = 0.0

            for term in query_terms:
                term_frequency = frequencies.get(term, 0)

                if term_frequency == 0:
                    continue

                document_frequency = self._document_frequency[term]

                inverse_document_frequency = math.log(
                    1.0
                    + (
                        (
                            document_count
                            - document_frequency
                            + 0.5
                        )
                        / (
                            document_frequency
                            + 0.5
                        )
                    )
                )

                denominator = (
                    term_frequency
                    + _BM25_K1
                    * (
                        1.0
                        - _BM25_B
                        + _BM25_B
                        * (
                            document_length
                            / self._average_document_length
                        )
                    )
                )

                score += (
                    inverse_document_frequency
                    * (
                        term_frequency
                        * (
                            _BM25_K1
                            + 1.0
                        )
                    )
                    / denominator
                )

            if score > 0.0:
                scored.append((score, document))

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].evidence_id,
            )
        )

        return tuple(
            RetrievedEvidence(
                evidence_id=document.evidence_id,
                source_ids=document.source_ids,
                document_ids=document.document_ids,
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
            for rank, (score, document) in enumerate(scored, start=1)
        )

    @staticmethod
    def _fuse(
        *,
        lexical_items: tuple[RetrievedEvidence, ...],
        bm25_items: tuple[RetrievedEvidence, ...],
    ) -> tuple[RetrievedEvidence, ...]:
        lexical_by_id = {
            item.evidence_id: item
            for item in lexical_items
        }
        bm25_by_id = {
            item.evidence_id: item
            for item in bm25_items
        }

        lexical_rank = {
            item.evidence_id: item.rank
            for item in lexical_items
        }
        bm25_rank = {
            item.evidence_id: item.rank
            for item in bm25_items
        }

        evidence_ids = set(lexical_by_id) | set(bm25_by_id)
        fused: list[tuple[float, RetrievedEvidence]] = []

        for evidence_id in evidence_ids:
            score = 0.0

            if evidence_id in lexical_rank:
                score += 1 / (
                    _FUSION_CONSTANT
                    + lexical_rank[evidence_id]
                )

            if evidence_id in bm25_rank:
                score += 1 / (
                    _FUSION_CONSTANT
                    + bm25_rank[evidence_id]
                )

            if evidence_id in lexical_by_id:
                source = lexical_by_id[evidence_id]
            else:
                source = bm25_by_id[evidence_id]

            fused.append((score, source))

        fused.sort(
            key=lambda item: (
                -item[0],
                item[1].evidence_id,
            )
        )

        return tuple(
            RetrievedEvidence(
                evidence_id=source.evidence_id,
                source_ids=source.source_ids,
                document_ids=source.document_ids,
                content=source.content,
                rank=rank,
                score=score,
                authority_level=source.authority_level,
                source_state=source.source_state,
                product_scope=source.product_scope,
                api_version_or_snapshot=source.api_version_or_snapshot,
                synthetic_overlay=source.synthetic_overlay,
                eligible_as_final_citation=source.eligible_as_final_citation,
            )
            for rank, (score, source) in enumerate(fused, start=1)
        )
