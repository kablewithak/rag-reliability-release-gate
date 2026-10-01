"""Freeze the Phase 5 evidence-lane diagnostic protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.evidence_lane_diagnostic_protocol import (
    Phase5EvidenceLaneDiagnosticProtocolV1,
    build_phase5_evidence_lane_diagnostic_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_evidence_lane_diagnostic_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_evidence_lane_diagnostic_protocol_freeze_v1.json"
)


class Phase5EvidenceLaneDiagnosticProtocolFreezeV1(ContractModel):
    receipt_version: Literal[
        "phase5-evidence-lane-diagnostic-protocol-freeze-v1"
    ] = "phase5-evidence-lane-diagnostic-protocol-freeze-v1"

    protocol_sha256: Sha256
    protocol_frozen: Literal[True] = True

    diagnostic_implemented: Literal[False] = False
    diagnostic_executed: Literal[False] = False

    runtime_retriever_changed: Literal[False] = False
    corpus_mutated: Literal[False] = False
    chunking_policy_changed: Literal[False] = False

    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False
    composition_authorized: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False


def materialize_phase5_evidence_lane_diagnostic_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5EvidenceLaneDiagnosticProtocolV1,
    str,
    Phase5EvidenceLaneDiagnosticProtocolFreezeV1,
    str,
]:
    protocol = build_phase5_evidence_lane_diagnostic_protocol_v1()

    protocol_sha = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5EvidenceLaneDiagnosticProtocolFreezeV1(
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
        materialize_phase5_evidence_lane_diagnostic_protocol_freeze(
            repo_root
        )
    )

    print(f"PHASE5_EVIDENCE_LANE_PROTOCOL_SHA256={protocol_sha}")
    print(f"PHASE5_EVIDENCE_LANE_PROTOCOL_FREEZE_SHA256={freeze_sha}")
    print(f"PHASE5_EVIDENCE_LANE_DIAGNOSTIC_ID={protocol.diagnostic_id}")
    print("PHASE5_EVIDENCE_LANE_DIAGNOSTIC_IMPLEMENTED=false")
    print("PHASE5_EVIDENCE_LANE_DIAGNOSTIC_EXECUTED=false")
    print("PHASE5_RUNTIME_RETRIEVER_CHANGED=false")
    print("PHASE5_CORPUS_MUTATED=false")
    print("PHASE5_CANDIDATE_IMPLEMENTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")


if __name__ == "__main__":
    main()
