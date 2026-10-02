from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.stratified_retrieval_candidate_protocol_freeze import (
    materialize_phase5_stratified_retrieval_candidate_protocol_freeze,
)

ROOT = Path(__file__).resolve().parents[2]

PROTOCOL_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_stratified_retrieval_candidate_protocol_v1.json"
)
FREEZE_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_stratified_retrieval_candidate_protocol_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stratified_protocol_freeze_binds_exact_bytes() -> None:
    (
        _protocol,
        protocol_sha256,
        receipt,
        receipt_sha256,
    ) = materialize_phase5_stratified_retrieval_candidate_protocol_freeze(ROOT)

    assert protocol_sha256 == _sha256(PROTOCOL_PATH)
    assert receipt.protocol_sha256 == protocol_sha256
    assert receipt_sha256 == _sha256(FREEZE_PATH)


def test_stratified_protocol_freeze_is_deterministic() -> None:
    first = materialize_phase5_stratified_retrieval_candidate_protocol_freeze(ROOT)
    second = materialize_phase5_stratified_retrieval_candidate_protocol_freeze(ROOT)

    assert first[1] == second[1]
    assert first[3] == second[3]


def test_stratified_freeze_preserves_nonclaims() -> None:
    _protocol, _protocol_sha, receipt, _receipt_sha = (
        materialize_phase5_stratified_retrieval_candidate_protocol_freeze(ROOT)
    )

    assert receipt.candidate_count == 1
    assert receipt.candidate_implemented is False
    assert receipt.candidate_executed is False
    assert receipt.runtime_retriever_changed is False

    assert receipt.post_reject_confirmation_inspected is False
    assert receipt.post_reject_confirmation_executed is False
    assert receipt.held_out_case_content_read is False
    assert receipt.held_out_outcomes_exposed is False

    assert receipt.provider_invoked is False
    assert receipt.retrieval_configuration_selected is False
    assert receipt.semantic_runtime_configuration_frozen is False

    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False
    assert receipt.release_eligible is False
    assert receipt.baseline_readiness_review_required_after_result is True
