from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.post_reject_investigation_protocol_freeze import (
    materialize_phase5_post_reject_investigation_protocol_freeze,
)

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = (
    ROOT / "artifacts" / "development" / "phase5_post_reject_investigation_protocol_v1.json"
)
FREEZE_PATH = (
    ROOT / "artifacts" / "development" / "phase5_post_reject_investigation_protocol_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_post_reject_freeze_binds_exact_bytes() -> None:
    _protocol, protocol_sha, receipt, receipt_sha = (
        materialize_phase5_post_reject_investigation_protocol_freeze(ROOT)
    )

    assert protocol_sha == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha
    assert receipt_sha == _sha256(FREEZE_PATH)


def test_post_reject_freeze_is_deterministic() -> None:
    first = materialize_phase5_post_reject_investigation_protocol_freeze(ROOT)
    second = materialize_phase5_post_reject_investigation_protocol_freeze(ROOT)

    assert first[1] == second[1]
    assert first[3] == second[3]


def test_post_reject_freeze_preserves_nonclaims() -> None:
    _protocol, _protocol_sha, receipt, _receipt_sha = (
        materialize_phase5_post_reject_investigation_protocol_freeze(ROOT)
    )

    assert receipt.failure_specific_development_evidence_opened is False
    assert receipt.fresh_confirmation_materialized is False
    assert receipt.fresh_confirmation_frozen is False
    assert receipt.development_spent_for_future_confirmation is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.provider_invoked is False
    assert receipt.b0_executed is False
