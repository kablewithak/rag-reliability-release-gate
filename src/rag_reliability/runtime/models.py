"""Internal deterministic runtime models for the Phase 2 thin slice."""

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import RuntimeOutcome
from rag_reliability.contracts.tracing import TraceRecord


class IndexedDocument(ContractModel):
    """Small development document used by the deterministic retriever."""

    source_id: NonEmptyStr
    content: NonEmptyStr
    authority_level: AuthorityLevel
    source_state: SourceState
    product_scope: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr
    synthetic_overlay: bool = False
    eligible_as_final_citation: bool = True

    @model_validator(mode="after")
    def validate_synthetic_authority(self) -> "IndexedDocument":
        if self.synthetic_overlay:
            if self.authority_level is not AuthorityLevel.NONE:
                raise ValueError("synthetic document must have authority_level=none")
            if self.eligible_as_final_citation:
                raise ValueError("synthetic document cannot be a final citation")
        return self


class ReplayEntry(ContractModel):
    """Provider-side replay fixture. It contains no evaluator-owned fields."""

    query: NonEmptyStr
    answer_text: NonEmptyStr
    cited_source_ids: tuple[NonEmptyStr, ...] = Field(min_length=1)


class PipelineExecution(ContractModel):
    """Internal execution result before evaluation scoring."""

    outcome: RuntimeOutcome
    trace: TraceRecord
