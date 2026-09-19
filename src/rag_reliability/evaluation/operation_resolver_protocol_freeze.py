"""Freeze the Phase 5 operation-resolver protocol before implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.operation_resolver_protocol import (
    Phase5OperationResolverProtocolV1,
    build_phase5_operation_resolver_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_protocol_v1.json"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_protocol_freeze_v1.json"
)


class Phase5OperationResolverProtocolFreezeReceipt(ContractModel):
    """Exact-byte custody receipt for the resolver protocol."""

    receipt_version: Literal[
        "phase5-operation-resolver-protocol-freeze-v1"
    ] = "phase5-operation-resolver-protocol-freeze-v1"

    protocol_version: Literal[
        "phase5-operation-resolver-protocol-v1"
    ] = "phase5-operation-resolver-protocol-v1"

    protocol_sha256: Sha256

    chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

    rrf_incumbent_artifact_sha256: Literal[
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    ] = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"

    fixture_count: Literal[10] = 10
    protocol_frozen: Literal[True] = True

    resolver_implementation_present_in_protocol: Literal[False] = False
    retrieval_ranking_changed: Literal[False] = False
    provider_invoked: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_freeze_boundary(self) -> Self:
        if self.resolver_implementation_present_in_protocol:
            raise ValueError(
                "resolver protocol freeze cannot contain implementation"
            )

        if self.retrieval_ranking_changed:
            raise ValueError(
                "resolver protocol freeze cannot mutate retrieval ranking"
            )

        return self


def materialize_phase5_operation_resolver_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5OperationResolverProtocolV1,
    str,
    Phase5OperationResolverProtocolFreezeReceipt,
    str,
]:
    """Materialize exact resolver-protocol bytes and freeze receipt."""

    protocol = build_phase5_operation_resolver_protocol_v1()

    if protocol.provider_calls_allowed:
        raise ValueError(
            "resolver protocol unexpectedly permits provider calls"
        )

    if protocol.held_out_outcomes_exposed:
        raise ValueError(
            "HELD_OUT outcomes became exposed before resolver implementation"
        )

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5OperationResolverProtocolFreezeReceipt(
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
    ) = materialize_phase5_operation_resolver_protocol_freeze(
        repo_root
    )

    print(
        "PHASE5_OPERATION_RESOLVER_PROTOCOL_VERSION="
        f"{protocol.protocol_version}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_PROTOCOL_SHA256="
        f"{protocol_sha256}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_PROTOCOL_FROZEN="
        f"{str(receipt.protocol_frozen).lower()}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_FIXTURE_COUNT="
        f"{receipt.fixture_count}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_PROVIDER_INVOKED="
        f"{str(receipt.provider_invoked).lower()}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_HELD_OUT_EXPOSED="
        f"{str(receipt.held_out_outcomes_exposed).lower()}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_PROTOCOL_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
