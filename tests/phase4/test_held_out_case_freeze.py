import hashlib
from pathlib import Path

from rag_reliability.evaluation.held_out_case_freeze import (
    EXPECTED_HELD_OUT_CASES_JSON_SHA256,
    EXPECTED_HELD_OUT_CASES_MARKDOWN_SHA256,
    Phase4HeldOutCaseFreezeReceipt,
    materialize_phase4_held_out_case_freeze,
)
from rag_reliability.evaluation.held_out_cases import (
    Phase4HeldOutCaseSuite,
)

ROOT = Path(__file__).resolve().parents[2]

JSON_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_held_out_cases_v1.json"
)

MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_held_out_cases_v1.md"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_held_out_case_freeze_v1.json"
)


def _sha256(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def test_reviewed_held_out_bytes_are_exact(
) -> None:
    assert (
        _sha256(
            JSON_PATH.read_bytes()
        )
        == EXPECTED_HELD_OUT_CASES_JSON_SHA256
    )

    assert (
        _sha256(
            MARKDOWN_PATH.read_bytes()
        )
        == EXPECTED_HELD_OUT_CASES_MARKDOWN_SHA256
    )


def test_candidate_remains_unfrozen_internally(
) -> None:
    suite = (
        Phase4HeldOutCaseSuite
        .model_validate_json(
            JSON_PATH.read_bytes()
        )
    )

    assert (
        suite.held_out_case_authoring_complete
        is True
    )

    assert (
        suite.held_out_suite_frozen
        is False
    )

    assert (
        suite.held_out_outcomes_exposed
        is False
    )

    assert (
        suite.baseline_authorized
        is False
    )

    assert (
        suite.release_eligible
        is False
    )


def test_external_receipt_freezes_exact_suite(
) -> None:
    receipt = (
        Phase4HeldOutCaseFreezeReceipt
        .model_validate_json(
            RECEIPT_PATH.read_bytes()
        )
    )

    assert receipt.case_count == 18
    assert receipt.cluster_count == 9

    assert (
        receipt.current_single_source_count
        == 5
    )

    assert (
        receipt.current_multi_evidence_count
        == 4
    )

    assert (
        receipt.version_freshness_count
        == 4
    )

    assert (
        receipt.authority_scope_count
        == 2
    )

    assert (
        receipt.must_refuse_count
        == 3
    )

    assert (
        receipt.held_out_suite_frozen
        is True
    )

    assert (
        receipt.held_out_outcomes_exposed
        is False
    )

    assert (
        receipt.baseline_authorized
        is False
    )

    assert (
        receipt.release_eligible
        is False
    )


def test_freeze_preserves_runtime_boundary(
) -> None:
    receipt, _receipt_sha = (
        materialize_phase4_held_out_case_freeze(
            ROOT
        )
    )

    assert len(receipt.case_ids) == 18
    assert len(set(receipt.case_ids)) == 18
