"""Freeze the reviewed Phase 4C HELD_OUT case suite by exact bytes."""

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
from rag_reliability.contracts.enums import (
    EvaluationRole,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.held_out_cases import (
    Phase4HeldOutCaseSuite,
)

EXPECTED_HELD_OUT_CASES_JSON_SHA256 = (
    "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
)

EXPECTED_HELD_OUT_CASES_MARKDOWN_SHA256 = (
    "701f23b4877c9193bfd34fb33f7f5ac3e67432073b495e5b0058b30599965749"
)

_SUITE_JSON_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_held_out_cases_v1.json"
)

_SUITE_MARKDOWN_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_held_out_cases_v1.md"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_held_out_case_freeze_v1.json"
)


class Phase4HeldOutCaseFreezeReceipt(
    ContractModel
):
    """Immutable custody receipt for the reviewed HELD_OUT suite."""

    receipt_version: Literal[
        "phase4c-held-out-case-freeze-v1"
    ] = "phase4c-held-out-case-freeze-v1"

    suite_version: Literal[
        "phase4c-held-out-cases-v1"
    ] = "phase4c-held-out-cases-v1"

    held_out_cases_json_sha256: Literal[
        "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"
    ] = "32eb820989c35a372266ec293aa43efd4651147e833f68aeab8c896282f047f8"

    held_out_cases_markdown_sha256: Literal[
        "701f23b4877c9193bfd34fb33f7f5ac3e67432073b495e5b0058b30599965749"
    ] = "701f23b4877c9193bfd34fb33f7f5ac3e67432073b495e5b0058b30599965749"

    authoring_dossier_sha256: Sha256
    refusal_semantic_review_sha256: Sha256

    case_count: Literal[18] = 18
    cluster_count: Literal[9] = 9

    current_single_source_count: Literal[
        5
    ] = 5

    current_multi_evidence_count: Literal[
        4
    ] = 4

    version_freshness_count: Literal[
        4
    ] = 4

    authority_scope_count: Literal[
        2
    ] = 2

    must_refuse_count: Literal[
        3
    ] = 3

    case_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=18,
        max_length=18,
    )

    held_out_case_authoring_complete: Literal[
        True
    ] = True

    held_out_suite_frozen: Literal[
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
                "frozen HELD_OUT case IDs "
                "must be unique"
            )

        return self


class Phase4HeldOutCaseFreezeError(
    ValueError
):
    """Reviewed HELD_OUT bytes cannot be safely frozen."""


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _verify_sidecar(
    path: Path,
    digest: str,
) -> None:
    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    observed = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    expected = (
        f"{digest}  {path.name}"
    )

    if observed != expected:
        raise Phase4HeldOutCaseFreezeError(
            f"SHA sidecar mismatch: {path}"
        )


