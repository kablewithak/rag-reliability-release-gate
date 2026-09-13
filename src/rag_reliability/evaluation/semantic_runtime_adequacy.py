"""Derive Phase 5 semantic-runtime structural floors without executing B0.

This audit reads frozen DEVELOPMENT/TUNING case metadata and the frozen Phase 3D
chunk manifest. It does not run retrieval, invoke a provider, score outcomes, or
expose HELD_OUT data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256

_DEVELOPMENT_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_development_cases_v1.json"
)
_TUNING_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_tuning_cases_v1.json"
)
_CHUNK_MANIFEST_PATH = (
    Path("datasets")
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_semantic_runtime_adequacy_v1.json"
)

_DEVELOPMENT_SHA256: Literal[
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
] = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"

_TUNING_SHA256: Literal[
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
] = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"

_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"


class Phase5SemanticRuntimeAdequacyReceipt(ContractModel):
    """Static structural requirements for a future semantic runtime config."""

    receipt_version: Literal[
        "phase5-semantic-runtime-adequacy-v1"
    ] = "phase5-semantic-runtime-adequacy-v1"

    development_suite_sha256: Literal[
        "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
    ] = _DEVELOPMENT_SHA256

    tuning_suite_sha256: Literal[
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
    ] = _TUNING_SHA256

    chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = _CHUNK_MANIFEST_SHA256

    included_case_count: Literal[42] = 42
    development_case_count: Literal[24] = 24
    tuning_case_count: Literal[18] = 18

    answerable_case_count: int = Field(ge=1)
    refusal_case_count: int = Field(ge=1)

    required_evidence_reference_count: int = Field(ge=1)
    unique_required_evidence_count: int = Field(ge=1)

    minimum_top_k_structural_floor: int = Field(ge=1)
    minimum_max_evidence_items_structural_floor: int = Field(ge=1)
    minimum_context_budget_characters_structural_floor: int = Field(ge=1)

    max_required_fact_count: int = Field(ge=1)

    max_required_evidence_case_id: NonEmptyStr
    max_required_context_case_id: NonEmptyStr
    max_required_fact_case_id: NonEmptyStr

    all_required_evidence_present_in_frozen_corpus: Literal[True] = True
    all_required_evidence_content_hashes_verified: Literal[True] = True

    context_budget_rule: Literal[
        "exact_bounded_context_builder_character_assembly"
    ] = "exact_bounded_context_builder_character_assembly"

    retrieval_ranking_adequacy_measured: Literal[False] = False
    semantic_generation_adequacy_measured: Literal[False] = False

    phase2b_runtime_config_reuse_authorized: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if (
            self.minimum_top_k_structural_floor
            != self.minimum_max_evidence_items_structural_floor
        ):
            raise ValueError(
                "retrieval and context structural evidence-count floors drifted"
            )

        if (
            self.answerable_case_count
            + self.refusal_case_count
            != self.included_case_count
        ):
            raise ValueError(
                "answerable/refusal counts do not reconcile to included cases"
            )

        if self.retrieval_ranking_adequacy_measured:
            raise ValueError(
                "static adequacy audit cannot claim retrieval ranking adequacy"
            )

        if self.semantic_generation_adequacy_measured:
            raise ValueError(
                "static adequacy audit cannot claim semantic generation adequacy"
            )

        if self.semantic_runtime_configuration_selected:
            raise ValueError(
                "static adequacy audit cannot select a runtime configuration"
            )

        if self.semantic_runtime_configuration_frozen:
            raise ValueError(
                "static adequacy audit cannot freeze a runtime configuration"
            )

        if self.baseline_execution_authorized:
            raise ValueError(
                "static adequacy audit cannot authorize B0"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "static adequacy audit cannot expose HELD_OUT outcomes"
            )

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(
    path: Path,
    expected_sha256: str,
) -> bytes:
    content = path.read_bytes()
    observed_sha256 = _sha256_bytes(content)

    if observed_sha256 != expected_sha256:
        raise ValueError(
            f"frozen artifact hash mismatch: {path}"
        )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    observed_sidecar = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    expected_sidecar = (
        f"{expected_sha256}  {path.name}"
    )

    if observed_sidecar != expected_sidecar:
        raise ValueError(
            f"SHA sidecar mismatch: {path}"
        )

    return content


def _suite_records(
    content: bytes,
    *,
    expected_case_count: int,
    expected_role: str,
) -> tuple[dict[str, object], ...]:
    payload = json.loads(content)

    if not isinstance(payload, dict):
        raise ValueError(
            "evaluation suite must be a JSON object"
        )

    case_count = payload.get("case_count")

    if case_count != expected_case_count:
        raise ValueError(
            "evaluation suite case count drifted"
        )

    raw_records = payload.get("records")

    if not isinstance(raw_records, list):
        raise ValueError(
            "evaluation suite records must be a JSON array"
        )

    records: list[dict[str, object]] = []

    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            raise ValueError(
                "evaluation suite record must be an object"
            )

        raw_case = raw_record.get("case")

        if not isinstance(raw_case, dict):
            raise ValueError(
                "evaluation suite record requires case object"
            )

        if raw_case.get("data_role") != expected_role:
            raise ValueError(
                "evaluation suite role drifted"
            )

        records.append(
            cast(dict[str, object], raw_case)
        )

    if len(records) != expected_case_count:
        raise ValueError(
            "evaluation suite record count drifted"
        )

    return tuple(records)


def _string_tuple(
    value: object,
    *,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(
            f"{field_name} must be a JSON array"
        )

    if any(
        not isinstance(item, str)
        or not item
        for item in value
    ):
        raise ValueError(
            f"{field_name} must contain non-empty strings"
        )

    typed = cast(list[str], value)

    if len(typed) != len(set(typed)):
        raise ValueError(
            f"{field_name} must be unique"
        )

    return tuple(typed)


def _case_id(case: dict[str, object]) -> str:
    value = case.get("case_id")

    if not isinstance(value, str) or not value:
        raise ValueError(
            "case_id must be a non-empty string"
        )

    return value


def _context_characters(
    *,
    evidence_ids: tuple[str, ...],
    content_by_evidence_id: dict[str, str],
) -> int:
    blocks = tuple(
        (
            f"EVIDENCE: {evidence_id}\n"
            f"{content_by_evidence_id[evidence_id]}"
        )
        for evidence_id in evidence_ids
    )

    return len(
        "\n\n".join(blocks)
    )


def materialize_phase5_semantic_runtime_adequacy(
    repo_root: Path,
) -> tuple[
    Phase5SemanticRuntimeAdequacyReceipt,
    str,
]:
    """Derive structural runtime floors from frozen non-HELD_OUT evidence."""

    development = _suite_records(
        _verified_bytes(
            repo_root / _DEVELOPMENT_PATH,
            _DEVELOPMENT_SHA256,
        ),
        expected_case_count=24,
        expected_role="evaluation_development_case",
    )

    tuning = _suite_records(
        _verified_bytes(
            repo_root / _TUNING_PATH,
            _TUNING_SHA256,
        ),
        expected_case_count=18,
        expected_role="intervention_tuning_case",
    )

    manifest_content = _verified_bytes(
        repo_root / _CHUNK_MANIFEST_PATH,
        _CHUNK_MANIFEST_SHA256,
    )

    manifest = (
        Phase3dChunkManifest.model_validate_json(
            manifest_content
        )
    )

    chunks_by_id = {
        chunk.chunk_id: chunk
        for chunk in manifest.chunks
    }

    cases = (*development, *tuning)

    answerable_cases: list[
        tuple[
            str,
            tuple[str, ...],
            tuple[str, ...],
        ]
    ] = []

    refusal_count = 0

    for case in cases:
        case_id = _case_id(case)
        response_mode = case.get(
            "expected_response_mode"
        )

        if response_mode == "refuse":
            refusal_count += 1
            continue

        if response_mode not in {
            "answer",
            "qualified_answer",
        }:
            raise ValueError(
                f"unknown expected_response_mode: {response_mode}"
            )

        required_evidence_ids = _string_tuple(
            case.get("required_evidence_ids"),
            field_name="required_evidence_ids",
        )

        required_fact_ids = _string_tuple(
            case.get("required_fact_ids"),
            field_name="required_fact_ids",
        )

        if not required_evidence_ids:
            raise ValueError(
                f"answerable case has no required evidence: {case_id}"
            )

        if not required_fact_ids:
            raise ValueError(
                f"answerable case has no required facts: {case_id}"
            )

        answerable_cases.append(
            (
                case_id,
                required_evidence_ids,
                required_fact_ids,
            )
        )

    if len(answerable_cases) + refusal_count != 42:
        raise ValueError(
            "answerable/refusal case counts do not reconcile"
        )

    all_required_evidence_ids = {
        evidence_id
        for (
            _case_id_value,
            case_required_evidence,
            _required_fact_ids,
        ) in answerable_cases
        for evidence_id in case_required_evidence
    }

    missing_evidence = (
        all_required_evidence_ids
        - set(chunks_by_id)
    )

    if missing_evidence:
        raise ValueError(
            "required evidence missing from frozen chunk manifest"
        )

    content_by_evidence_id: dict[str, str] = {}

    for evidence_id in sorted(
        all_required_evidence_ids
    ):
        chunk = chunks_by_id[evidence_id]
        path = (
            repo_root
            / Path(chunk.content_path)
        )

        content_bytes = path.read_bytes()

        if (
            _sha256_bytes(content_bytes)
            != chunk.content_sha256
        ):
            raise ValueError(
                f"required evidence content hash mismatch: {evidence_id}"
            )

        content_by_evidence_id[evidence_id] = (
            content_bytes.decode("utf-8")
        )

    max_evidence_case = max(
        answerable_cases,
        key=lambda item: len(item[1]),
    )

    context_sizes = tuple(
        (
            case_id,
            _context_characters(
                evidence_ids=evidence_ids,
                content_by_evidence_id=(
                    content_by_evidence_id
                ),
            ),
        )
        for (
            case_id,
            evidence_ids,
            _fact_ids,
        ) in answerable_cases
    )

    max_context_case_id, max_context_chars = max(
        context_sizes,
        key=lambda item: item[1],
    )

    max_fact_case = max(
        answerable_cases,
        key=lambda item: len(item[2]),
    )

    receipt = Phase5SemanticRuntimeAdequacyReceipt(
        answerable_case_count=len(
            answerable_cases
        ),
        refusal_case_count=refusal_count,
        required_evidence_reference_count=sum(
            len(evidence_ids)
            for (
                _case_id_value,
                evidence_ids,
                _fact_ids,
            ) in answerable_cases
        ),
        unique_required_evidence_count=len(
            all_required_evidence_ids
        ),
        minimum_top_k_structural_floor=len(
            max_evidence_case[1]
        ),
        minimum_max_evidence_items_structural_floor=(
            len(max_evidence_case[1])
        ),
        minimum_context_budget_characters_structural_floor=(
            max_context_chars
        ),
        max_required_fact_count=len(
            max_fact_case[2]
        ),
        max_required_evidence_case_id=(
            max_evidence_case[0]
        ),
        max_required_context_case_id=(
            max_context_case_id
        ),
        max_required_fact_case_id=(
            max_fact_case[0]
        ),
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        receipt,
    )

    return (
        receipt,
        receipt_sha256,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    receipt, receipt_sha256 = (
        materialize_phase5_semantic_runtime_adequacy(
            repo_root
        )
    )

    print(
        "PHASE5_SEMANTIC_RUNTIME_ADEQUACY_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )
    print(
        "PHASE5_ANSWERABLE_CASE_COUNT="
        f"{receipt.answerable_case_count}"
    )
    print(
        "PHASE5_REFUSAL_CASE_COUNT="
        f"{receipt.refusal_case_count}"
    )
    print(
        "PHASE5_MIN_TOP_K_STRUCTURAL_FLOOR="
        f"{receipt.minimum_top_k_structural_floor}"
    )
    print(
        "PHASE5_MIN_MAX_EVIDENCE_ITEMS_STRUCTURAL_FLOOR="
        f"{receipt.minimum_max_evidence_items_structural_floor}"
    )
    print(
        "PHASE5_MIN_CONTEXT_BUDGET_CHARACTERS_STRUCTURAL_FLOOR="
        f"{receipt.minimum_context_budget_characters_structural_floor}"
    )
    print(
        "PHASE5_MAX_REQUIRED_CONTEXT_CASE_ID="
        f"{receipt.max_required_context_case_id}"
    )
    print(
        "PHASE5_RETRIEVAL_RANKING_ADEQUACY_MEASURED=false"
    )
    print(
        "PHASE5_SEMANTIC_RUNTIME_CONFIGURATION_SELECTED=false"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED=false"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false"
    )


if __name__ == "__main__":
    main()
