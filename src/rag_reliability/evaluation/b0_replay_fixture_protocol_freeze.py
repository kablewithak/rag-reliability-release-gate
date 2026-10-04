"""Freeze the G5M B0 replay-fixture authoring protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.b0_replay_fixture_protocol import (
    Phase5B0ReplayFixtureProtocolV1,
    build_phase5_b0_replay_fixture_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_b0_replay_fixture_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_b0_replay_fixture_protocol_freeze_v1.json"
)


class Phase5B0ReplayFixtureProtocolFreezeV1(ContractModel):
    receipt_version: Literal[
        "phase5-b0-replay-fixture-protocol-freeze-v1"
    ] = "phase5-b0-replay-fixture-protocol-freeze-v1"

    protocol_version: Literal[
        "phase5-b0-replay-fixture-protocol-v1"
    ] = "phase5-b0-replay-fixture-protocol-v1"

    protocol_sha256: Sha256
    protocol_frozen: Literal[True] = True

    fixture_authoring_executed: Literal[False] = False
    replay_fixture_materialized: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.fixture_authoring_executed or self.replay_fixture_materialized:
            raise ValueError("fixture protocol freeze must precede authoring")

        if (
            self.baseline_execution_authorized
            or self.b0_executed
            or self.post_reject_confirmation_inspected
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("fixture protocol freeze overclaims downstream state")

        return self


def materialize_phase5_b0_replay_fixture_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5B0ReplayFixtureProtocolV1,
    str,
    Phase5B0ReplayFixtureProtocolFreezeV1,
    str,
]:
    protocol = build_phase5_b0_replay_fixture_protocol_v1()

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5B0ReplayFixtureProtocolFreezeV1(
        protocol_sha256=protocol_sha256,
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )

    return protocol, protocol_sha256, receipt, receipt_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    protocol, protocol_sha256, _receipt, receipt_sha256 = (
        materialize_phase5_b0_replay_fixture_protocol_freeze(repo_root)
    )

    print(f"PHASE5_B0_REPLAY_FIXTURE_PROTOCOL_SHA256={protocol_sha256}")
    print(f"PHASE5_B0_REPLAY_FIXTURE_POLICY={protocol.fixture_generation_policy}")
    print(f"PHASE5_B0_REPLAY_AUTHORIZED_CASES={protocol.authorized_case_count}")
    print(
        "PHASE5_B0_REPLAY_EVALUATOR_FIELDS_USED="
        f"{str(protocol.evaluator_fields_used_for_fixture_authoring).lower()}"
    )
    print(
        "PHASE5_B0_REPLAY_NEW_LIVE_CALLS_AUTHORIZED="
        f"{protocol.new_live_provider_calls_authorized}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(protocol.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_B0_REPLAY_FIXTURE_PROTOCOL_FREEZE_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
