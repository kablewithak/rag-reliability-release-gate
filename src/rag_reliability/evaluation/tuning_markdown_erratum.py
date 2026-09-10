"""Record the immutable Phase 4C TUNING Markdown quota erratum."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from rag_reliability.contracts.base import (
    ContractModel,
    Sha256,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.tuning_cases import (
    Phase4TuningCaseSuite,
)

_TUNING_JSON_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_cases_v1.json"
)

_TUNING_MARKDOWN_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_cases_v1.md"
)

_ERRATUM_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_markdown_erratum_v1.json"
)

EXPECTED_JSON_SHA256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)

EXPECTED_AFFECTED_MARKDOWN_SHA256 = (
    "1e51fe7eda8b804c92696c8ce9434721ff9355436cfc67f2483a1471edf86b7a"
)


class Phase4TuningQuotaCounts(
    ContractModel
):
    case_count: int
    cluster_count: int
    current_single_source_count: int
    current_multi_evidence_count: int
    version_freshness_count: int
    authority_scope_count: int
    must_refuse_count: int


class Phase4TuningMarkdownErratum(
    ContractModel
):
    receipt_version: Literal[
        "phase4c-tuning-markdown-erratum-v1"
    ] = "phase4c-tuning-markdown-erratum-v1"

    affected_artifact: Literal[
        "artifacts/development/phase4c_tuning_cases_v1.md"
    ] = (
        "artifacts/development/"
        "phase4c_tuning_cases_v1.md"
    )

    affected_markdown_sha256: Sha256
    canonical_json_sha256: Sha256

    observed_incorrect_header: Phase4TuningQuotaCounts
    authoritative_corrected_header: Phase4TuningQuotaCounts

    canonical_case_data_affected: Literal[
        False
    ] = False

    runtime_projection_affected: Literal[
        False
    ] = False

    tuning_suite_frozen: Literal[
        True
    ] = True

    held_out_outcomes_exposed: Literal[
        False
    ] = False

    baseline_authorized: Literal[
        False
    ] = False

    release_eligible: Literal[
        False
    ] = False


def _sha256(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def main() -> None:
    json_bytes = _TUNING_JSON_PATH.read_bytes()
    markdown_bytes = _TUNING_MARKDOWN_PATH.read_bytes()

    json_sha = _sha256(
        json_bytes
    )

    markdown_sha = _sha256(
        markdown_bytes
    )

    if json_sha != EXPECTED_JSON_SHA256:
        raise RuntimeError(
            "Canonical TUNING JSON SHA drifted"
        )

    if (
        markdown_sha
        != EXPECTED_AFFECTED_MARKDOWN_SHA256
    ):
        raise RuntimeError(
            "Affected TUNING Markdown SHA drifted"
        )

    suite = (
        Phase4TuningCaseSuite
        .model_validate_json(
            json_bytes
        )
    )

    corrected = Phase4TuningQuotaCounts(
        case_count=suite.case_count,
        cluster_count=suite.cluster_count,
        current_single_source_count=(
            suite.current_single_source_count
        ),
        current_multi_evidence_count=(
            suite.current_multi_evidence_count
        ),
        version_freshness_count=(
            suite.version_freshness_count
        ),
        authority_scope_count=(
            suite.authority_scope_count
        ),
        must_refuse_count=(
            suite.must_refuse_count
        ),
    )

    expected_corrected = (
        Phase4TuningQuotaCounts(
            case_count=18,
            cluster_count=9,
            current_single_source_count=6,
            current_multi_evidence_count=3,
            version_freshness_count=3,
            authority_scope_count=3,
            must_refuse_count=3,
        )
    )

    if corrected != expected_corrected:
        raise RuntimeError(
            "Canonical TUNING JSON counts "
            "do not match reviewed correction"
        )

    receipt = Phase4TuningMarkdownErratum(
        affected_markdown_sha256=(
            markdown_sha
        ),
        canonical_json_sha256=json_sha,
        observed_incorrect_header=(
            Phase4TuningQuotaCounts(
                case_count=24,
                cluster_count=12,
                current_single_source_count=7,
                current_multi_evidence_count=5,
                version_freshness_count=5,
                authority_scope_count=3,
                must_refuse_count=4,
            )
        ),
        authoritative_corrected_header=(
            corrected
        ),
    )

    receipt_sha = write_json_with_sha256(
        _ERRATUM_PATH,
        receipt,
    )

    print(
        "PHASE4C_TUNING_MARKDOWN_ERRATUM=RECORDED"
    )
    print(
        "AFFECTED_MARKDOWN_SHA256="
        f"{markdown_sha}"
    )
    print(
        "CANONICAL_JSON_SHA256="
        f"{json_sha}"
    )
    print(
        "CORRECT_CASE_COUNT="
        f"{corrected.case_count}"
    )
    print(
        "CORRECT_CLUSTER_COUNT="
        f"{corrected.cluster_count}"
    )
    print(
        "CANONICAL_CASE_DATA_AFFECTED=false"
    )
    print(
        "BASELINE_AUTHORIZED=false"
    )
    print(
        "ERRATUM_RECEIPT_SHA256="
        f"{receipt_sha}"
    )


if __name__ == "__main__":
    main()
