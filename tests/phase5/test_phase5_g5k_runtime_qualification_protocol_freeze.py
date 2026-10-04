from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.runtime_qualification_protocol_freeze import (
    materialize_phase5_g5k_runtime_qualification_protocol_freeze,
)

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_g5k_runtime_qualification_protocol_v1.json"
)
FREEZE_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_g5k_runtime_qualification_protocol_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_g5k_freeze_binds_exact_bytes() -> None:
    _protocol, protocol_sha, receipt, receipt_sha = (
        materialize_phase5_g5k_runtime_qualification_protocol_freeze(ROOT)
    )

    assert protocol_sha == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha
    assert receipt_sha == _sha256(FREEZE_PATH)


def test_g5k_freeze_is_deterministic_and_non_authorizing() -> None:
    first = materialize_phase5_g5k_runtime_qualification_protocol_freeze(ROOT)
    second = materialize_phase5_g5k_runtime_qualification_protocol_freeze(ROOT)

    assert first[1] == second[1]
    assert first[3] == second[3]

    receipt = first[2]

    assert receipt.protocol_frozen is True
    assert receipt.implementation_started is False
    assert receipt.qualification_executed is False

    assert receipt.protected_confirmation_authorized is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False
    assert receipt.held_out_outcomes_exposed is False
