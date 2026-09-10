"""Freeze the reviewed Phase 4C TUNING case suite by exact bytes."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.tuning_cases import (
    Phase4TuningCaseSuite,
)

EXPECTED_TUNING_CASES_JSON_SHA256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)

EXPECTED_TUNING_CASES_MARKDOWN_SHA256 = (
    "1e51fe7eda8b804c92696c8ce9434721ff9355436cfc67f2483a1471edf86b7a"
)

_SUITE_JSON_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_cases_v1.json"
)

_SUITE_MARKDOWN_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_cases_v1.md"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_case_freeze_v1.json"
)


class Phase4TuningCaseFreezeReceipt(
    ContractModel
):
    """Immutable custody receipt for the reviewed TUNING suite."""

    receipt_version: Literal[
        "phase4c-tuning-case-freeze-v1"
    ] = "phase4c-tuning-case-freeze-v1"

    suite_version: Literal[
        "phase4c-tuning-cases-v1"
    ] = "phase4c-tuning-cases-v1"

    tuning_cases_json_sha256: Literal[
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
    ] = (
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
    )

    tuning_cases_markdown_sha256: Literal[
        "1e51fe7eda8b804c92696c8ce9434721ff9355436cfc67f2483a1471edf86b7a"
    ] = (
        "1e51fe7eda8b804c92696c8ce9434721ff9355436cfc67f2483a1471edf86b7a"
    )

    authoring_dossier_sha256: Sha256
    refusal_semantic_review_sha256: Sha256

    case_count: Literal[18] = 18
    cluster_count: Literal[9] = 9

    current_single_source_count: Literal[6] = 6
    current_multi_evidence_count: Literal[3] = 3
    version_freshness_count: Literal[3] = 3
    authority_scope_count: Literal[3] = 3
    must_refuse_count: Literal[3] = 3

    case_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=18,
        max_length=18,
    )

    tuning_case_authoring_complete: Literal[
        True
    ] = True

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

    @model_validator(mode="after")
    def validate_freeze(
        self,
    ) -> Self:
        if (
            len(self.case_ids)
            != len(set(self.case_ids))
        ):
            raise ValueError(
                "frozen TUNING case IDs must be unique"
            )

        return self


class Phase4TuningCaseFreezeError(
    ValueError
):
    """Reviewed TUNING bytes cannot be safely frozen."""


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _read_verified(
    path: Path,
) -> tuple[
    bytes,
    str,
]:
    content = path.read_bytes()

    digest = _sha256_bytes(
        content
    )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    observed = (
        sidecar.read_text(
            encoding="utf-8"
        )
        .strip()
    )

    expected = (
        f"{digest}  {path.name}"
    )

    if observed != expected:
        raise Phase4TuningCaseFreezeError(
            f"SHA sidecar mismatch: {path}"
        )

    return (
        content,
        digest,
    )


def materialize_phase4_tuning_case_freeze(
    repo_root: Path,
) -> tuple[
    Phase4TuningCaseFreezeReceipt,
    str,
]:
    suite_bytes, suite_json_sha = (
        _read_verified(
            repo_root
            / _SUITE_JSON_PATH
        )
    )

    markdown_bytes, markdown_sha = (
        _read_verified(
            repo_root
            / _SUITE_MARKDOWN_PATH
        )
    )

    if (
        suite_json_sha
        != EXPECTED_TUNING_CASES_JSON_SHA256
    ):
        raise Phase4TuningCaseFreezeError(
            "TUNING JSON bytes differ from "
            "the semantically reviewed artifact"
        )

    if (
        markdown_sha
        != EXPECTED_TUNING_CASES_MARKDOWN_SHA256
    ):
        raise Phase4TuningCaseFreezeError(
            "TUNING Markdown bytes differ from "
            "the semantically reviewed artifact"
        )

    suite = (
        Phase4TuningCaseSuite
        .model_validate_json(
            suite_bytes
        )
    )

    if (
        suite.review_markdown_sha256
        != markdown_sha
    ):
        raise Phase4TuningCaseFreezeError(
            "suite JSON does not bind the reviewed Markdown"
        )

    if (
        suite.tuning_case_authoring_complete
        is not True
    ):
        raise Phase4TuningCaseFreezeError(
            "TUNING authoring is not complete"
        )

    if (
        suite.tuning_suite_frozen
        is not False
    ):
        raise Phase4TuningCaseFreezeError(
            "source candidate unexpectedly reports frozen"
        )

    if (
        suite.baseline_authorized
        is not False
    ):
        raise Phase4TuningCaseFreezeError(
            "baseline became authorized before freeze"
        )

    if (
        suite.release_eligible
        is not False
    ):
        raise Phase4TuningCaseFreezeError(
            "candidate became release eligible before freeze"
        )

    case_ids = tuple(
        record.case.case_id
        for record
        in suite.records
    )

    for record in suite.records:
        runtime_fields = set(
            record.case
            .to_runtime_input()
            .model_dump()
        )

        if runtime_fields != {
            "case_id",
            "query",
        }:
            raise Phase4TuningCaseFreezeError(
                "evaluator-only fields leaked "
                "through runtime projection"
            )

    receipt = (
        Phase4TuningCaseFreezeReceipt(
            authoring_dossier_sha256=(
                suite.authoring_dossier_sha256
            ),
            refusal_semantic_review_sha256=(
                suite.refusal_semantic_review_sha256
            ),
            case_ids=case_ids,
        )
    )

    receipt_sha = (
        write_json_with_sha256(
            repo_root
            / _FREEZE_RECEIPT_PATH,
            receipt,
        )
    )

    # Keep both byte reads semantically meaningful:
    # the exact Markdown bytes are part of the frozen custody pair.
    if not markdown_bytes:
        raise Phase4TuningCaseFreezeError(
            "reviewed Markdown is empty"
        )

    return (
        receipt,
        receipt_sha,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    (
        receipt,
        receipt_sha,
    ) = (
        materialize_phase4_tuning_case_freeze(
            repo_root
        )
    )

    print(
        "PHASE4C_TUNING_FREEZE_CASE_COUNT="
        f"{receipt.case_count}"
    )

    print(
        "PHASE4C_TUNING_FREEZE_CLUSTER_COUNT="
        f"{receipt.cluster_count}"
    )

    print(
        "PHASE4C_TUNING_CASES_JSON_SHA256="
        f"{receipt.tuning_cases_json_sha256}"
    )

    print(
        "PHASE4C_TUNING_CASES_MARKDOWN_SHA256="
        f"{receipt.tuning_cases_markdown_sha256}"
    )

    print(
        "PHASE4C_TUNING_SUITE_FROZEN=true"
    )

    print(
        "PHASE4_HELD_OUT_OUTCOMES_EXPOSED=false"
    )

    print(
        "PHASE4_BASELINE_AUTHORIZED=false"
    )

    print(
        "PHASE4_RELEASE_ELIGIBLE=false"
    )

    print(
        "PHASE4C_TUNING_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha}"
    )


if __name__ == "__main__":
    main()
