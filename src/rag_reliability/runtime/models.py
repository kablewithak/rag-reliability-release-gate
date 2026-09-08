"""Internal deterministic runtime models."""

from collections.abc import Mapping

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import RuntimeOutcome
from rag_reliability.contracts.tracing import TraceRecord


class IndexedDocument(ContractModel):
    """One retrievable evidence unit with explicit provenance lineage."""

    evidence_id: NonEmptyStr
    source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=1)
    document_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    content: NonEmptyStr
    authority_level: AuthorityLevel
    source_state: SourceState
    product_scope: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr
    synthetic_overlay: bool = False
    eligible_as_final_citation: bool = True

    @model_validator(mode="before")
    @classmethod
    def migrate_phase2_source_id(
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

        data.setdefault(
            "source_ids",
            (legacy_id,),
        )

        data.setdefault(
            "document_ids",
            (),
        )

        return data

    @model_validator(mode="after")
    def validate_document(
        self,
    ) -> "IndexedDocument":
        if (
            len(self.source_ids)
            != len(set(self.source_ids))
        ):
            raise ValueError(
                "indexed source IDs must be unique"
            )

        if (
            len(self.document_ids)
            != len(set(self.document_ids))
        ):
            raise ValueError(
                "indexed document IDs must be unique"
            )

        if self.synthetic_overlay:
            if (
                self.authority_level
                is not AuthorityLevel.NONE
            ):
                raise ValueError(
                    "synthetic document must have "
                    "authority_level=none"
                )

            if self.eligible_as_final_citation:
                raise ValueError(
                    "synthetic document cannot be "
                    "a final citation"
                )

        return self

    @property
    def source_id(self) -> str:
        """Temporary Phase 2 retrieval-identity compatibility alias."""

        return self.evidence_id


class ReplayEntry(ContractModel):
    """Provider replay fixture with no evaluator-owned fields."""

    query: NonEmptyStr
    answer_text: NonEmptyStr
    cited_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def migrate_phase2_citations(
        cls,
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

    @property
    def cited_source_ids(
        self,
    ) -> tuple[str, ...]:
        """Temporary Phase 2 compatibility alias."""

        return self.cited_evidence_ids


class PipelineExecution(ContractModel):
    """Internal execution result before evaluation scoring."""

    outcome: RuntimeOutcome
    trace: TraceRecord