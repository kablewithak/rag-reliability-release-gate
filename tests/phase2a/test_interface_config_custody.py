from rag_reliability.contracts.interfaces import (
    CitationValidator,
    ContextBuilder,
    ProviderAdapter,
    Retriever,
    SourcePolicyFilter,
)


def test_runtime_protocols_require_configuration_identity() -> None:
    for protocol in (
        Retriever,
        SourcePolicyFilter,
        ContextBuilder,
        ProviderAdapter,
        CitationValidator,
    ):
        assert "configuration_id" in protocol.__dict__ or any(
            "configuration_id" in base.__dict__
            for base in protocol.__mro__
        )
