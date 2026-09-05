import inspect

from rag_reliability.contracts.interfaces import (
    CitationValidator,
    ContextBuilder,
    ProviderAdapter,
    Reranker,
    Retriever,
    SourcePolicyFilter,
)


def test_runtime_protocol_methods_are_async() -> None:
    assert inspect.iscoroutinefunction(Retriever.retrieve)
    assert inspect.iscoroutinefunction(SourcePolicyFilter.apply)
    assert inspect.iscoroutinefunction(Reranker.rerank)
    assert inspect.iscoroutinefunction(ContextBuilder.build)
    assert inspect.iscoroutinefunction(ProviderAdapter.generate)
    assert inspect.iscoroutinefunction(CitationValidator.validate)
