from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.measurement_instrument_freeze import (
    materialize_phase5_measurement_instrument_freeze,
)

ROOT = Path(__file__).resolve().parents[2]

INSTRUMENT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_measurement_instrument_v1.json"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_measurement_instrument_freeze_v1.json"
)

INSTRUMENT_SOURCE_PATH = (
    ROOT
    / "src"
    / "rag_reliability"
    / "evaluation"
    / "measurement_instrument.py"
)

SCORING_SOURCE_PATH = (
    ROOT
    / "src"
    / "rag_reliability"
    / "evaluation"
    / "measurement_scoring.py"
)

AGGREGATION_SOURCE_PATH = (
    ROOT
    / "src"
    / "rag_reliability"
    / "evaluation"
    / "measurement_aggregation.py"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_materialization_binds_exact_instrument_bytes() -> None:
    (
        instrument,
        instrument_sha256,
        receipt,
        receipt_sha256,
    ) = (
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )
    )

    assert instrument_sha256 == _sha256(
        INSTRUMENT_PATH
    )
    assert (
        receipt.instrument_sha256
        == instrument_sha256
    )
    assert receipt_sha256 == _sha256(
        RECEIPT_PATH
    )

    assert instrument.baseline_execution_authorized is False
    assert receipt.instrument_frozen is True
    assert receipt.baseline_execution_authorized is False


def test_freeze_binds_measurement_source_files() -> None:
    (
        _instrument,
        _instrument_sha256,
        receipt,
        _receipt_sha256,
    ) = (
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )
    )

    assert (
        receipt.measurement_instrument_source_sha256
        == _sha256(
            INSTRUMENT_SOURCE_PATH
        )
    )

    assert (
        receipt.measurement_scoring_source_sha256
        == _sha256(
            SCORING_SOURCE_PATH
        )
    )

    assert (
        receipt.measurement_aggregation_source_sha256
        == _sha256(
            AGGREGATION_SOURCE_PATH
        )
    )


def test_freeze_preserves_measurement_boundary() -> None:
    (
        instrument,
        _instrument_sha256,
        receipt,
        _receipt_sha256,
    ) = (
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )
    )

    assert receipt.metric_count == 13

    assert (
        receipt.fact_scoring_method_id
        == "evaluator_owned_fact_verdict_v1"
    )

    assert (
        instrument.fact_scoring
        .lexical_substring_matching_allowed
        is False
    )

    assert (
        receipt.phase2_substring_fact_scoring_reused
        is False
    )

    assert receipt.held_out_outcomes_exposed is False
    assert receipt.release_eligible is False


def test_freeze_binds_existing_baseline_protocol_freeze() -> None:
    (
        _instrument,
        _instrument_sha256,
        receipt,
        _receipt_sha256,
    ) = (
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )
    )

    baseline_receipt_path = (
        ROOT
        / "artifacts"
        / "development"
        / "phase5_baseline_protocol_freeze_v1.json"
    )

    assert (
        receipt.baseline_protocol_freeze_receipt_sha256
        == _sha256(
            baseline_receipt_path
        )
    )


def test_materialization_is_deterministic() -> None:
    first = (
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )
    )
    second = (
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[3] == second[3]
