from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import TraceStage, TraceStatus
from rag_reliability.contracts.tracing import TraceEvent, TraceRecord


def test_trace_event_rejects_raw_prompt_field() -> None:
    with pytest.raises(ValidationError):
        TraceEvent.model_validate(
            {
                "event_id": "event-1",
                "stage": "retrieval",
                "status": "ok",
                "occurred_at": datetime.now(UTC),
                "duration_ms": 2.0,
                "raw_prompt": "should never be in metadata-safe trace",
            }
        )


def test_error_event_requires_error_code() -> None:
    with pytest.raises(ValidationError):
        TraceEvent(
            event_id="event-1",
            stage=TraceStage.PROVIDER_GENERATION,
            status=TraceStatus.ERROR,
            occurred_at=datetime.now(UTC),
            duration_ms=10.0,
        )


def test_trace_record_rejects_reverse_time_order() -> None:
    now = datetime.now(UTC)
    event = TraceEvent(
        event_id="event-1",
        stage=TraceStage.RETRIEVAL,
        status=TraceStatus.OK,
        occurred_at=now,
        duration_ms=1.0,
    )

    with pytest.raises(ValidationError):
        TraceRecord(
            trace_id="trace-1",
            case_id="dev-001",
            configuration_id="baseline-1",
            started_at=now,
            ended_at=now - timedelta(seconds=1),
            events=(event,),
        )
