"""Freeze the Phase 5 measurement instrument without authorizing B0."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.baseline_protocol_freeze import (
    Phase5BaselineProtocolFreezeReceipt,
)
from rag_reliability.evaluation.measurement_instrument import (
    Phase5MeasurementInstrumentV1,
    build_phase5_measurement_instrument_v1,
)

_BASELINE_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_freeze_v1.json"
)

_INSTRUMENT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_measurement_instrument_v1.json"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_measurement_instrument_freeze_v1.json"
)

_INSTRUMENT_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "evaluation"
    / "measurement_instrument.py"
)

_SCORING_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "evaluation"
    / "measurement_scoring.py"
)

_AGGREGATION_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "evaluation"
    / "measurement_aggregation.py"
)


class Phase5MeasurementInstrumentFreezeReceipt(ContractModel):
    """Custody receipt for the exact Phase 5 measurement instrument."""

    receipt_version: Literal[
        "phase5-measurement-instrument-freeze-v1"
    ] = "phase5-measurement-instrument-freeze-v1"

    instrument_version: Literal[
        "phase5-measurement-instrument-v1"
    ] = "phase5-measurement-instrument-v1"

    protocol_version: Literal[
        "phase5-baseline-protocol-v1"
    ] = "phase5-baseline-protocol-v1"

    instrument_sha256: Sha256

    baseline_protocol_freeze_receipt_sha256: Sha256
    baseline_protocol_sha256: Sha256

    measurement_instrument_source_sha256: Sha256
    measurement_scoring_source_sha256: Sha256
    measurement_aggregation_source_sha256: Sha256

    metric_count: Literal[13] = 13

    fact_scoring_method_id: Literal[
        "evaluator_owned_fact_verdict_v1"
    ] = "evaluator_owned_fact_verdict_v1"

    phase2_substring_fact_scoring_reused: Literal[
        False
    ] = False

    instrument_frozen: Literal[True] = True

    baseline_execution_authorized: Literal[
        False
    ] = False

    held_out_outcomes_exposed: Literal[
        False
    ] = False

    release_eligible: Literal[
        False
    ] = False

    @model_validator(mode="after")
    def validate_freeze_boundary(
        self,
    ) -> Self:
        if self.baseline_execution_authorized:
            raise ValueError(
                "instrument freeze cannot authorize B0"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "instrument freeze cannot expose HELD_OUT outcomes"
            )

        if self.phase2_substring_fact_scoring_reused:
            raise ValueError(
                "Phase 2 substring fact scoring cannot enter "
                "the frozen Phase 5 instrument"
            )

        return self


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _verified_sha256(path: Path) -> str:
    digest = _sha256_file(path)

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    observed = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    expected = f"{digest}  {path.name}"

    if observed != expected:
        raise ValueError(
            f"SHA sidecar mismatch: {path}"
        )

    return digest


def materialize_phase5_measurement_instrument_freeze(
    repo_root: Path,
) -> tuple[
    Phase5MeasurementInstrumentV1,
    str,
    Phase5MeasurementInstrumentFreezeReceipt,
    str,
]:
    """Materialize exact instrument bytes and an external freeze receipt."""

    baseline_freeze_path = (
        repo_root
        / _BASELINE_PROTOCOL_FREEZE_PATH
    )

    baseline_freeze_sha256 = (
        _verified_sha256(
            baseline_freeze_path
        )
    )

    baseline_freeze = (
        Phase5BaselineProtocolFreezeReceipt
        .model_validate_json(
            baseline_freeze_path.read_bytes()
        )
    )

    if not baseline_freeze.protocol_frozen:
        raise ValueError(
            "baseline protocol must already be frozen"
        )

    if baseline_freeze.baseline_execution_authorized:
        raise ValueError(
            "baseline protocol freeze unexpectedly authorized B0"
        )

    if baseline_freeze.held_out_outcomes_exposed:
        raise ValueError(
            "HELD_OUT outcomes were exposed before instrument freeze"
        )

    instrument = (
        build_phase5_measurement_instrument_v1()
    )

    if instrument.baseline_execution_authorized:
        raise ValueError(
            "draft instrument unexpectedly authorizes B0"
        )

    if instrument.held_out_outcomes_exposed:
        raise ValueError(
            "HELD_OUT outcomes became exposed before instrument freeze"
        )

    instrument_sha256 = write_json_with_sha256(
        repo_root / _INSTRUMENT_PATH,
        instrument,
    )

    receipt = (
        Phase5MeasurementInstrumentFreezeReceipt(
            instrument_sha256=(
                instrument_sha256
            ),
            baseline_protocol_freeze_receipt_sha256=(
                baseline_freeze_sha256
            ),
            baseline_protocol_sha256=(
                baseline_freeze.protocol_sha256
            ),
            measurement_instrument_source_sha256=(
                _sha256_file(
                    repo_root
                    / _INSTRUMENT_SOURCE_PATH
                )
            ),
            measurement_scoring_source_sha256=(
                _sha256_file(
                    repo_root
                    / _SCORING_SOURCE_PATH
                )
            ),
            measurement_aggregation_source_sha256=(
                _sha256_file(
                    repo_root
                    / _AGGREGATION_SOURCE_PATH
                )
            ),
        )
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_RECEIPT_PATH,
        receipt,
    )

    return (
        instrument,
        instrument_sha256,
        receipt,
        receipt_sha256,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    (
        instrument,
        instrument_sha256,
        receipt,
        receipt_sha256,
    ) = (
        materialize_phase5_measurement_instrument_freeze(
            repo_root
        )
    )

    print(
        "PHASE5_MEASUREMENT_INSTRUMENT_VERSION="
        f"{instrument.instrument_version}"
    )
    print(
        "PHASE5_MEASUREMENT_INSTRUMENT_SHA256="
        f"{instrument_sha256}"
    )
    print(
        "PHASE5_MEASUREMENT_INSTRUMENT_FROZEN="
        f"{str(receipt.instrument_frozen).lower()}"
    )
    print(
        "PHASE5_MEASUREMENT_METRIC_COUNT="
        f"{receipt.metric_count}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(receipt.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED="
        f"{str(receipt.held_out_outcomes_exposed).lower()}"
    )
    print(
        "PHASE5_MEASUREMENT_INSTRUMENT_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
