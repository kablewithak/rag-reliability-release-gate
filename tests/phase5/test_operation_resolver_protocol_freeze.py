from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.operation_resolver_protocol_freeze import (
    materialize_phase5_operation_resolver_protocol_freeze,
)

ROOT = Path(__file__).resolve().parents[2]

PROTOCOL_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_operation_resolver_protocol_v1.json"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_operation_resolver_protocol_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_materialization_binds_exact_resolver_protocol_bytes() -> None:
    (
        protocol,
        protocol_sha256,
        receipt,
        receipt_sha256,
    ) = materialize_phase5_operation_resolver_protocol_freeze(
        ROOT
    )

    assert protocol_sha256 == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha256
    assert receipt_sha256 == _sha256(RECEIPT_PATH)

    assert receipt.protocol_frozen is True
    assert receipt.resolver_implementation_present_in_protocol is False
    assert receipt.retrieval_ranking_changed is False


def test_freeze_preserves_safety_boundary() -> None:
    (
        protocol,
        _protocol_sha256,
        receipt,
        _receipt_sha256,
    ) = materialize_phase5_operation_resolver_protocol_freeze(
        ROOT
    )

    assert protocol.provider_calls_allowed is False
    assert protocol.held_out_outcomes_exposed is False
    assert receipt.provider_invoked is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.release_eligible is False


def test_resolver_protocol_materialization_is_deterministic() -> None:
    first = materialize_phase5_operation_resolver_protocol_freeze(
        ROOT
    )
    second = materialize_phase5_operation_resolver_protocol_freeze(
        ROOT
    )

    assert first[1] == second[1]
    assert first[3] == second[3]
