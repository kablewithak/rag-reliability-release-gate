"""Freeze the corrected Phase 5 operation-resolver protocol v2."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.operation_resolver_protocol_v2 import (
    Phase5OperationResolverProtocolV2,
    build_phase5_operation_resolver_protocol_v2,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_protocol_v2.json"
)
_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_protocol_freeze_v2.json"
)


class Phase5OperationResolverProtocolFreezeReceiptV2(ContractModel):
    """Exact-byte custody receipt for the corrected resolver protocol."""

    receipt_version: Literal[
        "phase5-operation-resolver-protocol-freeze-v2"
    ] = "phase5-operation-resolver-protocol-freeze-v2"

    protocol_version: Literal[
        "phase5-operation-resolver-protocol-v2"
    ] = "phase5-operation-resolver-protocol-v2"

    protocol_sha256: Sha256

    supersedes_protocol_sha256: Literal[
        "373fc8abb9a6bc20c04b788ce1a67c26b468cd2d7f662ddd27d938d1084cf61e"
    ] = "373fc8abb9a6bc20c04b788ce1a67c26b468cd2d7f662ddd27d938d1084cf61e"

    chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

    rrf_incumbent_artifact_sha256: Literal[
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    ] = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"

    runtime_catalog_operation_count: Literal[20] = 20
    fixture_count: Literal[10] = 10
    protocol_frozen: Literal[True] = True
    correction_applied: Literal[True] = True

    resolver_implementation_present_in_protocol: Literal[False] = False
    retrieval_ranking_changed: Literal[False] = False
    provider_invoked: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_freeze_boundary(self) -> Self:
        if self.resolver_implementation_present_in_protocol:
            raise ValueError("resolver v2 freeze cannot contain implementation")
        if self.retrieval_ranking_changed:
            raise ValueError("resolver v2 freeze cannot mutate retrieval ranking")
        return self


def materialize_phase5_operation_resolver_protocol_freeze_v2(
    repo_root: Path,
) -> tuple[
    Phase5OperationResolverProtocolV2,
    str,
    Phase5OperationResolverProtocolFreezeReceiptV2,
    str,
]:
    """Materialize exact corrected protocol bytes and a freeze receipt."""

    protocol = build_phase5_operation_resolver_protocol_v2()

    if protocol.provider_calls_allowed:
        raise ValueError("resolver v2 unexpectedly permits provider calls")
    if protocol.held_out_outcomes_exposed:
        raise ValueError("HELD_OUT outcomes became exposed in resolver v2")

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )
    receipt = Phase5OperationResolverProtocolFreezeReceiptV2(
        protocol_sha256=protocol_sha256,
    )
    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_RECEIPT_PATH,
        receipt,
    )

    return protocol, protocol_sha256, receipt, receipt_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    protocol, protocol_sha256, receipt, receipt_sha256 = (
        materialize_phase5_operation_resolver_protocol_freeze_v2(repo_root)
    )

    print(f"PHASE5_OPERATION_RESOLVER_PROTOCOL_VERSION={protocol.protocol_version}")
    print(f"PHASE5_OPERATION_RESOLVER_PROTOCOL_SHA256={protocol_sha256}")
    print(
        "PHASE5_OPERATION_RESOLVER_PROTOCOL_FROZEN="
        f"{str(receipt.protocol_frozen).lower()}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_RUNTIME_CATALOG_COUNT="
        f"{receipt.runtime_catalog_operation_count}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_PROTOCOL_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
