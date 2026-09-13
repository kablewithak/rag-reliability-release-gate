"""Freeze the Phase 5 baseline protocol without authorizing B0 execution."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.baseline_protocol import (
    Phase5BaselineProtocolV1,
    build_phase5_baseline_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_v1.json"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_freeze_v1.json"
)


class Phase5BaselineProtocolFreezeReceipt(ContractModel):
    """External custody receipt for the exact Phase 5 B0 protocol."""

    receipt_version: Literal[
        "phase5-baseline-protocol-freeze-v1"
    ] = "phase5-baseline-protocol-freeze-v1"

    protocol_version: Literal[
        "phase5-baseline-protocol-v1"
    ] = "phase5-baseline-protocol-v1"

    protocol_sha256: Sha256

    development_freeze_receipt_sha256: Literal[
        "6deecc31195f3acefb0a6a47a650bf20e4f7606bac9131ff882126504dfbc1bc"
    ] = "6deecc31195f3acefb0a6a47a650bf20e4f7606bac9131ff882126504dfbc1bc"

    tuning_freeze_receipt_sha256: Literal[
        "ef0edfee6a71a7f294c22dcc17d9ecb657b200a100175a7ccd2c709a1e3f97f6"
    ] = "ef0edfee6a71a7f294c22dcc17d9ecb657b200a100175a7ccd2c709a1e3f97f6"

    held_out_freeze_receipt_sha256: Literal[
        "00428ea72206b7e80b65ff80ed85e100aa0e40de208e03fc5741398e1fb0465c"
    ] = "00428ea72206b7e80b65ff80ed85e100aa0e40de208e03fc5741398e1fb0465c"

    included_case_count: Literal[42] = 42
    included_cluster_count: Literal[21] = 21

    development_included: Literal[True] = True
    tuning_included: Literal[True] = True
    held_out_included: Literal[False] = False

    evidence_lane: Literal[
        "deterministic_replay_control"
    ] = "deterministic_replay_control"

    protocol_frozen: Literal[True] = True
    held_out_outcomes_exposed: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    chaos_authorized: Literal[False] = False
    intervention_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_freeze_boundary(self) -> Self:
        if self.held_out_included:
            raise ValueError("HELD_OUT cannot enter the B0 protocol freeze")

        if self.baseline_execution_authorized:
            raise ValueError(
                "protocol freeze cannot authorize baseline execution"
            )

        return self


def materialize_phase5_baseline_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5BaselineProtocolV1,
    str,
    Phase5BaselineProtocolFreezeReceipt,
    str,
]:
    """Materialize exact protocol bytes and an external freeze receipt."""

    protocol = build_phase5_baseline_protocol_v1()

    if protocol.baseline_execution_authorized:
        raise ValueError(
            "draft protocol unexpectedly authorizes baseline execution"
        )

    if protocol.held_out_outcomes_exposed:
        raise ValueError(
            "HELD_OUT outcomes became exposed before protocol freeze"
        )

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5BaselineProtocolFreezeReceipt(
        protocol_sha256=protocol_sha256,
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_RECEIPT_PATH,
        receipt,
    )

    return (
        protocol,
        protocol_sha256,
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
        protocol,
        protocol_sha256,
        receipt,
        receipt_sha256,
    ) = materialize_phase5_baseline_protocol_freeze(
        repo_root
    )

    print(
        "PHASE5_BASELINE_PROTOCOL_VERSION="
        f"{protocol.protocol_version}"
    )
    print(
        "PHASE5_BASELINE_PROTOCOL_SHA256="
        f"{protocol_sha256}"
    )
    print(
        "PHASE5_BASELINE_PROTOCOL_FROZEN="
        f"{str(receipt.protocol_frozen).lower()}"
    )
    print(
        "PHASE5_BASELINE_INCLUDED_CASE_COUNT="
        f"{receipt.included_case_count}"
    )
    print(
        "PHASE5_HELD_OUT_INCLUDED="
        f"{str(receipt.held_out_included).lower()}"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED="
        f"{str(receipt.held_out_outcomes_exposed).lower()}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(receipt.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_BASELINE_PROTOCOL_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
