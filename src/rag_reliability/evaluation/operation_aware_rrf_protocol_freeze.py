"""Freeze the single Phase 5 operation-aware RRF protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.operation_aware_rrf_protocol import (
    Phase5OperationAwareRrfProtocolV1,
    build_phase5_operation_aware_rrf_protocol_v1,
)

_PROTOCOL_PATH = Path("artifacts") / "development" / "phase5_operation_aware_rrf_protocol_v1.json"
_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_operation_aware_rrf_protocol_freeze_v1.json"
)


class Phase5OperationAwareRrfProtocolFreezeReceipt(ContractModel):
    """Exact-byte custody receipt for the Slice 2 protocol."""

    receipt_version: Literal["phase5-operation-aware-rrf-protocol-freeze-v1"] = (
        "phase5-operation-aware-rrf-protocol-freeze-v1"
    )
    protocol_version: Literal["phase5-operation-aware-rrf-protocol-v1"] = (
        "phase5-operation-aware-rrf-protocol-v1"
    )
    protocol_sha256: Sha256
    candidate_count: Literal[1] = 1
    protocol_frozen: Literal[True] = True
    provider_invoked: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False
    semantic_runtime_capacity_gate_satisfied: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.candidate_count != 1:
            raise ValueError("Slice 2 freeze must bind exactly one candidate")

        if self.semantic_runtime_capacity_gate_satisfied:
            raise ValueError("Slice 2 protocol freeze cannot claim semantic runtime capacity")

        if self.semantic_runtime_configuration_frozen:
            raise ValueError("Slice 2 protocol freeze cannot freeze semantic runtime configuration")

        return self


def materialize_phase5_operation_aware_rrf_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5OperationAwareRrfProtocolV1,
    str,
    Phase5OperationAwareRrfProtocolFreezeReceipt,
    str,
]:
    """Materialize exact Slice 2 protocol bytes and freeze receipt."""

    protocol = build_phase5_operation_aware_rrf_protocol_v1()
    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )
    receipt = Phase5OperationAwareRrfProtocolFreezeReceipt(
        protocol_sha256=protocol_sha256,
    )
    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )
    return (
        protocol,
        protocol_sha256,
        receipt,
        receipt_sha256,
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    (
        protocol,
        protocol_sha256,
        receipt,
        receipt_sha256,
    ) = materialize_phase5_operation_aware_rrf_protocol_freeze(repo_root)

    print(f"PHASE5_OPERATION_AWARE_RRF_PROTOCOL_VERSION={protocol.protocol_version}")
    print(f"PHASE5_OPERATION_AWARE_RRF_PROTOCOL_SHA256={protocol_sha256}")
    print(f"PHASE5_OPERATION_AWARE_RRF_PROTOCOL_FROZEN={str(receipt.protocol_frozen).lower()}")
    print(f"PHASE5_OPERATION_AWARE_RRF_CANDIDATE_COUNT={receipt.candidate_count}")
    print(
        "PHASE5_SEMANTIC_RUNTIME_CAPACITY_GATE_SATISFIED="
        f"{str(receipt.semantic_runtime_capacity_gate_satisfied).lower()}"
    )
    print(f"PHASE5_OPERATION_AWARE_RRF_FREEZE_RECEIPT_SHA256={receipt_sha256}")


if __name__ == "__main__":
    main()
