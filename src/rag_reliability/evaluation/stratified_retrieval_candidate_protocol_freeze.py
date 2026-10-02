"""Freeze the single Phase 5 stratified retrieval candidate protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.stratified_retrieval_candidate_protocol import (
    Phase5StratifiedRetrievalCandidateProtocolV1,
    build_phase5_stratified_retrieval_candidate_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_stratified_retrieval_candidate_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_stratified_retrieval_candidate_protocol_freeze_v1.json"
)


class Phase5StratifiedRetrievalCandidateProtocolFreezeV1(ContractModel):
    """Exact-byte custody receipt for the G5G protocol."""

    receipt_version: Literal[
        "phase5-stratified-retrieval-candidate-protocol-freeze-v1"
    ] = "phase5-stratified-retrieval-candidate-protocol-freeze-v1"

    protocol_version: Literal[
        "phase5-stratified-retrieval-candidate-protocol-v1"
    ] = "phase5-stratified-retrieval-candidate-protocol-v1"

    protocol_sha256: Sha256
    candidate_count: Literal[1] = 1
    protocol_frozen: Literal[True] = True

    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    baseline_readiness_review_required_after_result: Literal[True] = True

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.candidate_count != 1:
            raise ValueError("G5G freeze must bind exactly one candidate")

        if self.candidate_implemented or self.candidate_executed:
            raise ValueError("G5G protocol freeze cannot claim candidate execution")

        if (
            self.post_reject_confirmation_inspected
            or self.post_reject_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
        ):
            raise ValueError("G5G protocol freeze cannot expose protected evidence")

        if (
            self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("G5G protocol freeze overclaims downstream state")

        return self


def materialize_phase5_stratified_retrieval_candidate_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5StratifiedRetrievalCandidateProtocolV1,
    str,
    Phase5StratifiedRetrievalCandidateProtocolFreezeV1,
    str,
]:
    """Materialize exact protocol bytes and their freeze receipt."""

    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5StratifiedRetrievalCandidateProtocolFreezeV1(
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
    ) = materialize_phase5_stratified_retrieval_candidate_protocol_freeze(
        repo_root
    )

    print(
        "PHASE5_STRATIFIED_RETRIEVAL_PROTOCOL_VERSION="
        f"{protocol.protocol_version}"
    )
    print(
        "PHASE5_STRATIFIED_RETRIEVAL_PROTOCOL_SHA256="
        f"{protocol_sha256}"
    )
    print(
        "PHASE5_STRATIFIED_RETRIEVAL_PROTOCOL_FROZEN="
        f"{str(receipt.protocol_frozen).lower()}"
    )
    print(
        "PHASE5_STRATIFIED_RETRIEVAL_CANDIDATE_COUNT="
        f"{receipt.candidate_count}"
    )
    print(
        "PHASE5_STRATIFIED_RETRIEVAL_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )
    print("PHASE5_STRATIFIED_RETRIEVAL_CANDIDATE_IMPLEMENTED=false")
    print("PHASE5_STRATIFIED_RETRIEVAL_CANDIDATE_EXECUTED=false")
    print("PHASE5_RUNTIME_RETRIEVER_CHANGED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_RETRIEVAL_CONFIGURATION_SELECTED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")


if __name__ == "__main__":
    main()
