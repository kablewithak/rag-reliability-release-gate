from __future__ import annotations

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.baseline_protocol import (
    build_phase5_baseline_protocol_v1,
)
from rag_reliability.evaluation.measurement_instrument import (
    Phase5FactAssessmentSet,
    Phase5FactVerdict,
    Phase5MeasurementInstrumentV1,
    build_phase5_measurement_instrument_v1,
)


def test_instrument_metric_ids_match_frozen_protocol() -> None:
    protocol = build_phase5_baseline_protocol_v1()
    instrument = build_phase5_measurement_instrument_v1()

    observed = tuple(
        metric.metric_id
        for metric in instrument.metric_definitions
    )

    assert (
        observed
        == protocol.measurement.required_metric_ids
    )


def test_instrument_keeps_gold_outside_runtime() -> None:
    instrument = build_phase5_measurement_instrument_v1()

    assert (
        instrument.fact_scoring.runtime_gold_access_allowed
        is False
    )
    assert (
        instrument.fact_scoring.lexical_substring_matching_allowed
        is False
    )
    assert (
        instrument.phase2_substring_fact_scoring_reused
        is False
    )


def test_fact_satisfied_requires_answer_span() -> None:
    with pytest.raises(
        ValidationError,
        match="supporting_answer_span",
    ):
        Phase5FactVerdict(
            fact_id="fact-1",
            verdict="satisfied",
        )


def test_fact_not_satisfied_requires_rationale() -> None:
    with pytest.raises(
        ValidationError,
        match="requires rationale",
    ):
        Phase5FactVerdict(
            fact_id="fact-1",
            verdict="not_satisfied",
        )


def test_fact_assessment_ids_must_be_unique() -> None:
    verdict = Phase5FactVerdict(
        fact_id="fact-1",
        verdict="satisfied",
        supporting_answer_span="Supported text.",
    )

    with pytest.raises(
        ValidationError,
        match="must be unique",
    ):
        Phase5FactAssessmentSet(
            case_id="case-1",
            verdicts=(
                verdict,
                verdict,
            ),
        )


def test_metric_definition_drift_is_rejected() -> None:
    instrument = build_phase5_measurement_instrument_v1()
    payload = instrument.model_dump()

    payload["metric_definitions"][0][
        "metric_id"
    ] = "drifted_metric"

    with pytest.raises(
        ValidationError,
        match="metric definitions drifted",
    ):
        Phase5MeasurementInstrumentV1.model_validate(
            payload
        )


def test_instrument_does_not_authorize_execution() -> None:
    instrument = build_phase5_measurement_instrument_v1()

    assert instrument.instrument_status == "draft_unfrozen"
    assert instrument.baseline_execution_authorized is False
    assert instrument.held_out_outcomes_exposed is False