def materialize_phase4_held_out_case_freeze(
    repo_root: Path,
) -> tuple[
    Phase4HeldOutCaseFreezeReceipt,
    str,
]:
    json_path = (
        repo_root
        / _SUITE_JSON_PATH
    )

    markdown_path = (
        repo_root
        / _SUITE_MARKDOWN_PATH
    )

    json_bytes = json_path.read_bytes()
    markdown_bytes = (
        markdown_path.read_bytes()
    )

    json_sha = _sha256_bytes(
        json_bytes
    )

    markdown_sha = _sha256_bytes(
        markdown_bytes
    )

    if (
        json_sha
        != EXPECTED_HELD_OUT_CASES_JSON_SHA256
    ):
        raise Phase4HeldOutCaseFreezeError(
            "reviewed HELD_OUT JSON "
            "bytes drifted"
        )

    if (
        markdown_sha
        != EXPECTED_HELD_OUT_CASES_MARKDOWN_SHA256
    ):
        raise Phase4HeldOutCaseFreezeError(
            "reviewed HELD_OUT Markdown "
            "bytes drifted"
        )

    _verify_sidecar(
        json_path,
        json_sha,
    )

    _verify_sidecar(
        markdown_path,
        markdown_sha,
    )

    suite = (
        Phase4HeldOutCaseSuite
        .model_validate_json(
            json_bytes
        )
    )

    if (
        suite.review_markdown_sha256
        != markdown_sha
    ):
        raise Phase4HeldOutCaseFreezeError(
            "suite review Markdown SHA "
            "does not match exact bytes"
        )

    if (
        suite.held_out_case_authoring_complete
        is not True
    ):
        raise Phase4HeldOutCaseFreezeError(
            "HELD_OUT authoring is incomplete"
        )

    if (
        suite.held_out_suite_frozen
        is not False
    ):
        raise Phase4HeldOutCaseFreezeError(
            "candidate must remain "
            "internally unfrozen"
        )

    if (
        suite.held_out_outcomes_exposed
        is not False
    ):
        raise Phase4HeldOutCaseFreezeError(
            "HELD_OUT outcomes are exposed"
        )

    if (
        suite.baseline_authorized
        is not False
    ):
        raise Phase4HeldOutCaseFreezeError(
            "baseline must remain unauthorized"
        )

    if (
        suite.release_eligible
        is not False
    ):
        raise Phase4HeldOutCaseFreezeError(
            "release must remain ineligible"
        )

    if (
        suite.case_count != 18
        or suite.cluster_count != 9
    ):
        raise Phase4HeldOutCaseFreezeError(
            "HELD_OUT suite dimensions drifted"
        )

    expected_counts = (
        5,
        4,
        4,
        2,
        3,
    )

    observed_counts = (
        suite.current_single_source_count,
        suite.current_multi_evidence_count,
        suite.version_freshness_count,
        suite.authority_scope_count,
        suite.must_refuse_count,
    )

    if observed_counts != expected_counts:
        raise Phase4HeldOutCaseFreezeError(
            "HELD_OUT scenario quotas drifted"
        )

    case_ids = tuple(
        record.case.case_id
        for record in suite.records
    )

    for record in suite.records:
        if (
            record.case.data_role
            is not EvaluationRole.HELD_OUT
        ):
            raise Phase4HeldOutCaseFreezeError(
                "non-HELD_OUT case entered "
                "HELD_OUT freeze"
            )

        runtime = (
            record.case
            .to_runtime_input()
            .model_dump()
        )

        if set(runtime) != {
            "case_id",
            "query",
        }:
            raise Phase4HeldOutCaseFreezeError(
                "gold fields leaked through "
                "runtime projection"
            )

    receipt = (
        Phase4HeldOutCaseFreezeReceipt(
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

    return (
        receipt,
        receipt_sha,
    )


def main() -> None:
    repo_root = (
        Path(__file__).resolve()
        .parents[3]
    )

    (
        receipt,
        receipt_sha,
    ) = (
        materialize_phase4_held_out_case_freeze(
            repo_root
        )
    )

    print(
        "PHASE4C_HELD_OUT_CASE_COUNT="
        f"{receipt.case_count}"
    )

    print(
        "PHASE4C_HELD_OUT_CLUSTER_COUNT="
        f"{receipt.cluster_count}"
    )

    print(
        "PHASE4C_HELD_OUT_SUITE_FROZEN=true"
    )

    print(
        "PHASE4C_HELD_OUT_OUTCOMES_EXPOSED=false"
    )

    print(
        "PHASE4_BASELINE_AUTHORIZED=false"
    )

    print(
        "PHASE4_RELEASE_ELIGIBLE=false"
    )

    print(
        "PHASE4C_HELD_OUT_CASES_JSON_SHA256="
        f"{receipt.held_out_cases_json_sha256}"
    )

    print(
        "PHASE4C_HELD_OUT_CASES_MARKDOWN_SHA256="
        f"{receipt.held_out_cases_markdown_sha256}"
    )

    print(
        "PHASE4C_HELD_OUT_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha}"
    )


if __name__ == "__main__":
    main()
