from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.measurement_instrument_freeze_v2 import (
    materialize_phase5_measurement_instrument_freeze_v2,
)

ROOT = Path(__file__).resolve().parents[2]

V1_RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_measurement_instrument_freeze_v1.json"
)

V2_RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_measurement_instrument_freeze_v2.json"
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


def test_v2_corrects_source_binding_without_rewriting_v1() -> None:
    v1_before = V1_RECEIPT_PATH.read_bytes()
    v1_sidecar_path = V1_RECEIPT_PATH.with_suffix(
        V1_RECEIPT_PATH.suffix + ".sha256"
    )
    v1_sidecar_before = v1_sidecar_path.read_bytes()

    receipt, receipt_sha256 = (
        materialize_phase5_measurement_instrument_freeze_v2(
            ROOT
        )
    )

    assert V1_RECEIPT_PATH.read_bytes() == v1_before
    assert v1_sidecar_path.read_bytes() == v1_sidecar_before

    assert receipt.supersedes_freeze_receipt_sha256 == (
        "66a6da58a69318de26ad5d3b06272d42a6e067834713dfab77a27662617da29e"
    )
    assert receipt.superseded_v1_measurement_instrument_source_sha256 == (
        "ee762d1efc9ebb8a0845d51e9795e65675ae4a202821a1f20c1db37dbe20f342"
    )
    assert receipt.measurement_instrument_source_sha256 == (
        _sha256(INSTRUMENT_SOURCE_PATH)
    )
    assert receipt.measurement_instrument_source_sha256 == (
        "72a718ef8b282c1c2d3e4e1d143222addcca777bd8ee159f51013a8a231a9a45"
    )

    assert receipt_sha256 == _sha256(
        V2_RECEIPT_PATH
    )


def test_v2_preserves_measurement_and_execution_boundaries() -> None:
    receipt, _receipt_sha256 = (
        materialize_phase5_measurement_instrument_freeze_v2(
            ROOT
        )
    )

    assert receipt.source_binding_correction_applied is True
    assert receipt.historical_v1_preserved is True
    assert receipt.instrument_frozen is True
    assert receipt.metric_count == 13

    assert (
        receipt.fact_scoring_method_id
        == "evaluator_owned_fact_verdict_v1"
    )
    assert receipt.phase2_substring_fact_scoring_reused is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.release_eligible is False


def test_v2_materialization_is_deterministic() -> None:
    first = (
        materialize_phase5_measurement_instrument_freeze_v2(
            ROOT
        )
    )
    second = (
        materialize_phase5_measurement_instrument_freeze_v2(
            ROOT
        )
    )

    assert first[1] == second[1]
