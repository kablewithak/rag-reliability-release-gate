import asyncio

from rag_reliability.config.identity import (
    CitationConfig,
    ContextConfig,
    RetrievalConfig,
    SourcePolicyConfig,
)
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CitationValidationStatus,
    SourceState,
)
from rag_reliability.contracts.runtime import (
    CitationValidationRequest,
    ContextBuildRequest,
    ContextBundle,
    ContextItem,
    ProviderResponse,
    RetrievalRequest,
    SourceFilterRequest,
)
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import IndexedDocument
from rag_reliability.runtime.retrieval import LexicalRetriever


def document(
    source_id: str,
    content: str,
    *,
    authority: AuthorityLevel = AuthorityLevel.AUTHORITATIVE,
    state: SourceState = SourceState.CURRENT,
    product_scope: str = "api.github.com",
    api_version: str = "2026-03-10",
) -> IndexedDocument:
    return IndexedDocument(
        source_id=source_id,
        content=content,
        authority_level=authority,
        source_state=state,
        product_scope=product_scope,
        api_version_or_snapshot=api_version,
    )


def test_lexical_retriever_is_deterministic() -> None:
    config = RetrievalConfig(retriever_id="lexical-v1", top_k=2)
    retriever = LexicalRetriever(
        config,
        (
            document("source-b", "issues support labels"),
            document("source-a", "issues support labels"),
            document("source-c", "actions workflow runs"),
        ),
    )

    result = asyncio.run(
        retriever.retrieve(RetrievalRequest(query="issues labels", top_k=2))
    )

    assert tuple(item.source_id for item in result.items) == (
        "source-a",
        "source-b",
    )
    assert tuple(item.rank for item in result.items) == (1, 2)


def test_source_filter_rejects_stale_and_wrong_scope() -> None:
    filter_config = SourcePolicyConfig(policy_id="github-rest-current-v1")
    source_filter = CurrentGithubRestSourcePolicyFilter(filter_config)

    retrieval = asyncio.run(
        LexicalRetriever(
            RetrievalConfig(retriever_id="lexical-v1", top_k=3),
            (
                document("current", "issues labels"),
                document(
                    "historical",
                    "issues labels",
                    authority=AuthorityLevel.HISTORICAL,
                    state=SourceState.HISTORICAL_COMPARISON,
                    api_version="2022-11-28",
                ),
                document(
                    "wrong-scope",
                    "issues labels",
                    product_scope="other.example.com",
                ),
            ),
        ).retrieve(RetrievalRequest(query="issues labels", top_k=3))
    )

    result = asyncio.run(
        source_filter.apply(SourceFilterRequest(candidates=retrieval.items))
    )

    assert tuple(item.source_id for item in result.eligible) == ("current",)
    reasons = {item.source_id: item.reason_code for item in result.rejected}
    assert reasons["historical"] == "authority_level_mismatch"
    assert reasons["wrong-scope"] == "product_scope_mismatch"


def test_context_builder_respects_budget_without_partial_truncation() -> None:
    config = ContextConfig(
        builder_id="bounded-context-v1",
        budget_unit_id="characters",
        max_budget=45,
        max_evidence_items=2,
    )
    builder = BoundedContextBuilder(config)
    retriever = LexicalRetriever(
        RetrievalConfig(retriever_id="lexical-v1", top_k=2),
        (
            document("a", "issues labels"),
            document("b", "issues labels plus additional detail"),
        ),
    )
    retrieved = asyncio.run(
        retriever.retrieve(RetrievalRequest(query="issues labels", top_k=2))
    )

    context = asyncio.run(
        builder.build(
            ContextBuildRequest(
                query="issues labels",
                evidence=retrieved.items,
            )
        )
    )

    assert tuple(item.source_id for item in context.items) == ("a",)
    assert context.assembled_context == "SOURCE: a\nissues labels"


def test_exact_citation_validator_rejects_non_verbatim_support() -> None:
    validator = ExactCitationValidator(
        CitationConfig(
            validator_id="exact-citation-v1",
            require_citations=True,
        )
    )
    context = ContextBundle(
        query="What does the source say?",
        items=(
            ContextItem(
                source_id="source-1",
                content="GitHub REST requests can include an API version header.",
                position=1,
                authority_level=AuthorityLevel.AUTHORITATIVE,
                source_state=SourceState.CURRENT,
                eligible_as_final_citation=True,
            ),
        ),
        assembled_context=(
            "SOURCE: source-1\n"
            "GitHub REST requests can include an API version header."
        ),
    )

    result = asyncio.run(
        validator.validate(
            CitationValidationRequest(
                provider_response=ProviderResponse(
                    answer_text="This unsupported wording is not present.",
                    cited_source_ids=("source-1",),
                ),
                context=context,
            )
        )
    )

    assert result.all_material_claims_supported is False
    assert result.checks[0].status is CitationValidationStatus.UNSUPPORTED
