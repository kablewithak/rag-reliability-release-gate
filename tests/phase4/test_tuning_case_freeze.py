import hashlib
from pathlib import Path

from rag_reliability.evaluation.tuning_case_freeze import (
    EXPECTED_TUNING_CASES_JSON_SHA256,
    EXPECTED_TUNING_CASES_MARKDOWN_SHA256,
    Phase4TuningCaseFreezeReceipt,
)
from rag_reliability.evaluation.tuning_cases import (
    Phase4TuningCaseSuite,
)

ROOT = Path(__file__).resolve().parents[2]

SUITE_JSON_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_cases_v1.json"
)

SUITE_MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_cases_v1.md"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_case_freeze_v1.json"
)


def _sha256(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _suite(
) -> Phase4TuningCaseSuite:
    return (
        Phase4TuningCaseSuite
        .model_validate_json(
            SUITE_JSON_PATH.read_bytes()
        )
    )


def _receipt(
) -> Phase4TuningCaseFreezeReceipt:
    return (
        Phase4TuningCaseFreezeReceipt
        .model_validate_json(
            RECEIPT_PATH.read_bytes()
        )
    )


def test_freeze_binds_exact_reviewed_tuning_bytes(
) -> None:
    receipt = _receipt()

    assert (
        _sha256(
            SUITE_JSON_PATH.read_bytes()
        )
        == EXPECTED_TUNING_CASES_JSON_SHA256
        == receipt.tuning_cases_json_sha256
    )

    assert (
        _sha256(
            SUITE_MARKDOWN_PATH.read_bytes()
        )
        == EXPECTED_TUNING_CASES_MARKDOWN_SHA256
        == receipt.tuning_cases_markdown_sha256
    )


def test_freeze_receipt_preserves_exact_tuning_case_identity(
) -> None:
    suite = _suite()
    receipt = _receipt()

    expected_case_ids = tuple(
        record.case.case_id
        for record
        in suite.records
    )

    assert (
        receipt.case_ids
        == expected_case_ids
    )

    assert len(
        receipt.case_ids
    ) == 18

    assert len(
        set(receipt.case_ids)
    ) == 18


def test_freeze_preserves_tuning_quota(
) -> None:
    receipt = _receipt()

    assert receipt.case_count == 18
    assert receipt.cluster_count == 9

    assert (
        receipt.current_single_source_count
        == 6
    )

    assert (
        receipt.current_multi_evidence_count
        == 3
    )

    assert (
        receipt.version_freshness_count
        == 3
    )

    assert (
        receipt.authority_scope_count
        == 3
    )

    assert (
        receipt.must_refuse_count
        == 3
    )


def test_external_receipt_freezes_unmodified_tuning_candidate(
) -> None:
    suite = _suite()
    receipt = _receipt()

    assert (
        suite.tuning_suite_frozen
        is False
    )

    assert (
        receipt.tuning_suite_frozen
        is True
    )

    assert (
        receipt.tuning_case_authoring_complete
        is True
    )


def test_tuning_freeze_does_not_expose_held_out_or_authorize_baseline(
) -> None:
    receipt = _receipt()

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


def test_tuning_freeze_receipt_sidecar_matches_exact_bytes(
) -> None:
    digest = _sha256(
        RECEIPT_PATH.read_bytes()
    )

    sidecar = (
        RECEIPT_PATH
        .with_suffix(
            ".json.sha256"
        )
    )

    assert (
        sidecar.read_text(
            encoding="utf-8"
        ).strip()
        == (
            f"{digest}  "
            f"{RECEIPT_PATH.name}"
        )
    )


def test_runtime_boundary_remains_gold_free_after_tuning_freeze(
) -> None:
    suite = _suite()

    for record in suite.records:
        runtime = (
            record.case
            .to_runtime_input()
            .model_dump()
        )

        assert set(
            runtime
        ) == {
            "case_id",
            "query",
        }
