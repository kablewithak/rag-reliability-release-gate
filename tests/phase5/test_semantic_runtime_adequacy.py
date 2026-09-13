from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.semantic_runtime_adequacy import (
    materialize_phase5_semantic_runtime_adequacy,
)

ROOT = Path(__file__).resolve().parents[2]

OUTPUT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_semantic_runtime_adequacy_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_adequacy_materialization_is_deterministic() -> None:
    first = (
        materialize_phase5_semantic_runtime_adequacy(
            ROOT
        )
    )
    second = (
        materialize_phase5_semantic_runtime_adequacy(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[1] == _sha256(
        OUTPUT_PATH
    )


def test_adequacy_reconciles_non_held_out_case_counts() -> None:
    receipt, _receipt_sha256 = (
        materialize_phase5_semantic_runtime_adequacy(
            ROOT
        )
    )

    assert receipt.included_case_count == 42
    assert receipt.development_case_count == 24
    assert receipt.tuning_case_count == 18

    assert (
        receipt.answerable_case_count
        + receipt.refusal_case_count
        == 42
    )

    assert receipt.held_out_outcomes_exposed is False


def test_adequacy_derives_positive_structural_floors() -> None:
    receipt, _receipt_sha256 = (
        materialize_phase5_semantic_runtime_adequacy(
            ROOT
        )
    )

    assert (
        receipt.minimum_top_k_structural_floor
        >= 1
    )
    assert (
        receipt.minimum_max_evidence_items_structural_floor
        == receipt.minimum_top_k_structural_floor
    )
    assert (
        receipt.minimum_context_budget_characters_structural_floor
        >= 1
    )
    assert receipt.max_required_fact_count >= 1


def test_adequacy_verifies_required_evidence_custody() -> None:
    receipt, _receipt_sha256 = (
        materialize_phase5_semantic_runtime_adequacy(
            ROOT
        )
    )

    assert (
        receipt.all_required_evidence_present_in_frozen_corpus
        is True
    )
    assert (
        receipt.all_required_evidence_content_hashes_verified
        is True
    )


def test_adequacy_does_not_overclaim_runtime_validity() -> None:
    receipt, _receipt_sha256 = (
        materialize_phase5_semantic_runtime_adequacy(
            ROOT
        )
    )

    assert receipt.retrieval_ranking_adequacy_measured is False
    assert receipt.semantic_generation_adequacy_measured is False
    assert receipt.phase2b_runtime_config_reuse_authorized is False
    assert receipt.semantic_runtime_configuration_selected is False
    assert receipt.semantic_runtime_configuration_frozen is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.release_eligible is False
