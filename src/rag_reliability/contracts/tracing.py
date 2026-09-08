"""Metadata-safe trace contracts."""

from pydantic import AwareDatetime, Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import (
    ChaosProfileId,
    FailureLabel,
    TraceStage,
    TraceStatus,
)


class TraceEvent(ContractModel):
    """A metadata-only stage event; raw prompt/context/output fields are absent."""

    event_id: NonEmptyStr
    stage: TraceStage
    status: TraceStatus
    occurred_at: AwareDatetime
    duration_ms: float = Field(ge=0.0)

    evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    error_code: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_event(
        self,
    ) -> "TraceEvent":
        if (
            len(self.evidence_ids)
            != len(set(self.evidence_ids))
        ):
            raise ValueError(
                "trace evidence IDs must be unique"
            )

        if (
            len(self.source_ids)
            != len(set(self.source_ids))
        ):
            raise ValueError(
                "trace source IDs must be unique"
            )

        if (
            self.status is TraceStatus.ERROR
            and self.error_code is None
        ):
            raise ValueError(
                "error trace event requires error_code"
            )

        if (
            self.status is not TraceStatus.ERROR
            and self.error_code is not None
        ):
            raise ValueError(
                "error_code is only valid for "
                "error trace events"
            )

        return self


class TraceRecord(ContractModel):
    """Trace envelope preserving attribution without raw provider bodies."""

    trace_id: NonEmptyStr
    case_id: NonEmptyStr
    configuration_id: NonEmptyStr
    profile_id: ChaosProfileId | None = None
    started_at: AwareDatetime
    ended_at: AwareDatetime
    events: tuple[TraceEvent, ...] = Field(
        min_length=1
    )
    primary_failure: FailureLabel | None = None
    secondary_failures: tuple[
        FailureLabel,
        ...,
    ] = ()

    @model_validator(mode="after")
    def validate_trace_order(
        self,
    ) -> "TraceRecord":
        if self.ended_at < self.started_at:
            raise ValueError(
                "ended_at cannot precede started_at"
            )

        if (
            self.primary_failure
            in self.secondary_failures
        ):
            raise ValueError(
                "primary failure cannot be repeated "
                "as a secondary failure"
            )

        if (
            len(set(self.secondary_failures))
            != len(self.secondary_failures)
        ):
            raise ValueError(
                "secondary failures must be unique"
            )

        return self