from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.operation_resolver_protocol_freeze_v2 import (
    materialize_phase5_operation_resolver_protocol_freeze_v2,
)

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_operation_resolver_protocol_v2.json"
)
RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_operation_resolver_protocol_freeze_v2.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v2_materialization_binds_exact_corrected_protocol_bytes() -> None:
    protocol, protocol_sha256, receipt, receipt_sha256 = (
        materialize_phase5_operation_resolver_protocol_freeze_v2(ROOT)
    )

    assert protocol_sha256 == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha256
    assert receipt_sha256 == _sha256(RECEIPT_PATH)
    assert receipt.protocol_frozen is True
    assert receipt.correction_applied is True
    assert receipt.runtime_catalog_operation_count == 20


def test_v2_freeze_preserves_execution_boundary() -> None:
    protocol, _protocol_sha256, receipt, _receipt_sha256 = (
        materialize_phase5_operation_resolver_protocol_freeze_v2(ROOT)
    )

    assert protocol.provider_calls_allowed is False
    assert protocol.held_out_outcomes_exposed is False
    assert receipt.provider_invoked is False
    assert receipt.retrieval_ranking_changed is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.release_eligible is False


def test_v2_materialization_is_deterministic() -> None:
    first = materialize_phase5_operation_resolver_protocol_freeze_v2(ROOT)
    second = materialize_phase5_operation_resolver_protocol_freeze_v2(ROOT)

    assert first[1] == second[1]
    assert first[3] == second[3]
