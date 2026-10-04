"""Strict query-only projection for the authorized B0 DEVELOPMENT/TUNING suites."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.contracts.evaluation import RuntimeCaseInput

_DEVELOPMENT_PATH = (
    Path("artifacts") / "development" / "phase4c_development_cases_v1.json"
)
_TUNING_PATH = Path("artifacts") / "development" / "phase4c_tuning_cases_v1.json"

_DEVELOPMENT_SHA256: Sha256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SHA256: Sha256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)

DevelopmentRole = Literal["evaluation_development_case"]
TuningRole = Literal["intervention_tuning_case"]
B0Role = DevelopmentRole | TuningRole


class B0ProjectedSuite(ContractModel):
    """One frozen suite reduced to fields allowed into fixture authoring/runtime."""

    role: B0Role
    suite_sha256: Sha256
    cases: tuple[RuntimeCaseInput, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_case_ids(self) -> Self:
        case_ids = tuple(case.case_id for case in self.cases)
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("projected suite case IDs must be unique")
        return self


class Phase5B0RuntimeProjectionV1(ContractModel):
    """Trusted orchestration envelope around query-only case projections."""

    projection_version: Literal[
        "phase5-b0-runtime-projection-v1"
    ] = "phase5-b0-runtime-projection-v1"

    runtime_projection_fields: tuple[str, str] = ("case_id", "query")

    development: B0ProjectedSuite
    tuning: B0ProjectedSuite

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        if self.runtime_projection_fields != ("case_id", "query"):
            raise ValueError("B0 runtime projection field boundary drifted")

        if self.development.role != "evaluation_development_case":
            raise ValueError("DEVELOPMENT projection role drifted")

        if self.tuning.role != "intervention_tuning_case":
            raise ValueError("TUNING projection role drifted")

        if self.development.suite_sha256 != _DEVELOPMENT_SHA256:
            raise ValueError("DEVELOPMENT suite identity drifted")

        if self.tuning.suite_sha256 != _TUNING_SHA256:
            raise ValueError("TUNING suite identity drifted")

        if len(self.development.cases) != 24:
            raise ValueError("DEVELOPMENT projection must contain 24 cases")

        if len(self.tuning.cases) != 18:
            raise ValueError("TUNING projection must contain 18 cases")

        all_case_ids = tuple(
            case.case_id
            for suite in (self.development, self.tuning)
            for case in suite.cases
        )

        if len(all_case_ids) != 42:
            raise ValueError("B0 runtime projection must contain 42 cases")

        if len(all_case_ids) != len(set(all_case_ids)):
            raise ValueError("B0 runtime projection case IDs must be globally unique")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(
    path: Path,
    expected_sha256: str,
) -> bytes:
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen suite hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise ValueError(f"frozen suite sidecar mismatch: {path}")

    return content


def _project_payload(
    payload: object,
    *,
    expected_case_count: int,
) -> tuple[RuntimeCaseInput, ...]:
    """Project only case_id/query; evaluator-owned case fields are ignored."""

    if not isinstance(payload, dict):
        raise ValueError("evaluation suite must be a JSON object")

    if payload.get("case_count") != expected_case_count:
        raise ValueError("evaluation suite case_count drifted")

    raw_records = payload.get("records")
    if not isinstance(raw_records, list):
        raise ValueError("evaluation suite records must be a JSON array")

    projected: list[RuntimeCaseInput] = []

    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            raise ValueError("evaluation suite record must be an object")

        raw_case = raw_record.get("case")
        if not isinstance(raw_case, dict):
            raise ValueError("evaluation suite record requires case object")

        case_id = raw_case.get("case_id")
        query = raw_case.get("query")

        if not isinstance(case_id, str) or not case_id:
            raise ValueError("projected case_id must be non-empty text")
        if not isinstance(query, str) or not query:
            raise ValueError("projected query must be non-empty text")

        # Deliberately read only the two allowlisted fields. Do not construct
        # EvaluationCase here: that would carry evaluator-owned fields across
        # the authoring boundary.
        projected.append(
            RuntimeCaseInput(
                case_id=case_id,
                query=query,
            )
        )

    if len(projected) != expected_case_count:
        raise ValueError("evaluation suite record count drifted")

    case_ids = tuple(case.case_id for case in projected)
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("evaluation suite projected case IDs must be unique")

    return tuple(projected)


def _load_projected_suite(
    repo_root: Path,
    *,
    path: Path,
    expected_sha256: str,
    expected_case_count: int,
    role: B0Role,
) -> B0ProjectedSuite:
    content = _verified_bytes(
        repo_root / path,
        expected_sha256,
    )
    payload = json.loads(content)

    return B0ProjectedSuite(
        role=role,
        suite_sha256=expected_sha256,
        cases=_project_payload(
            payload,
            expected_case_count=expected_case_count,
        ),
    )


def load_phase5_b0_runtime_projection(
    repo_root: Path,
) -> Phase5B0RuntimeProjectionV1:
    """Load only the two frozen nonprotected B0 suites into a query-only envelope."""

    return Phase5B0RuntimeProjectionV1(
        development=_load_projected_suite(
            repo_root,
            path=_DEVELOPMENT_PATH,
            expected_sha256=_DEVELOPMENT_SHA256,
            expected_case_count=24,
            role="evaluation_development_case",
        ),
        tuning=_load_projected_suite(
            repo_root,
            path=_TUNING_PATH,
            expected_sha256=_TUNING_SHA256,
            expected_case_count=18,
            role="intervention_tuning_case",
        ),
    )
