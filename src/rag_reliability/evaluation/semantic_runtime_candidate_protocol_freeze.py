"""Freeze the Phase 5 semantic-runtime candidate protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.semantic_runtime_candidate_protocol import (
    Phase5SemanticRuntimeCandidateProtocolV1,
    build_phase5_semantic_runtime_candidate_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_candidate_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_candidate_protocol_freeze_v1.json"
)


class Phase5SemanticRuntimeCandidateProtocolFreezeReceipt(ContractModel):
    receipt_version: Literal["phase5-semantic-runtime-candidate-protocol-freeze-v1"] = (
        "phase5-semantic-runtime-candidate-protocol-freeze-v1"
    )

    protocol_version: Literal["phase5-semantic-runtime-candidate-protocol-v1"] = (
        "phase5-semantic-runtime-candidate-protocol-v1"
    )

    protocol_sha256: Sha256
    candidate_count: Literal[1] = 1
    protocol_frozen: Literal[True] = True

    development_confirmation_executed: Literal[False] = False
    live_capacity_qualification_satisfied: Literal[False] = False
    runtime_retriever_integrated: Literal[False] = False
    runtime_configuration_materialized: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    provider_invoked: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.candidate_count != 1:
            raise ValueError("freeze receipt must bind one candidate")
        if self.development_confirmation_executed:
            raise ValueError("freeze precedes DEVELOPMENT confirmation")
        if self.live_capacity_qualification_satisfied:
            raise ValueError("freeze cannot claim live capacity")
        if self.semantic_runtime_configuration_frozen:
            raise ValueError("freeze cannot freeze runtime configuration")
        return self


def materialize_phase5_semantic_runtime_candidate_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5SemanticRuntimeCandidateProtocolV1,
    str,
    Phase5SemanticRuntimeCandidateProtocolFreezeReceipt,
    str,
]:
    protocol = build_phase5_semantic_runtime_candidate_protocol_v1()
    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )
    receipt = Phase5SemanticRuntimeCandidateProtocolFreezeReceipt(
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
        receipt,
        receipt_sha256,
    ) = materialize_phase5_semantic_runtime_candidate_protocol_freeze(repo_root)

    print(f"PHASE5_SEMANTIC_RUNTIME_CANDIDATE_PROTOCOL_SHA256={protocol_sha256}")
    print(
        "PHASE5_SEMANTIC_RUNTIME_CANDIDATE_CONTEXT="
        f"top_k:{protocol.candidate.retrieval_top_k},"
        f"items:{protocol.candidate.context_max_evidence_items},"
        f"chars:{protocol.candidate.context_max_budget}"
    )
    print(
        "PHASE5_LIVE_CAPACITY_PROBE_AUTHORIZED_NOW="
        f"{str(protocol.provider_capacity.live_capacity_probe_authorized_now).lower()}"
    )
    print(f"PHASE5_SEMANTIC_RUNTIME_CANDIDATE_FREEZE_SHA256={receipt_sha256}")


if __name__ == "__main__":
    main()
