from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.stratified_retrieval_candidate_protocol import (
    build_phase5_stratified_retrieval_candidate_protocol_v1,
)
from rag_reliability.evaluation.stratified_retrieval_characterization import (
    _load_controls,
)

ROOT = Path(__file__).resolve().parents[2]


def test_characterization_binds_frozen_protocol_bytes() -> None:
    protocol, freeze = _load_controls(ROOT)

    assert protocol.protocol_version == (
        "phase5-stratified-retrieval-candidate-protocol-v1"
    )
    assert freeze.protocol_frozen is True
    assert freeze.protocol_sha256 == (
        "1439cbbd96eaf3e3ee4de48634969745c90e9ce62ba31855409b667f9721f009"
    )


def test_characterization_boundary_remains_development_tuning_only() -> None:
    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()

    assert protocol.evidence_scope == (
        "spent_development_answerable_plus_tuning_answerable_offline_only"
    )
    assert protocol.post_reject_confirmation_inspected is False
    assert protocol.held_out_case_content_read is False
    assert protocol.provider_invoked is False
    assert protocol.baseline_execution_authorized is False


def test_characterization_gate_remains_single_non_swept_candidate() -> None:
    protocol = build_phase5_stratified_retrieval_candidate_protocol_v1()

    assert protocol.candidate.candidate_count == 1
    assert protocol.candidate.parameter_sweep_used is False
    assert protocol.candidate.tuning_parameter_optimization_used is False
    assert protocol.promotion_gate.deterministic_repeat_count == 3
    assert protocol.promotion_gate.provider_calls_allowed == 0
