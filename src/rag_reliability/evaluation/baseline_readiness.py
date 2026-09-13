"""Phase 5 B0 readiness gate.

This gate proves whether the frozen baseline protocol may proceed to observation.
It must not authorize semantic baseline execution without a context-sensitive,
frozen provider lane.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.baseline_protocol_freeze import (
    Phase5BaselineProtocolFreezeReceipt,
)

_PROTOCOL_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_freeze_v1.json"
)

_READINESS_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_readiness_v1.json"
)

_BLOCKERS = (
    "semantic_provider_adapter_unbound",
    "semantic_provider_configuration_unfrozen",
    "semantic_provider_smoke_test_missing",
)


class Phase5BaselineReadinessReceipt(ContractModel):
    """Evidence-backed readiness state before any B0 observation."""

    receipt_version: Literal[
        "phase5-baseline-readiness-v1"
    ] = "phase5-baseline-readiness-v1"

    protocol_freeze_receipt_sha256: Sha256
    protocol_sha256: Sha256

    protocol_frozen: Literal[True] = True

    control_lane_available: Literal[True] = True

    semantic_provider_adapter_bound: Literal[False] = False
    semantic_provider_configuration_frozen: Literal[False] = False
    semantic_provider_smoke_test_passed: Literal[False] = False

    semantic_metrics_authorized: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False

    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    blockers: tuple[NonEmptyStr, ...] = Field(
        min_length=3,
        max_length=3,
    )

    @model_validator(mode="after")
    def validate_readiness_boundary(self) -> Self:
        if self.blockers != _BLOCKERS:
            raise ValueError("Phase 5 readiness blockers drifted")

        if self.semantic_metrics_authorized:
            raise ValueError(
                "semantic metrics cannot be authorized "
                "without a semantic provider lane"
            )

        if self.baseline_execution_authorized:
            raise ValueError(
                "B0 cannot be authorized while readiness blockers remain"
            )

        return self


def _verified_sha256(path: Path) -> str:
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()

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


def materialize_phase5_baseline_readiness(
    repo_root: Path,
) -> tuple[
    Phase5BaselineReadinessReceipt,
    str,
]:
    """Materialize the current blocked B0 readiness state."""

    freeze_path = (
        repo_root
        / _PROTOCOL_FREEZE_RECEIPT_PATH
    )

    freeze_sha256 = _verified_sha256(
        freeze_path
    )

    freeze_receipt = (
        Phase5BaselineProtocolFreezeReceipt
        .model_validate_json(
            freeze_path.read_bytes()
        )
    )

    if freeze_receipt.protocol_frozen is not True:
        raise ValueError(
            "baseline protocol is not frozen"
        )

    if freeze_receipt.baseline_execution_authorized:
        raise ValueError(
            "protocol freeze unexpectedly authorized B0"
        )

    if freeze_receipt.held_out_outcomes_exposed:
        raise ValueError(
            "HELD_OUT outcomes became exposed"
        )

    receipt = Phase5BaselineReadinessReceipt(
        protocol_freeze_receipt_sha256=freeze_sha256,
        protocol_sha256=freeze_receipt.protocol_sha256,
        blockers=_BLOCKERS,
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _READINESS_RECEIPT_PATH,
        receipt,
    )

    return (
        receipt,
        receipt_sha256,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    receipt, receipt_sha256 = (
        materialize_phase5_baseline_readiness(
            repo_root
        )
    )

    print(
        "PHASE5_PROTOCOL_FROZEN="
        f"{str(receipt.protocol_frozen).lower()}"
    )
    print(
        "PHASE5_CONTROL_LANE_AVAILABLE="
        f"{str(receipt.control_lane_available).lower()}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_BOUND="
        f"{str(receipt.semantic_provider_adapter_bound).lower()}"
    )
    print(
        "PHASE5_SEMANTIC_METRICS_AUTHORIZED="
        f"{str(receipt.semantic_metrics_authorized).lower()}"
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
        "PHASE5_BASELINE_READINESS_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
