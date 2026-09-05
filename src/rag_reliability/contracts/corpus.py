"""Corpus and synthetic-overlay contracts."""

from datetime import date

from pydantic import AnyHttpUrl, AwareDatetime, Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    ChaosProfileId,
    ChaosPurpose,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)

_REAL_SOURCE_ROLES = {
    DataRole.UNIT_FIXTURE,
    DataRole.CORPUS_SOURCE,
    DataRole.HISTORICAL_SOURCE,
    DataRole.BACKGROUND_LOAD_SOURCE,
}


class RealSourceRecord(ContractModel):
    """Manifest record for a real, provenance-bearing source."""

    source_id: NonEmptyStr
    source_family: CorpusSourceFamily
    source_url: AnyHttpUrl
    source_license: NonEmptyStr
    retrieved_at: AwareDatetime
    source_commit_sha_or_version: NonEmptyStr
    document_version: NonEmptyStr
    effective_from: date | None = None
    effective_to: date | None = None
    authority_level: AuthorityLevel
    source_state: SourceState
    product_scope: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr
    content_sha256: Sha256
    title: NonEmptyStr
    topic_tags: tuple[NonEmptyStr, ...] = Field(min_length=1)
    data_role: DataRole

    @model_validator(mode="after")
    def validate_source_semantics(self) -> "RealSourceRecord":
        if self.data_role not in _REAL_SOURCE_ROLES:
            raise ValueError("real source record has an invalid data role")

        if self.authority_level is AuthorityLevel.NONE:
            raise ValueError("real source record cannot have authority_level=none")

        if self.source_state is SourceState.CURRENT:
            if self.authority_level is not AuthorityLevel.AUTHORITATIVE:
                raise ValueError("current source must be authoritative")

        if self.source_state is SourceState.HISTORICAL_COMPARISON:
            if self.authority_level is not AuthorityLevel.HISTORICAL:
                raise ValueError("historical comparison source must be historical")
            if self.data_role is not DataRole.HISTORICAL_SOURCE:
                raise ValueError("historical comparison source must use historical_source role")

        if self.effective_from and self.effective_to:
            if self.effective_to < self.effective_from:
                raise ValueError("effective_to cannot precede effective_from")

        if len(set(self.topic_tags)) != len(self.topic_tags):
            raise ValueError("topic_tags must be unique")

        return self


class SyntheticChaosOverlay(ContractModel):
    """Metadata contract for non-authoritative synthetic chaos material."""

    overlay_id: NonEmptyStr
    synthetic_overlay: bool = True
    authority_level: AuthorityLevel = AuthorityLevel.NONE
    eligible_as_final_citation: bool = False
    eligible_as_gold_evidence: bool = False
    derived_from_source_ids: tuple[NonEmptyStr, ...] = ()
    chaos_purpose: ChaosPurpose
    seed: int = Field(ge=0)
    scenario_id: NonEmptyStr
    profile_id: ChaosProfileId
    data_role: DataRole = DataRole.CHAOS_OVERLAY

    @model_validator(mode="after")
    def validate_overlay_safety(self) -> "SyntheticChaosOverlay":
        if not self.synthetic_overlay:
            raise ValueError("synthetic overlay flag must remain true")
        if self.authority_level is not AuthorityLevel.NONE:
            raise ValueError("synthetic overlay authority must be none")
        if self.eligible_as_final_citation:
            raise ValueError("synthetic overlay cannot be eligible as a final citation")
        if self.eligible_as_gold_evidence:
            raise ValueError("synthetic overlay cannot be eligible as gold evidence")
        if self.data_role is not DataRole.CHAOS_OVERLAY:
            raise ValueError("synthetic overlay must use chaos_overlay data role")
        return self
