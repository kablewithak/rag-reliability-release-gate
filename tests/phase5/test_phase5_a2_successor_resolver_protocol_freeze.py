from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.a2_successor_resolver_protocol_freeze import (
    materialize_phase5_a2_successor_resolver_protocol_freeze,
)

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = (
    ROOT / "artifacts" / "development" / "phase5_a2_successor_resolver_protocol_v1.json"
)
FREEZE_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_a2_successor_resolver_protocol_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_a2_protocol_freeze_binds_exact_bytes() -> None:
    _protocol, protocol_sha, receipt, freeze_sha = (
        materialize_phase5_a2_successor_resolver_protocol_freeze(ROOT)
    )

    assert protocol_sha == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha
    assert freeze_sha == _sha256(FREEZE_PATH)


def test_a2_protocol_freeze_preserves_nonexecution() -> None:
    _protocol, _protocol_sha, receipt, _freeze_sha = (
        materialize_phase5_a2_successor_resolver_protocol_freeze(ROOT)
    )

    assert receipt.candidate_implemented is False
    assert receipt.candidate_executed is False
    assert receipt.post_reject_confirmation_inspected is False
    assert receipt.post_reject_confirmation_executed is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.provider_invoked is False
    assert receipt.b0_executed is False
    assert receipt.chaos_executed is False
    assert receipt.load_executed is False
