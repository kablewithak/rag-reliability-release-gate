"""Freeze the reviewed Phase 4C DEVELOPMENT case suite by exact bytes."""

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
from rag_reliability.evaluation.development_cases import (
    Phase4DevelopmentCaseSuite,
)

EXPECTED_DEVELOPMENT_CASES_JSON_SHA256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)

EXPECTED_DEVELOPMENT_CASES_MARKDOWN_SHA256 = (
    "17346d2609c71e994f60d5c99f1bb348c822a4a9d74dc17786156466337873f3"
)

_SUITE_JSON_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_development_cases_v1.json"
)

_SUITE_MARKDOWN_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_development_cases_v1.md"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_development_case_freeze_v1.json"
)


class Phase4DevelopmentCaseFreezeReceipt(
    ContractModel
):
    """Immutable custody receipt for the reviewed DEVELOPMENT suite."""

    receipt_version: Literal[
        "phase4c-development-case-freeze-v1"
    ] = "phase4c-development-case-freeze-v1"

    suite_version: Literal[
        "phase4c-development-cases-v1"
    ] = "phase4c-development-cases-v1"

    development_cases_json_sha256: Literal[
        "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
    ] = (
        "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
    )

    development_cases_markdown_sha256: Literal[
        "17346d2609c71e994f60d5c99f1bb348c822a4a9d74dc17786156466337873f3"
    ] = (
        "17346d2609c71e994f60d5c99f1bb348c822a4a9d74dc17786156466337873f3"
    )

    authoring_dossier_sha256: Sha256
    refusal_semantic_review_sha256: Sha256

    case_count: Literal[24] = 24
    cluster_count: Literal[12] = 12

    current_single_source_count: Literal[7] = 7
    current_multi_evidence_count: Literal[5] = 5
    version_freshness_count: Literal[5] = 5
    authority_scope_count: Literal[3] = 3
    must_refuse_count: Literal[4] = 4

    case_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=24,
        max_length=24,
    )

    development_case_authoring_complete: Literal[
        True
    ] = True

    development_suite_frozen: Literal[
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
                "frozen DEVELOPMENT case IDs must be unique"
            )

        return self


class Phase4DevelopmentCaseFreezeError(
    ValueError
):
    """Reviewed DEVELOPMENT bytes cannot be safely frozen."""


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
        raise Phase4DevelopmentCaseFreezeError(
            f"SHA sidecar mismatch: {path}"
        )

    return (
        content,
        digest,
    )


def materialize_phase4_development_case_freeze(
    repo_root: Path,
) -> tuple[
    Phase4DevelopmentCaseFreezeReceipt,
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
        != EXPECTED_DEVELOPMENT_CASES_JSON_SHA256
    ):
        raise Phase4DevelopmentCaseFreezeError(
            "DEVELOPMENT JSON bytes differ from "
            "the semantically reviewed artifact"
        )

    if (
        markdown_sha
        != EXPECTED_DEVELOPMENT_CASES_MARKDOWN_SHA256
    ):
        raise Phase4DevelopmentCaseFreezeError(
            "DEVELOPMENT Markdown bytes differ from "
            "the semantically reviewed artifact"
        )

    suite = (
        Phase4DevelopmentCaseSuite
        .model_validate_json(
            suite_bytes
        )
    )

    if (
        suite.review_markdown_sha256
        != markdown_sha
    ):
        raise Phase4DevelopmentCaseFreezeError(
            "suite JSON does not bind the reviewed Markdown"
        )

    if (
        suite.development_case_authoring_complete
        is not True
    ):
        raise Phase4DevelopmentCaseFreezeError(
            "DEVELOPMENT authoring is not complete"
        )

    if (
        suite.development_suite_frozen
        is not False
    ):
        raise Phase4DevelopmentCaseFreezeError(
            "source candidate unexpectedly reports frozen"
        )

    if (
        suite.baseline_authorized
        is not False
    ):
        raise Phase4DevelopmentCaseFreezeError(
            "baseline became authorized before freeze"
        )

    if (
        suite.release_eligible
        is not False
    ):
        raise Phase4DevelopmentCaseFreezeError(
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
            raise Phase4DevelopmentCaseFreezeError(
                "evaluator-only fields leaked "
                "through runtime projection"
            )

    receipt = (
        Phase4DevelopmentCaseFreezeReceipt(
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
        raise Phase4DevelopmentCaseFreezeError(
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
        materialize_phase4_development_case_freeze(
            repo_root
        )
    )

    print(
        "PHASE4C_DEVELOPMENT_FREEZE_CASE_COUNT="
        f"{receipt.case_count}"
    )

    print(
        "PHASE4C_DEVELOPMENT_FREEZE_CLUSTER_COUNT="
        f"{receipt.cluster_count}"
    )

    print(
        "PHASE4C_DEVELOPMENT_CASES_JSON_SHA256="
        f"{receipt.development_cases_json_sha256}"
    )

    print(
        "PHASE4C_DEVELOPMENT_CASES_MARKDOWN_SHA256="
        f"{receipt.development_cases_markdown_sha256}"
    )

    print(
        "PHASE4C_DEVELOPMENT_SUITE_FROZEN=true"
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
        "PHASE4C_DEVELOPMENT_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha}"
    )


if __name__ == "__main__":
    main()
