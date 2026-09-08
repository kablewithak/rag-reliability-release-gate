"""Strict request/result contracts for the runtime RAG path."""

from collections.abc import Mapping
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


def _migrate_legacy_identity(
    value: object,
) -> object:
    if not isinstance(value, Mapping):
        return value

    data = dict(value)
    legacy_id = data.pop("source_id", None)

    if legacy_id is None:
        return data

    canonical_id = data.get("evidence_id")

    if (
        canonical_id is not None
        and canonical_id != legacy_id
    ):
        raise ValueError(
            "legacy source_id conflicts with evidence_id"
        )

    data.setdefault(
        "evidence_id",
        legacy_id,
    )
    data.setdefault(
        "source_ids",
        (legacy_id,),
    )
    data.setdefault(
        "document_ids",
        (),
    )

    return data


def _migrate_legacy_citations(
    value: object,
) -> object:
    if not isinstance(value, Mapping):
        return value

    data = dict(value)

    legacy_ids = data.pop(
        "cited_source_ids",
        None,
    )

    if legacy_ids is None:
        return data

    canonical_ids = data.get(
        "cited_evidence_ids"
    )

    if (
        canonical_ids is not None
        and canonical_ids != legacy_ids
    ):
        raise ValueError(
            "legacy cited_source_ids conflicts "
            "with cited_evidence_ids"
        )

    data.setdefault(
        "cited_evidence_ids",
        legacy_ids,
    )

    return data


def _validate_identity_tuple(
    values: tuple[str, ...],
    *,
    field_name: str,
) -> None:
    if len(values) != len(set(values)):
        raise ValueError(
            f"{field_name} must be unique"
        )


class RetrievalRequest(ContractModel):
    query: NonEmptyStr
    top_k: int = Field(ge=1)


class RetrievedEvidence(ContractModel):
    """One ranked retrieval unit with separate provenance identities."""

    evidence_id: NonEmptyStr
    source_ids: tuple[NonEmptyStr, ...] = Field(
        min_length=1
    )
    document_ids: tuple[NonEmptyStr, ...] = ()

    content: NonEmptyStr
    rank: int = Field(ge=1)
    score: float
    authority_level: AuthorityLevel
    source_state: SourceState
    product_scope: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr
    synthetic_overlay: bool = False
    eligible_as_final_citation: bool = True

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_source_id(
        cls,
        value: object,
    ) -> object:
        return _migrate_legacy_identity(
            value
        )

    @model_validator(mode="after")
    def validate_evidence(self) -> "RetrievedEvidence":
        _validate_identity_tuple(
            self.source_ids,
            field_name="source_ids",
        )
        _validate_identity_tuple(
            self.document_ids,
            field_name="document_ids",
        )

        if self.synthetic_overlay:
            if (
                self.authority_level
                is not AuthorityLevel.NONE
            ):
                raise ValueError(
                    "synthetic retrieved evidence "
                    "must have authority_level=none"
                )

            if self.eligible_as_final_citation:
                raise ValueError(
                    "synthetic retrieved evidence "
                    "cannot be a final citation"
                )

        return self

    @property
    def source_id(self) -> str:
        """Temporary Phase 2 retrieval-identity compatibility alias."""

        return self.evidence_id


class RetrievalResult(ContractModel):
    items: tuple[RetrievedEvidence, ...]

    @model_validator(mode="after")
    def validate_unique_ranks_and_evidence(
        self,
    ) -> "RetrievalResult":
        ranks = tuple(
            item.rank
            for item in self.items
        )

        if len(ranks) != len(set(ranks)):
            raise ValueError(
                "retrieval ranks must be unique"
            )

        evidence_ids = tuple(
            item.evidence_id
            for item in self.items
        )

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            raise ValueError(
                "retrieval evidence IDs must be unique"
            )

        return self


class RejectedEvidence(ContractModel):
    evidence_id: NonEmptyStr
    source_ids: tuple[NonEmptyStr, ...] = Field(
        min_length=1
    )
    document_ids: tuple[NonEmptyStr, ...] = ()
    reason_code: NonEmptyStr

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_source_id(
        cls,
        value: object,
    ) -> object:
        return _migrate_legacy_identity(
            value
        )

    @model_validator(mode="after")
    def validate_lineage(
        self,
    ) -> "RejectedEvidence":
        _validate_identity_tuple(
            self.source_ids,
            field_name="source_ids",
        )
        _validate_identity_tuple(
            self.document_ids,
            field_name="document_ids",
        )

        return self

    @property
    def source_id(self) -> str:
        """Temporary Phase 2 retrieval-identity compatibility alias."""

        return self.evidence_id


class SourceFilterRequest(ContractModel):
    candidates: tuple[RetrievedEvidence, ...]


class SourceFilterResult(ContractModel):
    eligible: tuple[RetrievedEvidence, ...]
    rejected: tuple[RejectedEvidence, ...] = ()

    @model_validator(mode="after")
    def validate_partition(
        self,
    ) -> "SourceFilterResult":
        eligible_ids = tuple(
            item.evidence_id
            for item in self.eligible
        )

        rejected_ids = tuple(
            item.evidence_id
            for item in self.rejected
        )

        if (
            len(eligible_ids)
            != len(set(eligible_ids))
        ):
            raise ValueError(
                "eligible evidence IDs must be unique"
            )

        if (
            len(rejected_ids)
            != len(set(rejected_ids))
        ):
            raise ValueError(
                "rejected evidence IDs must be unique"
            )

        if (
            set(eligible_ids)
            & set(rejected_ids)
        ):
            raise ValueError(
                "evidence cannot be both "
                "eligible and rejected"
            )

        return self


