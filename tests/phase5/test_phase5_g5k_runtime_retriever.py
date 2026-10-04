from __future__ import annotations

import asyncio
from pathlib import Path

from rag_reliability.config.identity import RetrievalConfig
from rag_reliability.contracts.runtime import RetrievalRequest
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    _fuse_rankings,
)
from rag_reliability.evaluation.semantic_runtime_development_confirmation import (
    _load_development_cases,
)
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_aware_rrf_retriever import (
    OperationAwareRrfRetriever,
)
from rag_reliability.runtime.operation_catalog import load_runtime_operation_catalog
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

ROOT = Path(__file__).resolve().parents[2]


async def _assert_all_parity() -> None:
    documents, _ids = _load_indexed_documents(ROOT)

    config = RetrievalConfig(
        retriever_id=(
            "phase5-operation-aware-rrf-stable-partition-v1"
        ),
        top_k=20,
    )

    runtime = OperationAwareRrfRetriever(
        config=config,
        documents=documents,
        repo_root=ROOT,
    )

    rrf_config = Phase5RrfHybridCandidateConfig()

    lexical = LexicalRetriever(
        config=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=rrf_config.characterization_top_k,
        ),
        documents=documents,
    )

    bm25 = _Bm25CandidateRetriever(
        config=Phase5Bm25CandidateConfig(),
        documents=documents,
    )

    resolver = DeterministicOperationResolver(
        load_runtime_operation_catalog(ROOT)
    )

    manifest = Phase3dChunkManifest.model_validate_json(
        (
            ROOT
            / "datasets"
            / "chunk_manifests"
            / "phase3d_chunk_manifest_v1.json"
        ).read_bytes()
    )

    lineage = {
        chunk.chunk_id: tuple(chunk.linked_operation_ids)
        for chunk in manifest.chunks
    }

    cases = (
        *_load_development_cases(ROOT),
        *_load_tuning_cases(ROOT),
    )

    assert len(cases) == 42

    for case in cases:
        actual = (
            await runtime.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=20,
                )
            )
        ).items

        lexical_items = (
            await lexical.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=rrf_config.characterization_top_k,
                )
            )
        ).items

        generic = _fuse_rankings(
            lexical_items=lexical_items,
            bm25_items=bm25.retrieve(case.query),
            config=rrf_config,
        )

        expected = stable_partition_by_operation_lineage(
            items=generic,
            resolution=resolver.resolve(case.query),
            linked_operation_ids_by_evidence_id=lineage,
        )[:20]

        assert actual == expected, case.case_id


def test_runtime_retriever_matches_reference_on_all_exposed_queries() -> None:
    asyncio.run(_assert_all_parity())


def test_runtime_retriever_preserves_config_identity_and_top_k() -> None:
    documents, _ids = _load_indexed_documents(ROOT)

    config = RetrievalConfig(
        retriever_id=(
            "phase5-operation-aware-rrf-stable-partition-v1"
        ),
        top_k=20,
    )

    retriever = OperationAwareRrfRetriever(
        config=config,
        documents=documents,
        repo_root=ROOT,
    )

    case = _load_development_cases(ROOT)[0]

    result = asyncio.run(
        retriever.retrieve(
            RetrievalRequest(
                query=case.query,
                top_k=100,
            )
        )
    )

    assert retriever.configuration_id == config.configuration_id
    assert len(result.items) <= 20
