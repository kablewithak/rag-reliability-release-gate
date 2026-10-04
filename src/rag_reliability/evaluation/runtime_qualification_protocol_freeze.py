"""Freeze the G5K runtime/control-lane qualification protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.runtime_qualification_protocol import (
    Phase5G5kRuntimeQualificationProtocolV1,
    build_phase5_g5k_runtime_qualification_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_g5k_runtime_qualification_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_g5k_runtime_qualification_protocol_freeze_v1.json"
)


class Phase5G5kRuntimeQualificationProtocolFreezeV1(ContractModel):
    receipt_version: Literal[
        "phase5-g5k-runtime-qualification-protocol-freeze-v1"
    ] = "phase5-g5k-runtime-qualification-protocol-freeze-v1"

    protocol_version: Literal[
        "phase5-g5k-runtime-qualification-protocol-v1"
    ] = "phase5-g5k-runtime-qualification-protocol-v1"

    protocol_sha256: Sha256
    protocol_frozen: Literal[True] = True

    implementation_started: Literal[False] = False
    qualification_executed: Literal[False] = False

    protected_confirmation_authorized: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.implementation_started or self.qualification_executed:
            raise ValueError("G5K freeze must precede implementation/result")

        if (
            self.protected_confirmation_authorized
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("G5K freeze overclaims downstream state")

        return self


def materialize_phase5_g5k_runtime_qualification_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5G5kRuntimeQualificationProtocolV1,
    str,
    Phase5G5kRuntimeQualificationProtocolFreezeV1,
    str,
]:
    protocol = build_phase5_g5k_runtime_qualification_protocol_v1()

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5G5kRuntimeQualificationProtocolFreezeV1(
        protocol_sha256=protocol_sha256,
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )

    return protocol, protocol_sha256, receipt, receipt_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    (
        protocol,
        protocol_sha256,
        _receipt,
        receipt_sha256,
    ) = materialize_phase5_g5k_runtime_qualification_protocol_freeze(
        repo_root
    )

    print(
        "PHASE5_G5K_RUNTIME_QUALIFICATION_PROTOCOL_SHA256="
        f"{protocol_sha256}"
    )
    print(
        "PHASE5_G5K_SELECTED_RETRIEVAL="
        f"{protocol.selected_retrieval_id}"
    )
    print(
        "PHASE5_G5K_LANE_A_PROVIDER_MODE="
        f"{protocol.lane_a_provider_mode}"
    )
    print(
        "PHASE5_G5K_LANE_A_CONTEXT_SENSITIVE="
        f"{str(protocol.lane_a_generation_is_context_sensitive).lower()}"
    )
    print(
        "PHASE5_G5K_LANE_B_LIVE_QUALIFIED="
        f"{str(protocol.lane_b_live_qualification_satisfied).lower()}"
    )
    print(
        "PHASE5_G5K_NEW_LIVE_CALLS_AUTHORIZED="
        f"{protocol.lane_b_new_live_calls_authorized}"
    )
    print(
        "PHASE5_G5K_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(protocol.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_G5K_RUNTIME_QUALIFICATION_FREEZE_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
