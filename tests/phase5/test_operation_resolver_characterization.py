from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.operation_resolver_characterization import (
    materialize_phase5_operation_resolver_characterization,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_operation_resolver_characterization_v2.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_characterization_binds_frozen_protocol() -> None:
    report, _digest = materialize_phase5_operation_resolver_characterization(ROOT)

    assert report.protocol_sha256 == (
        "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
    )
    assert report.protocol_freeze_receipt_sha256 == (
        "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"
    )


def test_characterization_matches_frozen_fixture_contract() -> None:
    report, _digest = materialize_phase5_operation_resolver_characterization(ROOT)

    assert report.fixture_count == 10
    assert report.catalog_operation_count == 20
    assert report.expectation_mismatch_count == 0
    assert report.false_confident_resolution_count == 0
    assert report.nondeterministic_fixture_count == 0
    assert report.resolved_fixture_count >= 5
    assert report.acceptance_passed is True
    assert report.acceptance_failures == ()


def test_characterization_preserves_runtime_and_eval_boundaries() -> None:
    report, _digest = materialize_phase5_operation_resolver_characterization(ROOT)

    assert report.evaluator_fields_passed_to_resolver is False
    assert report.provider_invoked is False
    assert report.development_gold_used is False
    assert report.held_out_outcomes_exposed is False
    assert report.runtime_retriever_changed is False
    assert report.retrieval_configuration_selected is False
    assert report.semantic_runtime_configuration_frozen is False
    assert report.baseline_execution_authorized is False
    assert report.b0_executed is False
    assert report.release_eligible is False


def test_characterization_materialization_is_deterministic() -> None:
    first = materialize_phase5_operation_resolver_characterization(ROOT)
    second = materialize_phase5_operation_resolver_characterization(ROOT)

    assert first[1] == second[1]
    assert first[1] == _sha256(REPORT_PATH)
