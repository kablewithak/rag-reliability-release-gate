import hashlib
from pathlib import Path

from rag_reliability.evaluation.tuning_markdown_erratum import (
    EXPECTED_AFFECTED_MARKDOWN_SHA256,
    EXPECTED_JSON_SHA256,
    Phase4TuningMarkdownErratum,
)

ROOT = Path(__file__).resolve().parents[2]

JSON_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_cases_v1.json"
)

MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_cases_v1.md"
)

ERRATUM_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_markdown_erratum_v1.json"
)


def _sha256(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def test_erratum_preserves_exact_frozen_artifacts(
) -> None:
    assert (
        _sha256(
            JSON_PATH.read_bytes()
        )
        == EXPECTED_JSON_SHA256
    )

    assert (
        _sha256(
            MARKDOWN_PATH.read_bytes()
        )
        == EXPECTED_AFFECTED_MARKDOWN_SHA256
    )


def test_erratum_records_actual_and_corrected_counts(
) -> None:
    receipt = (
        Phase4TuningMarkdownErratum
        .model_validate_json(
            ERRATUM_PATH.read_bytes()
        )
    )

    observed = (
        receipt.observed_incorrect_header
    )

    assert observed.case_count == 24
    assert observed.cluster_count == 12
    assert (
        observed.current_single_source_count
        == 7
    )
    assert (
        observed.current_multi_evidence_count
        == 5
    )
    assert (
        observed.version_freshness_count
        == 5
    )
    assert observed.authority_scope_count == 3
    assert observed.must_refuse_count == 4

    corrected = (
        receipt.authoritative_corrected_header
    )

    assert corrected.case_count == 18
    assert corrected.cluster_count == 9
    assert (
        corrected.current_single_source_count
        == 6
    )
    assert (
        corrected.current_multi_evidence_count
        == 3
    )
    assert (
        corrected.version_freshness_count
        == 3
    )
    assert corrected.authority_scope_count == 3
    assert corrected.must_refuse_count == 3


def test_erratum_does_not_reauthorize_or_rewrite_suite(
) -> None:
    receipt = (
        Phase4TuningMarkdownErratum
        .model_validate_json(
            ERRATUM_PATH.read_bytes()
        )
    )

    assert (
        receipt.canonical_case_data_affected
        is False
    )

    assert (
        receipt.runtime_projection_affected
        is False
    )

    assert receipt.tuning_suite_frozen is True

    assert (
        receipt.held_out_outcomes_exposed
        is False
    )

    assert receipt.baseline_authorized is False
    assert receipt.release_eligible is False
