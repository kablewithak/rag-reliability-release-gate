import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CitationValidationStatus,
    SourceState,
)
from rag_reliability.contracts.runtime import (
    AnswerOutcome,
    CitationCheck,
    CitationValidationResult,
    ContextBundle,
    ContextItem,
    ProviderRequest,
    ProviderResponse,
    RetrievedEvidence,
    RuntimeOutcome,
    runtime_outcome_adapter,
)


def build_context() -> ContextBundle:
    return ContextBundle(
        query="What is the current API version?",
        items=(
            ContextItem(
                source_id="source-1",
                content="Current authoritative evidence.",
                position=1,
                authority_level=AuthorityLevel.AUTHORITATIVE,
                source_state=SourceState.CURRENT,
                eligible_as_final_citation=True,
            ),
        ),
        assembled_context="Current authoritative evidence.",
    )


def test_provider_request_rejects_provider_specific_client_object() -> None:
    with pytest.raises(ValidationError):
        ProviderRequest.model_validate(
            {
                "query": "Question",
                "context": build_context().model_dump(),
                "provider_client": object(),
            }
        )


def test_provider_response_rejects_raw_provider_payload() -> None:
    with pytest.raises(ValidationError):
        ProviderResponse.model_validate(
            {
                "answer_text": "Answer",
                "cited_source_ids": ["source-1"],
                "raw_provider_response": {"vendor": "opaque"},
            }
        )


def test_synthetic_retrieved_evidence_cannot_be_authoritative() -> None:
    with pytest.raises(ValidationError):
        RetrievedEvidence(
            source_id="synthetic-1",
            content="Synthetic distractor.",
            rank=1,
            score=0.4,
            authority_level=AuthorityLevel.AUTHORITATIVE,
            source_state=SourceState.CURRENT,
            product_scope="github-rest",
            api_version_or_snapshot="2026-03-10",
            synthetic_overlay=True,
            eligible_as_final_citation=False,
        )


def test_runtime_outcome_uses_discriminated_state() -> None:
    validation = CitationValidationResult(
        checks=(
            CitationCheck(
                source_id="source-1",
                status=CitationValidationStatus.SUPPORTED,
            ),
        ),
        all_material_claims_supported=True,
    )
    outcome = AnswerOutcome(
        answer_text="Supported answer.",
        cited_source_ids=("source-1",),
        citation_validation=validation,
    )

    parsed: RuntimeOutcome = runtime_outcome_adapter.validate_python(outcome.model_dump())

    assert parsed.status == "answer"


def test_runtime_outcome_rejects_unknown_state() -> None:
    with pytest.raises(ValidationError):
        runtime_outcome_adapter.validate_python(
            {
                "status": "maybe",
                "message": "Ambiguous runtime state is forbidden.",
            }
        )
