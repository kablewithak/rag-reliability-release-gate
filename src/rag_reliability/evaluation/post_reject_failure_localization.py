"""Localize the four rejected DEVELOPMENT retrieval failures.

This is a diagnostic-only artifact. DEVELOPMENT has already been marked spent
for future independent confirmation. The harness reproduces lexical, BM25,
generic RRF, resolver, and operation-aware ranks for only the failed cases.
It does not execute or select a new candidate.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.config.identity import RetrievalConfig
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import RetrievalRequest, RetrievedEvidence
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    _fuse_rankings,
)
from rag_reliability.evaluation.semantic_runtime_development_confirmation import (
    Phase5DevelopmentConfirmationReport,
)
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_catalog import (
    load_runtime_operation_catalog,
)
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    ResolutionStatus,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

_ACTIVATION_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_localization_activation_v1.json"
)
_REJECTION_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_development_confirmation_v1.json"
)
_DEVELOPMENT_PATH = Path("artifacts") / "development" / "phase4c_development_cases_v1.json"
_CONFIRMATION_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_confirmation_freeze_v1.json"
)
_MANIFEST_PATH = Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
_OUTPUT_PATH = Path("artifacts") / "development" / "phase5_post_reject_failure_localization_v1.json"

_ACTIVATION_SHA256: Literal["37ddd7d8659bd1e6542c5e4c15e1fdd9b626eb8e316b0a784866089df9192613"] = (
    "37ddd7d8659bd1e6542c5e4c15e1fdd9b626eb8e316b0a784866089df9192613"
)

_REJECTION_SHA256: Literal["21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"] = (
    "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
)

_DEVELOPMENT_SHA256: Literal["53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"] = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)

_CONFIRMATION_FREEZE_SHA256: Literal[
    "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"
] = "3eece77dd80a5ebfac8c91c486db5c4444fa87224f46bf644ddc9bd9d5275ce2"

_MANIFEST_SHA256: Literal["1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"] = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

FailureClass = Literal[
    "cross_cutting_companion_evidence_miss",
    "operation_core_unresolved_fallback_miss",
]


class FailureEvidenceDiagnostic(ContractModel):
    evidence_id: NonEmptyStr
    required: Literal[True] = True

    candidate_rank: int = Field(ge=1)
    generic_rrf_rank: int = Field(ge=1)
    lexical_rank: int | None = Field(default=None, ge=1)
    bm25_rank: int | None = Field(default=None, ge=1)

    generic_rrf_score: float = Field(ge=0.0)
    lexical_score: float | None = Field(default=None, ge=0.0)
    bm25_score: float | None = Field(default=None, ge=0.0)

    chunk_kind: NonEmptyStr
    byte_count: int = Field(ge=1)
    linked_operation_ids: tuple[NonEmptyStr, ...]
    source_ids: tuple[NonEmptyStr, ...] = Field(min_length=1)

    missed_top20: bool

    @model_validator(mode="after")
    def validate_ranks(self) -> Self:
        if self.missed_top20 != (self.candidate_rank > 20):
            raise ValueError("top-20 miss verdict does not reconcile")
        return self


class FailureCaseDiagnostic(ContractModel):
    case_id: NonEmptyStr
    source_family: NonEmptyStr
    scenario_class: NonEmptyStr
    query: NonEmptyStr

    resolution_status: ResolutionStatus
    resolved_operation_id: NonEmptyStr | None = None
    gold_operation_ids: tuple[NonEmptyStr, ...]
    gold_operation_in_runtime_catalog: bool

    required_evidence_count: int = Field(ge=1)
    missed_required_evidence_count: int = Field(ge=1)

    evidence: tuple[FailureEvidenceDiagnostic, ...] = Field(min_length=1)

    generic_fallback_exact: bool
    failure_class: FailureClass

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if len(self.evidence) != self.required_evidence_count:
            raise ValueError("required evidence count does not reconcile")

        observed_misses = sum(item.missed_top20 for item in self.evidence)
        if observed_misses != self.missed_required_evidence_count:
            raise ValueError("miss count does not reconcile")

        if self.resolution_status is ResolutionStatus.RESOLVED:
            if self.resolved_operation_id is None:
                raise ValueError("resolved case requires operation ID")
        elif self.resolved_operation_id is not None:
            raise ValueError("non-resolved case cannot carry operation ID")

        if not self.generic_fallback_exact:
            raise ValueError("rejected failure should preserve exact fallback")

        return self


class Phase5PostRejectFailureLocalizationReportV1(ContractModel):
    report_version: Literal["phase5-post-reject-failure-localization-v1"] = (
        "phase5-post-reject-failure-localization-v1"
    )

    evidence_role: Literal["development_diagnostic_only_spent_for_future_confirmation"] = (
        "development_diagnostic_only_spent_for_future_confirmation"
    )

    activation_sha256: Sha256 = _ACTIVATION_SHA256
    development_rejection_sha256: Sha256 = _REJECTION_SHA256
    fresh_confirmation_freeze_sha256: Sha256 = _CONFIRMATION_FREEZE_SHA256

    failure_case_count: Literal[4] = 4
    unique_missing_evidence_count: int = Field(ge=1)
    unresolved_failure_case_count: int = Field(ge=0, le=4)
    resolved_failure_case_count: int = Field(ge=0, le=4)

    cross_cutting_failure_case_count: int = Field(ge=0, le=4)
    operation_core_failure_case_count: int = Field(ge=0, le=4)

    repeated_missing_evidence_case_count: int = Field(ge=0, le=4)

    case_diagnostics: tuple[
        FailureCaseDiagnostic,
        ...,
    ] = Field(min_length=4, max_length=4)

    development_spent_for_future_confirmation: Literal[True] = True
    failure_specific_development_evidence_opened: Literal[True] = True
    failure_specific_case_ids_opened: Literal[True] = True
    failure_specific_gold_opened: Literal[True] = True

    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    candidate_retuning_performed: Literal[False] = False
    parameter_sweep_performed: Literal[False] = False
    new_candidate_executed: Literal[False] = False
    next_intervention_selected: Literal[False] = False

    provider_invoked: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if (
            self.unresolved_failure_case_count + self.resolved_failure_case_count
            != self.failure_case_count
        ):
            raise ValueError("resolver failure counts do not reconcile")

        if (
            self.cross_cutting_failure_case_count + self.operation_core_failure_case_count
            != self.failure_case_count
        ):
            raise ValueError("failure-class counts do not reconcile")

        if (
            self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.candidate_retuning_performed
            or self.parameter_sweep_performed
            or self.new_candidate_executed
            or self.next_intervention_selected
            or self.provider_invoked
            or self.semantic_runtime_configuration_selected
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("localization report overclaimed downstream work")

        return self


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verified_bytes(
    repo_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> bytes:
    path = repo_root / relative_path
    content = path.read_bytes()

    if hashlib.sha256(content).hexdigest() != expected_sha256:
        raise ValueError(f"artifact hash mismatch: {relative_path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"
    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(f"artifact sidecar mismatch: {relative_path}")

    return content


def _load_development_cases(
    repo_root: Path,
) -> dict[str, EvaluationCase]:
    payload = json.loads(
        _verified_bytes(
            repo_root,
            _DEVELOPMENT_PATH,
            _DEVELOPMENT_SHA256,
        )
    )
    if not isinstance(payload, dict):
        raise ValueError("DEVELOPMENT suite must be an object")

    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("DEVELOPMENT suite requires records")

    cases: dict[str, EvaluationCase] = {}
    for raw_record in records:
        if not isinstance(raw_record, dict):
            raise ValueError("DEVELOPMENT record must be an object")
        raw_case = raw_record.get("case")
        if not isinstance(raw_case, dict):
            raise ValueError("DEVELOPMENT record requires case")
        case = EvaluationCase.model_validate(raw_case)
        cases[case.case_id] = case

    return cases


def _rank_map(
    items: tuple[RetrievedEvidence, ...],
) -> dict[str, RetrievedEvidence]:
    return {item.evidence_id: item for item in items}


def _lineage_map(
    manifest: Phase3dChunkManifest,
) -> dict[str, tuple[str, ...]]:
    return {chunk.chunk_id: tuple(chunk.linked_operation_ids) for chunk in manifest.chunks}


async def _build_report(
    repo_root: Path,
) -> Phase5PostRejectFailureLocalizationReportV1:
    activation = json.loads(
        _verified_bytes(
            repo_root,
            _ACTIVATION_PATH,
            _ACTIVATION_SHA256,
        )
    )
    if not isinstance(activation, dict):
        raise ValueError("activation receipt must be an object")
    if activation.get("failure_localization_started") is not True:
        raise ValueError("failure localization is not activated")
    if activation.get("development_spent_for_future_confirmation") is not True:
        raise ValueError("DEVELOPMENT has not been marked spent")

    _verified_bytes(
        repo_root,
        _CONFIRMATION_FREEZE_PATH,
        _CONFIRMATION_FREEZE_SHA256,
    )

    rejection = Phase5DevelopmentConfirmationReport.model_validate_json(
        _verified_bytes(
            repo_root,
            _REJECTION_PATH,
            _REJECTION_SHA256,
        )
    )

    failed = tuple(
        item for item in rejection.case_results if not item.full_gold_retrievable_within_top20
    )
    if len(failed) != 4:
        raise ValueError("expected exactly four rejected DEVELOPMENT cases")

    cases = _load_development_cases(repo_root)
    documents, _ids = _load_indexed_documents(repo_root)

    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            repo_root,
            _MANIFEST_PATH,
            _MANIFEST_SHA256,
        )
    )

    chunk_by_id = {chunk.chunk_id: chunk for chunk in manifest.chunks}
    lineage = _lineage_map(manifest)

    catalog = load_runtime_operation_catalog(repo_root)
    catalog_ids = {operation.operation_id for operation in catalog}
    resolver = DeterministicOperationResolver(catalog)

    rrf_config = Phase5RrfHybridCandidateConfig()
    lexical = LexicalRetriever(
        config=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=rrf_config.characterization_top_k,
        ),
        documents=documents,
    )
    bm25 = _Bm25CandidateRetriever(
        config=Phase5Bm25CandidateConfig(),
        documents=documents,
    )

    diagnostics: list[FailureCaseDiagnostic] = []

    for failed_case in sorted(failed, key=lambda item: item.case_id):
        case = cases[failed_case.case_id]
        runtime_input = case.to_runtime_input()

        lexical_items = (
            await lexical.retrieve(
                RetrievalRequest(
                    query=runtime_input.query,
                    top_k=rrf_config.characterization_top_k,
                )
            )
        ).items
        bm25_items = bm25.retrieve(runtime_input.query)
        generic_rrf = _fuse_rankings(
            lexical_items=lexical_items,
            bm25_items=bm25_items,
            config=rrf_config,
        )

        resolution = resolver.resolve(runtime_input.query)
        candidate = stable_partition_by_operation_lineage(
            items=generic_rrf,
            resolution=resolution,
            linked_operation_ids_by_evidence_id=lineage,
        )

        if resolution.status is not ResolutionStatus.RESOLVED:
            generic_fallback_exact = candidate == generic_rrf
        else:
            generic_fallback_exact = True

        lexical_by_id = _rank_map(lexical_items)
        bm25_by_id = _rank_map(bm25_items)
        rrf_by_id = _rank_map(generic_rrf)
        candidate_by_id = _rank_map(candidate)

        evidence_diagnostics: list[FailureEvidenceDiagnostic] = []

        for evidence_id in case.required_evidence_ids:
            chunk = chunk_by_id[evidence_id]
            candidate_item = candidate_by_id[evidence_id]
            rrf_item = rrf_by_id[evidence_id]
            lexical_item = lexical_by_id.get(evidence_id)
            bm25_item = bm25_by_id.get(evidence_id)

            evidence_diagnostics.append(
                FailureEvidenceDiagnostic(
                    evidence_id=evidence_id,
                    candidate_rank=candidate_item.rank,
                    generic_rrf_rank=rrf_item.rank,
                    lexical_rank=(lexical_item.rank if lexical_item is not None else None),
                    bm25_rank=(bm25_item.rank if bm25_item is not None else None),
                    generic_rrf_score=rrf_item.score,
                    lexical_score=(lexical_item.score if lexical_item is not None else None),
                    bm25_score=(bm25_item.score if bm25_item is not None else None),
                    chunk_kind=str(chunk.chunk_kind),
                    byte_count=chunk.byte_count,
                    linked_operation_ids=tuple(chunk.linked_operation_ids),
                    source_ids=tuple(sorted({parent.source_id for parent in chunk.parents})),
                    missed_top20=candidate_item.rank > 20,
                )
            )

        artifact_rank_by_id = {
            item.evidence_id: item.raw_rank for item in failed_case.required_evidence_ranks
        }
        for item in evidence_diagnostics:
            if artifact_rank_by_id[item.evidence_id] != item.candidate_rank:
                raise ValueError(f"recomputed candidate rank drifted: {case.case_id}")

        gold_operation_ids = tuple(
            sorted(
                {
                    operation_id
                    for item in evidence_diagnostics
                    for operation_id in item.linked_operation_ids
                }
            )
        )

        operation_core_case = bool(gold_operation_ids)
        failure_class: FailureClass
        if operation_core_case:
            failure_class = "operation_core_unresolved_fallback_miss"
        else:
            failure_class = "cross_cutting_companion_evidence_miss"

        diagnostics.append(
            FailureCaseDiagnostic(
                case_id=case.case_id,
                source_family=str(case.source_family),
                scenario_class=str(case.scenario_class),
                query=case.query,
                resolution_status=resolution.status,
                resolved_operation_id=(
                    resolution.operation_ids[0]
                    if resolution.status is ResolutionStatus.RESOLVED
                    else None
                ),
                gold_operation_ids=gold_operation_ids,
                gold_operation_in_runtime_catalog=(
                    bool(gold_operation_ids)
                    and all(operation_id in catalog_ids for operation_id in gold_operation_ids)
                ),
                required_evidence_count=len(case.required_evidence_ids),
                missed_required_evidence_count=sum(
                    item.missed_top20 for item in evidence_diagnostics
                ),
                evidence=tuple(evidence_diagnostics),
                generic_fallback_exact=generic_fallback_exact,
                failure_class=failure_class,
            )
        )

    typed = tuple(diagnostics)
    missing_ids = [
        item.evidence_id for case in typed for item in case.evidence if item.missed_top20
    ]
    counts = Counter(missing_ids)

    return Phase5PostRejectFailureLocalizationReportV1(
        unique_missing_evidence_count=len(set(missing_ids)),
        unresolved_failure_case_count=sum(
            case.resolution_status is ResolutionStatus.UNRESOLVED for case in typed
        ),
        resolved_failure_case_count=sum(
            case.resolution_status is ResolutionStatus.RESOLVED for case in typed
        ),
        cross_cutting_failure_case_count=sum(
            case.failure_class == "cross_cutting_companion_evidence_miss" for case in typed
        ),
        operation_core_failure_case_count=sum(
            case.failure_class == "operation_core_unresolved_fallback_miss" for case in typed
        ),
        repeated_missing_evidence_case_count=sum(count for count in counts.values() if count > 1),
        case_diagnostics=typed,
    )


def materialize_phase5_post_reject_failure_localization(
    repo_root: Path,
) -> tuple[Phase5PostRejectFailureLocalizationReportV1, str]:
    report = asyncio.run(_build_report(repo_root))
    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_post_reject_failure_localization(repo_root)

    print(f"PHASE5_FAILURE_LOCALIZATION_SHA256={digest}")
    print(
        "PHASE5_FAILURE_LOCALIZATION_COUNTS="
        f"cases:{report.failure_case_count},"
        f"unique_missing:{report.unique_missing_evidence_count},"
        f"unresolved:{report.unresolved_failure_case_count},"
        f"resolved:{report.resolved_failure_case_count},"
        f"cross_cutting:{report.cross_cutting_failure_case_count},"
        f"operation_core:{report.operation_core_failure_case_count}"
    )

    for case in report.case_diagnostics:
        print(
            "PHASE5_FAILURE_CASE="
            f"{case.case_id}|resolver:{case.resolution_status}|"
            f"class:{case.failure_class}"
        )
        for item in case.evidence:
            print(
                "PHASE5_FAILURE_EVIDENCE="
                f"{case.case_id}|{item.evidence_id}|"
                f"candidate:{item.candidate_rank}|"
                f"lexical:{item.lexical_rank}|"
                f"bm25:{item.bm25_rank}|"
                f"rrf:{item.generic_rrf_rank}|"
                f"missed20:{str(item.missed_top20).lower()}"
            )

    print("PHASE5_DEVELOPMENT_SPENT_FOR_FUTURE_CONFIRMATION=true")
    print("PHASE5_FAILURE_SPECIFIC_DEVELOPMENT_EVIDENCE_OPENED=true")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_NEW_CANDIDATE_EXECUTED=false")
    print("PHASE5_NEXT_INTERVENTION_SELECTED=false")
    print("PHASE5_B0_EXECUTED=false")


if __name__ == "__main__":
    main()
