from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.baseline_protocol_freeze import (
    materialize_phase5_baseline_protocol_freeze,
)

ROOT = Path(__file__).resolve().parents[2]

PROTOCOL_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_baseline_protocol_v1.json"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_baseline_protocol_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_materialization_binds_exact_protocol_bytes() -> None:
    (
        protocol,
        protocol_sha256,
        receipt,
        receipt_sha256,
    ) = materialize_phase5_baseline_protocol_freeze(
        ROOT
    )

    assert protocol_sha256 == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha256
    assert receipt_sha256 == _sha256(RECEIPT_PATH)

    assert protocol.baseline_execution_authorized is False
    assert receipt.protocol_frozen is True
    assert receipt.baseline_execution_authorized is False


def test_freeze_preserves_role_boundary() -> None:
    (
        _protocol,
        _protocol_sha256,
        receipt,
        _receipt_sha256,
    ) = materialize_phase5_baseline_protocol_freeze(
        ROOT
    )

    assert receipt.included_case_count == 42
    assert receipt.included_cluster_count == 21

    assert receipt.development_included is True
    assert receipt.tuning_included is True
    assert receipt.held_out_included is False
    assert receipt.held_out_outcomes_exposed is False


def test_freeze_preserves_replay_evidence_boundary() -> None:
    (
        protocol,
        _protocol_sha256,
        receipt,
        _receipt_sha256,
    ) = materialize_phase5_baseline_protocol_freeze(
        ROOT
    )

    assert receipt.evidence_lane == "deterministic_replay_control"

    assert (
        protocol.execution.generation_is_context_sensitive
        is False
    )

    assert (
        "context_sensitive_generation_improvement"
        in protocol.execution.prohibited_claim_ids
    )


def test_materialization_is_deterministic() -> None:
    first = materialize_phase5_baseline_protocol_freeze(
        ROOT
    )
    second = materialize_phase5_baseline_protocol_freeze(
        ROOT
    )

    assert first[1] == second[1]
    assert first[3] == second[3]
