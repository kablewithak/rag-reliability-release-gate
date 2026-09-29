from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rag_reliability.evaluation.measurement_instrument_freeze import (
    Phase5MeasurementInstrumentFreezeReceipt,
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _historical_receipt() -> Phase5MeasurementInstrumentFreezeReceipt:
    return (
        Phase5MeasurementInstrumentFreezeReceipt
        .model_validate_json(
            RECEIPT_PATH.read_bytes()
        )
    )


def test_historical_v1_receipt_sidecar_remains_self_consistent() -> None:
    sidecar = RECEIPT_PATH.with_suffix(
        RECEIPT_PATH.suffix + ".sha256"
    )

    assert sidecar.read_text(
        encoding="utf-8"
    ).strip() == (
        f"{_sha256(RECEIPT_PATH)}  {RECEIPT_PATH.name}"
    )


def test_historical_v1_source_binding_defect_is_explicit() -> None:
    receipt = _historical_receipt()

    assert receipt.measurement_instrument_source_sha256 == (
        "ee762d1efc9ebb8a0845d51e9795e65675ae4a202821a1f20c1db37dbe20f342"
    )
    assert _sha256(INSTRUMENT_SOURCE_PATH) == (
        "72a718ef8b282c1c2d3e4e1d143222addcca777bd8ee159f51013a8a231a9a45"
    )
    assert (
        receipt.measurement_instrument_source_sha256
        != _sha256(INSTRUMENT_SOURCE_PATH)
    )


def test_v1_materialization_fails_closed_before_mutating_frozen_bytes() -> None:
    instrument_before = INSTRUMENT_PATH.read_bytes()
    receipt_before = RECEIPT_PATH.read_bytes()
    receipt_sidecar_path = RECEIPT_PATH.with_suffix(
        RECEIPT_PATH.suffix + ".sha256"
    )
    receipt_sidecar_before = receipt_sidecar_path.read_bytes()

    with pytest.raises(
        ValueError,
        match="historical v1 measurement freeze source binding mismatch",
    ):
        materialize_phase5_measurement_instrument_freeze(
            ROOT
        )

    assert INSTRUMENT_PATH.read_bytes() == instrument_before
    assert RECEIPT_PATH.read_bytes() == receipt_before
    assert receipt_sidecar_path.read_bytes() == receipt_sidecar_before


def test_historical_v1_preserves_measurement_boundary() -> None:
    receipt = _historical_receipt()

    assert receipt.metric_count == 13
    assert (
        receipt.fact_scoring_method_id
        == "evaluator_owned_fact_verdict_v1"
    )
    assert receipt.phase2_substring_fact_scoring_reused is False
    assert receipt.instrument_frozen is True
    assert receipt.baseline_execution_authorized is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.release_eligible is False
