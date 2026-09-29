"""Freeze the Phase 5 A2 successor resolver protocol before implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.a2_successor_resolver_protocol import (
    Phase5A2SuccessorResolverProtocolV1,
    build_phase5_a2_successor_resolver_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_a2_successor_resolver_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_a2_successor_resolver_protocol_freeze_v1.json"
)


class Phase5A2SuccessorResolverProtocolFreezeV1(ContractModel):
    receipt_version: Literal["phase5-a2-successor-resolver-protocol-freeze-v1"] = (
        "phase5-a2-successor-resolver-protocol-freeze-v1"
    )

    protocol_sha256: Sha256
    protocol_frozen: Literal[True] = True

    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False
    b0_executed: Literal[False] = False
    chaos_executed: Literal[False] = False
    load_executed: Literal[False] = False


def materialize_phase5_a2_successor_resolver_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5A2SuccessorResolverProtocolV1,
    str,
    Phase5A2SuccessorResolverProtocolFreezeV1,
    str,
]:
    protocol = build_phase5_a2_successor_resolver_protocol_v1()
    protocol_sha = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5A2SuccessorResolverProtocolFreezeV1(
        protocol_sha256=protocol_sha,
    )
    freeze_sha = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )

    return protocol, protocol_sha, receipt, freeze_sha


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    protocol, protocol_sha, _receipt, freeze_sha = (
        materialize_phase5_a2_successor_resolver_protocol_freeze(repo_root)
    )

    print(f"PHASE5_A2_PROTOCOL_SHA256={protocol_sha}")
    print(f"PHASE5_A2_PROTOCOL_FREEZE_SHA256={freeze_sha}")
    print(f"PHASE5_A2_EXPERIMENT_ID={protocol.experiment_id}")
    print("PHASE5_A2_CANDIDATE_IMPLEMENTED=false")
    print("PHASE5_A2_CANDIDATE_EXECUTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")


if __name__ == "__main__":
    main()