class RerankRequest(ContractModel):
    query: NonEmptyStr
    candidates: tuple[RetrievedEvidence, ...]


class RerankResult(ContractModel):
    items: tuple[RetrievedEvidence, ...]

    @model_validator(mode="after")
    def validate_unique_ranks_and_evidence(
        self,
    ) -> "RerankResult":
        ranks = tuple(
            item.rank
            for item in self.items
        )

        if len(ranks) != len(set(ranks)):
            raise ValueError(
                "reranked evidence ranks must be unique"
            )

        evidence_ids = tuple(
            item.evidence_id
            for item in self.items
        )

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            raise ValueError(
                "reranked evidence IDs must be unique"
            )

        return self


class ContextBuildRequest(ContractModel):
    query: NonEmptyStr
    evidence: tuple[RetrievedEvidence, ...]


class ContextItem(ContractModel):
    evidence_id: NonEmptyStr
    source_ids: tuple[NonEmptyStr, ...] = Field(
        min_length=1
    )
    document_ids: tuple[NonEmptyStr, ...] = ()

    content: NonEmptyStr
    position: int = Field(ge=1)
    authority_level: AuthorityLevel
    source_state: SourceState
    eligible_as_final_citation: bool

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_source_id(
        cls,
        value: object,
    ) -> object:
        return _migrate_legacy_identity(
            value
        )

    @model_validator(mode="after")
    def validate_lineage(
        self,
    ) -> "ContextItem":
        _validate_identity_tuple(
            self.source_ids,
            field_name="source_ids",
        )
        _validate_identity_tuple(
            self.document_ids,
            field_name="document_ids",
        )

        return self

    @property
    def source_id(self) -> str:
        """Temporary Phase 2 retrieval-identity compatibility alias."""

        return self.evidence_id


class ContextBundle(ContractModel):
    query: NonEmptyStr
    items: tuple[ContextItem, ...]
    assembled_context: NonEmptyStr

    @model_validator(mode="after")
    def validate_context_order(
        self,
    ) -> "ContextBundle":
        evidence_ids = tuple(
            item.evidence_id
            for item in self.items
        )

        positions = tuple(
            item.position
            for item in self.items
        )

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            raise ValueError(
                "context evidence IDs must be unique"
            )

        if (
            len(positions)
            != len(set(positions))
        ):
            raise ValueError(
                "context positions must be unique"
            )

        return self


class ProviderRequest(ContractModel):
    query: NonEmptyStr
    context: ContextBundle


class ProviderResponse(ContractModel):
    answer_text: NonEmptyStr
    cited_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_cited_source_ids(
        cls,
        value: object,
    ) -> object:
        return _migrate_legacy_citations(
            value
        )

    @model_validator(mode="after")
    def validate_citation_uniqueness(
        self,
    ) -> "ProviderResponse":
        if (
            len(self.cited_evidence_ids)
            != len(set(self.cited_evidence_ids))
        ):
            raise ValueError(
                "provider citation evidence IDs "
                "must be unique"
            )

        return self

    @property
    def cited_source_ids(
        self,
    ) -> tuple[str, ...]:
        """Temporary Phase 2 compatibility alias."""

        return self.cited_evidence_ids


class CitationValidationRequest(ContractModel):
    provider_response: ProviderResponse
    context: ContextBundle


class CitationCheck(ContractModel):
    evidence_id: NonEmptyStr
    status: CitationValidationStatus

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_source_id(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, Mapping):
            return value

        data = dict(value)

        legacy_id = data.pop(
            "source_id",
            None,
        )

        if legacy_id is None:
            return data

        canonical_id = data.get(
            "evidence_id"
        )

        if (
            canonical_id is not None
            and canonical_id != legacy_id
        ):
            raise ValueError(
                "legacy source_id conflicts "
                "with evidence_id"
            )

        data.setdefault(
            "evidence_id",
            legacy_id,
        )

        return data

    @property
    def source_id(self) -> str:
        """Temporary Phase 2 compatibility alias."""

        return self.evidence_id


class CitationValidationResult(ContractModel):
    checks: tuple[CitationCheck, ...]
    all_material_claims_supported: bool


class AnswerOutcome(ContractModel):
    status: Literal["answer"] = "answer"
    answer_text: NonEmptyStr
    cited_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ]
    citation_validation: CitationValidationResult

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_cited_source_ids(
        cls,
        value: object,
    ) -> object:
        return _migrate_legacy_citations(
            value
        )

    @property
    def cited_source_ids(
        self,
    ) -> tuple[str, ...]:
        """Temporary Phase 2 compatibility alias."""

        return self.cited_evidence_ids


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

runtime_outcome_adapter: TypeAdapter[
    RuntimeOutcome
] = TypeAdapter(RuntimeOutcome)