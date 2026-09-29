"""Supersede the stale Phase 5 measurement source binding without rewriting v1."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final, Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.baseline_protocol_freeze import (
    Phase5BaselineProtocolFreezeReceipt,
)
from rag_reliability.evaluation.measurement_instrument_freeze import (
    Phase5MeasurementInstrumentFreezeReceipt,
)

_HISTORICAL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_measurement_instrument_freeze_v1.json"
)

_INSTRUMENT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_measurement_instrument_v1.json"
)

_BASELINE_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_freeze_v1.json"
)

_CORRECTED_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_measurement_instrument_freeze_v2.json"
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

_HISTORICAL_FREEZE_SHA256: Final[
    Literal[
        "66a6da58a69318de26ad5d3b06272d42a6e067834713dfab77a27662617da29e"
    ]
] = "66a6da58a69318de26ad5d3b06272d42a6e067834713dfab77a27662617da29e"

_HISTORICAL_SOURCE_SHA256: Final[
    Literal[
        "ee762d1efc9ebb8a0845d51e9795e65675ae4a202821a1f20c1db37dbe20f342"
    ]
] = "ee762d1efc9ebb8a0845d51e9795e65675ae4a202821a1f20c1db37dbe20f342"

_CORRECTED_SOURCE_SHA256 = (
    "72a718ef8b282c1c2d3e4e1d143222addcca777bd8ee159f51013a8a231a9a45"
)


class Phase5MeasurementInstrumentFreezeReceiptV2(ContractModel):
    """Correct exact-byte source custody while preserving v1 evidence."""

    receipt_version: Literal[
        "phase5-measurement-instrument-freeze-v2"
    ] = "phase5-measurement-instrument-freeze-v2"

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

    supersedes_freeze_receipt_sha256: Literal[
        "66a6da58a69318de26ad5d3b06272d42a6e067834713dfab77a27662617da29e"
    ] = _HISTORICAL_FREEZE_SHA256

    superseded_v1_measurement_instrument_source_sha256: Literal[
        "ee762d1efc9ebb8a0845d51e9795e65675ae4a202821a1f20c1db37dbe20f342"
    ] = _HISTORICAL_SOURCE_SHA256

    source_binding_correction_applied: Literal[True] = True
    historical_v1_preserved: Literal[True] = True

    metric_count: Literal[13] = 13

    fact_scoring_method_id: Literal[
        "evaluator_owned_fact_verdict_v1"
    ] = "evaluator_owned_fact_verdict_v1"

    phase2_substring_fact_scoring_reused: Literal[
        False
    ] = False

    instrument_frozen: Literal[True] = True
    baseline_execution_authorized: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_correction_boundary(self) -> Self:
        if (
            self.measurement_instrument_source_sha256
            == self.superseded_v1_measurement_instrument_source_sha256
        ):
            raise ValueError(
                "v2 must correct the stale v1 measurement source binding"
            )

        if self.baseline_execution_authorized:
            raise ValueError(
                "measurement freeze v2 cannot authorize B0"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "measurement freeze v2 cannot expose HELD_OUT outcomes"
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


def materialize_phase5_measurement_instrument_freeze_v2(
    repo_root: Path,
) -> tuple[
    Phase5MeasurementInstrumentFreezeReceiptV2,
    str,
]:
    """Write only the v2 correction receipt; never rewrite v1 evidence."""

    historical_freeze_path = (
        repo_root / _HISTORICAL_FREEZE_PATH
    )
    historical_freeze_sha256 = (
        _verified_sha256(
            historical_freeze_path
        )
    )

    if historical_freeze_sha256 != _HISTORICAL_FREEZE_SHA256:
        raise ValueError(
            "historical v1 freeze receipt bytes drifted"
        )

    historical = (
        Phase5MeasurementInstrumentFreezeReceipt
        .model_validate_json(
            historical_freeze_path.read_bytes()
        )
    )

    if (
        historical.measurement_instrument_source_sha256
        != _HISTORICAL_SOURCE_SHA256
    ):
        raise ValueError(
            "historical v1 source-binding claim drifted"
        )

    instrument_sha256 = _verified_sha256(
        repo_root / _INSTRUMENT_PATH
    )

    if instrument_sha256 != historical.instrument_sha256:
        raise ValueError(
            "frozen measurement instrument bytes drifted"
        )

    baseline_freeze_path = (
        repo_root / _BASELINE_PROTOCOL_FREEZE_PATH
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

    if (
        baseline_freeze_sha256
        != historical.baseline_protocol_freeze_receipt_sha256
    ):
        raise ValueError(
            "baseline protocol freeze receipt drifted"
        )

    if (
        baseline_freeze.protocol_sha256
        != historical.baseline_protocol_sha256
    ):
        raise ValueError(
            "baseline protocol binding drifted"
        )

    measurement_source_sha256 = _sha256_file(
        repo_root / _INSTRUMENT_SOURCE_PATH
    )

    if measurement_source_sha256 != _CORRECTED_SOURCE_SHA256:
        raise ValueError(
            "current measurement instrument source bytes do not match "
            "the preregistered v2 correction"
        )

    scoring_source_sha256 = _sha256_file(
        repo_root / _SCORING_SOURCE_PATH
    )

    if (
        scoring_source_sha256
        != historical.measurement_scoring_source_sha256
    ):
        raise ValueError(
            "measurement scoring source drifted"
        )

    aggregation_source_sha256 = _sha256_file(
        repo_root / _AGGREGATION_SOURCE_PATH
    )

    if (
        aggregation_source_sha256
        != historical.measurement_aggregation_source_sha256
    ):
        raise ValueError(
            "measurement aggregation source drifted"
        )

    receipt = Phase5MeasurementInstrumentFreezeReceiptV2(
        instrument_sha256=instrument_sha256,
        baseline_protocol_freeze_receipt_sha256=(
            baseline_freeze_sha256
        ),
        baseline_protocol_sha256=(
            baseline_freeze.protocol_sha256
        ),
        measurement_instrument_source_sha256=(
            measurement_source_sha256
        ),
        measurement_scoring_source_sha256=(
            scoring_source_sha256
        ),
        measurement_aggregation_source_sha256=(
            aggregation_source_sha256
        ),
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _CORRECTED_FREEZE_PATH,
        receipt,
    )

    return receipt, receipt_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    receipt, receipt_sha256 = (
        materialize_phase5_measurement_instrument_freeze_v2(
            repo_root
        )
    )

    print(
        "PHASE5_MEASUREMENT_INSTRUMENT_FREEZE_VERSION="
        f"{receipt.receipt_version}"
    )
    print(
        "PHASE5_MEASUREMENT_SOURCE_SHA256="
        f"{receipt.measurement_instrument_source_sha256}"
    )
    print(
        "PHASE5_MEASUREMENT_FREEZE_SUPERSEDES_SHA256="
        f"{receipt.supersedes_freeze_receipt_sha256}"
    )
    print(
        "PHASE5_MEASUREMENT_SOURCE_BINDING_CORRECTION="
        f"{str(receipt.source_binding_correction_applied).lower()}"
    )
    print(
        "PHASE5_HISTORICAL_V1_PRESERVED="
        f"{str(receipt.historical_v1_preserved).lower()}"
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
        "PHASE5_MEASUREMENT_INSTRUMENT_FREEZE_V2_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
