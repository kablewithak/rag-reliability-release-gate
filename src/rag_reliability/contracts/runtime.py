"""Strict request/result contracts for the runtime RAG path."""

from typing import Annotated, Literal

from pydantic import Field, TypeAdapter, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CitationValidationStatus,
    RefusalReason,
    RuntimeErrorCode,
    SourceState,
)


class RetrievalRequest(ContractModel):
    query: NonEmptyStr
    top_k: int = Field(ge=1)


class RetrievedEvidence(ContractModel):
    source_id: NonEmptyStr
    content: NonEmptyStr
    rank: int = Field(ge=1)
    score: float
    authority_level: AuthorityLevel
    source_state: SourceState
    product_scope: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr
    synthetic_overlay: bool = False
    eligible_as_final_citation: bool = True

    @model_validator(mode="after")
    def validate_synthetic_authority(self) -> "RetrievedEvidence":
        if self.synthetic_overlay:
            if self.authority_level is not AuthorityLevel.NONE:
                raise ValueError("synthetic retrieved evidence must have authority_level=none")
            if self.eligible_as_final_citation:
                raise ValueError("synthetic retrieved evidence cannot be a final citation")
        return self


class RetrievalResult(ContractModel):
    items: tuple[RetrievedEvidence, ...]

    @model_validator(mode="after")
    def validate_unique_ranks(self) -> "RetrievalResult":
        ranks = tuple(item.rank for item in self.items)
        if len(ranks) != len(set(ranks)):
            raise ValueError("retrieval ranks must be unique")
        return self


class RejectedEvidence(ContractModel):
    source_id: NonEmptyStr
    reason_code: NonEmptyStr


class SourceFilterRequest(ContractModel):
    candidates: tuple[RetrievedEvidence, ...]


class SourceFilterResult(ContractModel):
    eligible: tuple[RetrievedEvidence, ...]
    rejected: tuple[RejectedEvidence, ...] = ()

    @model_validator(mode="after")
    def validate_partition(self) -> "SourceFilterResult":
        eligible_ids = tuple(item.source_id for item in self.eligible)
        rejected_ids = tuple(item.source_id for item in self.rejected)

        if len(eligible_ids) != len(set(eligible_ids)):
            raise ValueError("eligible source IDs must be unique")
        if len(rejected_ids) != len(set(rejected_ids)):
            raise ValueError("rejected source IDs must be unique")
        if set(eligible_ids) & set(rejected_ids):
            raise ValueError("source cannot be both eligible and rejected")
        return self


class RerankRequest(ContractModel):
    query: NonEmptyStr
    candidates: tuple[RetrievedEvidence, ...]


class RerankResult(ContractModel):
    items: tuple[RetrievedEvidence, ...]

    @model_validator(mode="after")
    def validate_unique_ranks(self) -> "RerankResult":
        ranks = tuple(item.rank for item in self.items)
        if len(ranks) != len(set(ranks)):
            raise ValueError("reranked evidence ranks must be unique")
        return self


class ContextBuildRequest(ContractModel):
    query: NonEmptyStr
    evidence: tuple[RetrievedEvidence, ...]


class ContextItem(ContractModel):
    source_id: NonEmptyStr
    content: NonEmptyStr
    position: int = Field(ge=1)
    authority_level: AuthorityLevel
    source_state: SourceState
    eligible_as_final_citation: bool


class ContextBundle(ContractModel):
    query: NonEmptyStr
    items: tuple[ContextItem, ...]
    assembled_context: NonEmptyStr

    @model_validator(mode="after")
    def validate_context_order(self) -> "ContextBundle":
        source_ids = tuple(item.source_id for item in self.items)
        positions = tuple(item.position for item in self.items)

        if len(source_ids) != len(set(source_ids)):
            raise ValueError("context source IDs must be unique")
        if len(positions) != len(set(positions)):
            raise ValueError("context positions must be unique")
        return self


class ProviderRequest(ContractModel):
    query: NonEmptyStr
    context: ContextBundle


class ProviderResponse(ContractModel):
    answer_text: NonEmptyStr
    cited_source_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_citation_uniqueness(self) -> "ProviderResponse":
        if len(self.cited_source_ids) != len(set(self.cited_source_ids)):
            raise ValueError("provider citation source IDs must be unique")
        return self


class CitationValidationRequest(ContractModel):
    provider_response: ProviderResponse
    context: ContextBundle


class CitationCheck(ContractModel):
    source_id: NonEmptyStr
    status: CitationValidationStatus


class CitationValidationResult(ContractModel):
    checks: tuple[CitationCheck, ...]
    all_material_claims_supported: bool


class AnswerOutcome(ContractModel):
    status: Literal["answer"] = "answer"
    answer_text: NonEmptyStr
    cited_source_ids: tuple[NonEmptyStr, ...]
    citation_validation: CitationValidationResult


class RefusalOutcome(ContractModel):
    status: Literal["refusal"] = "refusal"
    reason: RefusalReason
    message: NonEmptyStr


class ErrorOutcome(ContractModel):
    status: Literal["error"] = "error"
    error_code: RuntimeErrorCode
    message: NonEmptyStr
    retryable: bool


RuntimeOutcome = Annotated[
    AnswerOutcome | RefusalOutcome | ErrorOutcome,
    Field(discriminator="status"),
]

runtime_outcome_adapter: TypeAdapter[RuntimeOutcome] = TypeAdapter(RuntimeOutcome)
