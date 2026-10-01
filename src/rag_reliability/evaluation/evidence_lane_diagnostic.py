"""Execute the Phase 5 evidence-lane diagnostic exactly as frozen."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.config.identity import RetrievalConfig
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import RetrievalRequest, RetrievedEvidence
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.evidence_lane_diagnostic_protocol import (
    Phase5EvidenceLaneDiagnosticProtocolV1,
)
from rag_reliability.evaluation.evidence_lane_diagnostic_protocol_freeze import (
    Phase5EvidenceLaneDiagnosticProtocolFreezeV1,
)
from rag_reliability.evaluation.operation_aware_rrf_candidate_experiment import (
    Phase5OperationAwareRrfCandidateExperimentReport,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    _fuse_rankings,
)
from rag_reliability.evaluation.semantic_runtime_development_confirmation import (
    Phase5DevelopmentConfirmationReport,
    _load_development_cases,
)
from rag_reliability.runtime.models import IndexedDocument
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_catalog import (
    load_runtime_operation_catalog,
)
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_evidence_lane_diagnostic_protocol_v1.json"
)
_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_evidence_lane_diagnostic_protocol_freeze_v1.json"
)
_DEVELOPMENT_REJECTION_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_semantic_runtime_development_confirmation_v1.json"
)
_FAILURE_LOCALIZATION_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_post_reject_failure_localization_v1.json"
)
_PROMOTED_RETRIEVAL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_aware_rrf_candidate_experiment_v1.json"
)
_RRF_INCUMBENT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_rrf_hybrid_candidate_experiment_v1.json"
)
_CHUNK_MANIFEST_PATH = (
    Path("datasets")
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)
_OUTPUT_PATH = Path("artifacts") / "development" / "phase5_evidence_lane_diagnostic_v1.json"

_PROTOCOL_SHA256 = "b7b82810e224af452eaa9d8c23b4db8330857c2b1acc01eedbecc429bc458992"
_PROTOCOL_FREEZE_SHA256 = "80a1fd5fa970d3bd1d8a8ada8d77eed1f25349c95769d7f1932d81d47c237081"
_DEVELOPMENT_REJECTION_SHA256 = "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
_FAILURE_LOCALIZATION_SHA256 = "5ac9f4b6f7e117a1adf699496ae4d8f3a4e0de7874d597f90c75d8a282cc61d6"
_PROMOTED_RETRIEVAL_SHA256 = "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
_RRF_INCUMBENT_SHA256 = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
_CHUNK_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

_FAILED_DEVELOPMENT_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-repos-accept-invitation-current",
    "phase4-dev-repos-accept-invitation-success",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)
_AUTHORED_FAILURE_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)
_OPERATION_CORE_FAILURE_CASE_IDS = (
    "phase4-dev-repos-accept-invitation-current",
    "phase4-dev-repos-accept-invitation-success",
)

DiagnosticRole = Literal["development", "tuning"]


class EvidenceLaneEvidenceObservation(ContractModel):
    evidence_id: NonEmptyStr
    chunk_kind: ChunkKind
    global_bm25_rank: int | None = Field(default=None, ge=1)
    global_incumbent_rank: int | None = Field(default=None, ge=1)
    native_lane_bm25_rank: int | None = Field(default=None, ge=1)
    global_to_native_lane_rank_delta: int | None = None


class EvidenceLaneCaseObservation(ContractModel):
    role: DiagnosticRole
    case_id: NonEmptyStr
    evidence: tuple[EvidenceLaneEvidenceObservation, ...] = Field(min_length=1)
    full_gold_global_incumbent_k20: bool
    full_gold_native_lane_k20: bool
    deterministic_across_repeats: bool
    previously_failed_development_case: bool


class Phase5EvidenceLaneDiagnosticV1(ContractModel):
    report_version: Literal[
        "phase5-evidence-lane-diagnostic-v1"
    ] = "phase5-evidence-lane-diagnostic-v1"
    evidence_class: Literal["diagnostic_only"] = "diagnostic_only"
    run_validity: Literal["VALID"] = "VALID"

    protocol_sha256: Sha256 = _PROTOCOL_SHA256
    protocol_freeze_sha256: Sha256 = _PROTOCOL_FREEZE_SHA256
    development_rejection_sha256: Sha256 = _DEVELOPMENT_REJECTION_SHA256
    failure_localization_sha256: Sha256 = _FAILURE_LOCALIZATION_SHA256
    promoted_retrieval_sha256: Sha256 = _PROMOTED_RETRIEVAL_SHA256
    rrf_incumbent_sha256: Sha256 = _RRF_INCUMBENT_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    deterministic_repeat_count: Literal[3] = 3
    authored_lane_chunk_count: Literal[26] = 26
    operation_core_lane_chunk_count: Literal[504] = 504
    component_lane_chunk_count: Literal[803] = 803

    development_answerable_case_count: Literal[20] = 20
    tuning_answerable_case_count: Literal[15] = 15
    failed_development_case_count: Literal[4] = 4

    failed_development_native_lane_recovered_count: int = Field(ge=0, le=4)
    authored_failure_native_lane_recovered_count: int = Field(ge=0, le=2)
    operation_core_failure_native_lane_recovered_count: int = Field(ge=0, le=2)
    nondeterministic_case_count: int = Field(ge=0, le=35)

    stratified_retrieval_candidate_hypothesis_supported: bool
    authored_granularity_review_supported: bool
    operation_representation_review_supported: bool

    observations: tuple[EvidenceLaneCaseObservation, ...] = Field(min_length=35, max_length=35)

    diagnostic_implemented: Literal[True] = True
    diagnostic_executed: Literal[True] = True
    runtime_retriever_changed: Literal[False] = False
    corpus_mutated: Literal[False] = False
    chunking_policy_changed: Literal[False] = False
    candidate_implemented: Literal[False] = False
    candidate_executed: Literal[False] = False
    composition_authorized: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False
    baseline_readiness_review_required: Literal[True] = True
    automatic_candidate_implementation_authorized: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        identities = tuple((item.role, item.case_id) for item in self.observations)
        if len(identities) != len(set(identities)):
            raise ValueError("evidence-lane diagnostic case identities must be unique")

        failed = tuple(
            item
            for item in self.observations
            if item.role == "development" and item.previously_failed_development_case
        )
        if len(failed) != 4:
            raise ValueError("evidence-lane diagnostic must retain four failed DEVELOPMENT cases")

        authored = tuple(
            item
            for item in failed
            if item.case_id in _AUTHORED_FAILURE_CASE_IDS
        )
        operation = tuple(
            item
            for item in failed
            if item.case_id in _OPERATION_CORE_FAILURE_CASE_IDS
        )
        recovered = sum(item.full_gold_native_lane_k20 for item in failed)

        if self.failed_development_native_lane_recovered_count != recovered:
            raise ValueError("failed-case native-lane recovery count does not reconcile")
        if self.authored_failure_native_lane_recovered_count != sum(
            item.full_gold_native_lane_k20 for item in authored
        ):
            raise ValueError("authored native-lane recovery count does not reconcile")
        if self.operation_core_failure_native_lane_recovered_count != sum(
            item.full_gold_native_lane_k20 for item in operation
        ):
            raise ValueError("operation-core native-lane recovery count does not reconcile")
        if self.stratified_retrieval_candidate_hypothesis_supported != (recovered == 4):
            raise ValueError("stratified-retrieval support flag does not reconcile")
        if self.authored_granularity_review_supported != any(
            not item.full_gold_native_lane_k20 for item in authored
        ):
            raise ValueError("authored-granularity review flag does not reconcile")
        if self.operation_representation_review_supported != any(
            not item.full_gold_native_lane_k20 for item in operation
        ):
            raise ValueError("operation-representation review flag does not reconcile")

        forbidden = (
            self.runtime_retriever_changed
            or self.corpus_mutated
            or self.chunking_policy_changed
            or self.candidate_implemented
            or self.candidate_executed
            or self.composition_authorized
            or self.post_reject_confirmation_inspected
            or self.post_reject_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
            or self.automatic_candidate_implementation_authorized
        )
        if forbidden:
            raise ValueError("evidence-lane diagnostic overclaimed downstream state")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(repo_root: Path, relative_path: Path, expected_sha256: str) -> bytes:
    path = repo_root / relative_path
    content = path.read_bytes()
    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {relative_path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"
    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(f"frozen artifact sidecar mismatch: {relative_path}")
    return content


def _load_manifest(repo_root: Path) -> Phase3dChunkManifest:
    return Phase3dChunkManifest.model_validate_json(
        _verified_bytes(repo_root, _CHUNK_MANIFEST_PATH, _CHUNK_MANIFEST_SHA256)
    )


def _partition_documents_by_lane(
    *,
    documents: tuple[IndexedDocument, ...],
    manifest: Phase3dChunkManifest,
) -> dict[ChunkKind, tuple[IndexedDocument, ...]]:
    kind_by_id = {chunk.chunk_id: chunk.chunk_kind for chunk in manifest.chunks}

    if set(kind_by_id) != {item.evidence_id for item in documents}:
        raise ValueError("indexed corpus and chunk manifest evidence identities differ")

    lanes = {
        kind: tuple(item for item in documents if kind_by_id[item.evidence_id] is kind)
        for kind in ChunkKind
    }
    expected_counts = {
        ChunkKind.AUTHORED_SECTION: 26,
        ChunkKind.OPENAPI_OPERATION_CORE: 504,
        ChunkKind.OPENAPI_COMPONENT: 803,
    }
    if {kind: len(items) for kind, items in lanes.items()} != expected_counts:
        raise ValueError("evidence-lane corpus counts drifted")
    return lanes


def _lineage_map(manifest: Phase3dChunkManifest) -> dict[str, tuple[str, ...]]:
    return {chunk.chunk_id: tuple(chunk.linked_operation_ids) for chunk in manifest.chunks}


def _rank_by_id(items: tuple[RetrievedEvidence, ...]) -> dict[str, int]:
    return {item.evidence_id: item.rank for item in items}


def _full_gold_k20(ranks: tuple[int | None, ...]) -> bool:
    return all(rank is not None and rank <= 20 for rank in ranks)


def _localization_bm25_expectations(repo_root: Path) -> dict[str, dict[str, int]]:
    payload = json.loads(
        _verified_bytes(
            repo_root,
            _FAILURE_LOCALIZATION_PATH,
            _FAILURE_LOCALIZATION_SHA256,
        )
    )
    if not isinstance(payload, dict):
        raise ValueError("failure localization artifact must be an object")
    raw_cases = payload.get("case_diagnostics")
    if not isinstance(raw_cases, list):
        raise ValueError("failure localization diagnostics must be an array")

    result: dict[str, dict[str, int]] = {}
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("failure localization diagnostic must be an object")
        case_id = raw_case.get("case_id")
        if case_id not in _FAILED_DEVELOPMENT_CASE_IDS:
            continue
        raw_evidence = raw_case.get("evidence")
        if not isinstance(raw_evidence, list):
            raise ValueError("failure localization evidence must be an array")
        ranks: dict[str, int] = {}
        for raw_item in raw_evidence:
            if not isinstance(raw_item, dict):
                raise ValueError("failure localization evidence item must be an object")
            evidence_id = raw_item.get("evidence_id")
            bm25_rank = raw_item.get("bm25_rank")
            if not isinstance(evidence_id, str) or not isinstance(bm25_rank, int):
                raise ValueError("failure localization BM25 rank is incomplete")
            ranks[evidence_id] = bm25_rank
        result[str(case_id)] = ranks

    if set(result) != set(_FAILED_DEVELOPMENT_CASE_IDS):
        raise ValueError("failure localization does not cover expected failed cases")
    return result


async def _global_incumbent_once(
    *,
    query: str,
    lexical: LexicalRetriever,
    bm25: _Bm25CandidateRetriever,
    rrf_config: Phase5RrfHybridCandidateConfig,
    resolver: DeterministicOperationResolver,
    lineage: dict[str, tuple[str, ...]],
) -> tuple[RetrievedEvidence, ...]:
    lexical_items = (
        await lexical.retrieve(
            RetrievalRequest(query=query, top_k=rrf_config.characterization_top_k)
        )
    ).items
    bm25_items = bm25.retrieve(query)
    generic = _fuse_rankings(
        lexical_items=lexical_items,
        bm25_items=bm25_items,
        config=rrf_config,
    )
    resolution = resolver.resolve(query)
    return stable_partition_by_operation_lineage(
        items=generic,
        resolution=resolution,
        linked_operation_ids_by_evidence_id=lineage,
    )


async def _build_report(repo_root: Path) -> Phase5EvidenceLaneDiagnosticV1:
    protocol = Phase5EvidenceLaneDiagnosticProtocolV1.model_validate_json(
        _verified_bytes(repo_root, _PROTOCOL_PATH, _PROTOCOL_SHA256)
    )
    freeze = Phase5EvidenceLaneDiagnosticProtocolFreezeV1.model_validate_json(
        _verified_bytes(repo_root, _PROTOCOL_FREEZE_PATH, _PROTOCOL_FREEZE_SHA256)
    )
    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("evidence-lane freeze does not bind expected protocol")
    if protocol.measurement.parameter_sweep_allowed:
        raise ValueError("evidence-lane protocol unexpectedly allows a parameter sweep")
    if protocol.boundary.lane_selected_from_gold:
        raise ValueError("evidence-lane protocol unexpectedly allows gold-selected routing")

    development_rejection = Phase5DevelopmentConfirmationReport.model_validate_json(
        _verified_bytes(
            repo_root,
            _DEVELOPMENT_REJECTION_PATH,
            _DEVELOPMENT_REJECTION_SHA256,
        )
    )
    promoted = Phase5OperationAwareRrfCandidateExperimentReport.model_validate_json(
        _verified_bytes(
            repo_root,
            _PROMOTED_RETRIEVAL_PATH,
            _PROMOTED_RETRIEVAL_SHA256,
        )
    )
    _verified_bytes(repo_root, _RRF_INCUMBENT_PATH, _RRF_INCUMBENT_SHA256)
    if promoted.experiment_decision != "PROMOTE":
        raise ValueError("operation-aware incumbent is not the promoted retrieval candidate")

    manifest = _load_manifest(repo_root)
    documents, _evidence_ids = _load_indexed_documents(repo_root)
    lanes = _partition_documents_by_lane(documents=documents, manifest=manifest)

    bm25_config = Phase5Bm25CandidateConfig()
    global_bm25 = _Bm25CandidateRetriever(config=bm25_config, documents=documents)
    lane_bm25 = {
        kind: _Bm25CandidateRetriever(config=bm25_config, documents=lane_documents)
        for kind, lane_documents in lanes.items()
    }

    rrf_config = Phase5RrfHybridCandidateConfig()
    lexical = LexicalRetriever(
        config=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=rrf_config.characterization_top_k,
        ),
        documents=documents,
    )
    resolver = DeterministicOperationResolver(load_runtime_operation_catalog(repo_root))
    lineage = _lineage_map(manifest)
    kind_by_evidence_id = {chunk.chunk_id: chunk.chunk_kind for chunk in manifest.chunks}

    development_cases = tuple(
        case
        for case in _load_development_cases(repo_root)
        if case.expected_response_mode is not ResponseMode.REFUSE
    )
    tuning_cases = tuple(
        case
        for case in _load_tuning_cases(repo_root)
        if case.expected_response_mode is not ResponseMode.REFUSE
    )
    if len(development_cases) != 20:
        raise ValueError("DEVELOPMENT answerable count drifted")
    if len(tuning_cases) != 15:
        raise ValueError("TUNING answerable count drifted")

    development_recorded = {
        item.case_id: item for item in development_rejection.case_results
    }
    localization_bm25 = _localization_bm25_expectations(repo_root)
    repeat_count = protocol.measurement.deterministic_repeat_count

    cases: tuple[tuple[DiagnosticRole, EvaluationCase], ...] = (
        tuple(("development", case) for case in development_cases)
        + tuple(("tuning", case) for case in tuning_cases)
    )

    observations: list[EvidenceLaneCaseObservation] = []

    for role, case in cases:
        global_bm25_repeats = tuple(
            global_bm25.retrieve(case.query) for _ in range(repeat_count)
        )

        lane_repeats = tuple(
            {
                kind: lane_bm25[kind].retrieve(case.query)
                for kind in ChunkKind
            }
            for _ in range(repeat_count)
        )

        incumbent_repeats = tuple(
            [
                await _global_incumbent_once(
                    query=case.query,
                    lexical=lexical,
                    bm25=global_bm25,
                    rrf_config=rrf_config,
                    resolver=resolver,
                    lineage=lineage,
                )
                for _ in range(repeat_count)
            ]
        )

        deterministic = (
            all(items == global_bm25_repeats[0] for items in global_bm25_repeats[1:])
            and all(lane_set == lane_repeats[0] for lane_set in lane_repeats[1:])
            and all(items == incumbent_repeats[0] for items in incumbent_repeats[1:])
        )

        global_bm25_ranks = _rank_by_id(global_bm25_repeats[0])
        global_incumbent_ranks = _rank_by_id(incumbent_repeats[0])
        native_lane_rank_maps = {
            kind: _rank_by_id(lane_repeats[0][kind]) for kind in ChunkKind
        }

        if role == "development":
            recorded = development_recorded[case.case_id]
            recorded_ranks = {
                item.evidence_id: item.raw_rank
                for item in recorded.required_evidence_ranks
            }
            for evidence_id in case.required_evidence_ids:
                if global_incumbent_ranks.get(evidence_id) != recorded_ranks.get(evidence_id):
                    raise ValueError(
                        f"DEVELOPMENT incumbent reproduction drifted: {case.case_id}"
                    )

        if role == "development" and case.case_id in _FAILED_DEVELOPMENT_CASE_IDS:
            expected_bm25 = localization_bm25[case.case_id]
            for evidence_id in case.required_evidence_ids:
                if global_bm25_ranks.get(evidence_id) != expected_bm25.get(evidence_id):
                    raise ValueError(
                        f"failed-case global BM25 reproduction drifted: {case.case_id}"
                    )

        evidence_observations: list[EvidenceLaneEvidenceObservation] = []

        # Evaluator-owned required evidence is consulted only after global and
        # all three lane rankings have already been materialized above.
        for evidence_id in case.required_evidence_ids:
            chunk_kind = kind_by_evidence_id[evidence_id]
            global_rank = global_bm25_ranks.get(evidence_id)
            native_rank = native_lane_rank_maps[chunk_kind].get(evidence_id)
            delta = None
            if global_rank is not None and native_rank is not None:
                delta = global_rank - native_rank

            evidence_observations.append(
                EvidenceLaneEvidenceObservation(
                    evidence_id=evidence_id,
                    chunk_kind=chunk_kind,
                    global_bm25_rank=global_rank,
                    global_incumbent_rank=global_incumbent_ranks.get(evidence_id),
                    native_lane_bm25_rank=native_rank,
                    global_to_native_lane_rank_delta=delta,
                )
            )

        typed_evidence = tuple(evidence_observations)
        observations.append(
            EvidenceLaneCaseObservation(
                role=role,
                case_id=case.case_id,
                evidence=typed_evidence,
                full_gold_global_incumbent_k20=_full_gold_k20(
                    tuple(item.global_incumbent_rank for item in typed_evidence)
                ),
                full_gold_native_lane_k20=_full_gold_k20(
                    tuple(item.native_lane_bm25_rank for item in typed_evidence)
                ),
                deterministic_across_repeats=deterministic,
                previously_failed_development_case=(
                    role == "development"
                    and case.case_id in _FAILED_DEVELOPMENT_CASE_IDS
                ),
            )
        )

    typed_observations = tuple(
        sorted(observations, key=lambda item: (item.role, item.case_id))
    )
    failed = tuple(
        item
        for item in typed_observations
        if item.role == "development" and item.previously_failed_development_case
    )
    authored = tuple(
        item for item in failed if item.case_id in _AUTHORED_FAILURE_CASE_IDS
    )
    operation = tuple(
        item for item in failed if item.case_id in _OPERATION_CORE_FAILURE_CASE_IDS
    )
    recovered = sum(item.full_gold_native_lane_k20 for item in failed)

    return Phase5EvidenceLaneDiagnosticV1(
        failed_development_native_lane_recovered_count=recovered,
        authored_failure_native_lane_recovered_count=sum(
            item.full_gold_native_lane_k20 for item in authored
        ),
        operation_core_failure_native_lane_recovered_count=sum(
            item.full_gold_native_lane_k20 for item in operation
        ),
        nondeterministic_case_count=sum(
            not item.deterministic_across_repeats for item in typed_observations
        ),
        stratified_retrieval_candidate_hypothesis_supported=(recovered == 4),
        authored_granularity_review_supported=any(
            not item.full_gold_native_lane_k20 for item in authored
        ),
        operation_representation_review_supported=any(
            not item.full_gold_native_lane_k20 for item in operation
        ),
        observations=typed_observations,
    )


def materialize_phase5_evidence_lane_diagnostic(
    repo_root: Path,
) -> tuple[Phase5EvidenceLaneDiagnosticV1, str]:
    report = asyncio.run(_build_report(repo_root))
    digest = write_json_with_sha256(repo_root / _OUTPUT_PATH, report)
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_evidence_lane_diagnostic(repo_root)

    print(f"PHASE5_EVIDENCE_LANE_DIAGNOSTIC_SHA256={digest}")
    print(f"PHASE5_EVIDENCE_LANE_RUN_VALIDITY={report.run_validity}")
    print(
        "PHASE5_EVIDENCE_LANE_FAILED_CASE_RECOVERY="
        f"{report.failed_development_native_lane_recovered_count}/4"
    )
    print(
        "PHASE5_EVIDENCE_LANE_AUTHORED_RECOVERY="
        f"{report.authored_failure_native_lane_recovered_count}/2"
    )
    print(
        "PHASE5_EVIDENCE_LANE_OPERATION_CORE_RECOVERY="
        f"{report.operation_core_failure_native_lane_recovered_count}/2"
    )
    print(
        "PHASE5_EVIDENCE_LANE_NONDETERMINISM="
        f"{report.nondeterministic_case_count}"
    )
    print(
        "PHASE5_EVIDENCE_LANE_STRATIFIED_RETRIEVAL_SUPPORTED="
        f"{str(report.stratified_retrieval_candidate_hypothesis_supported).lower()}"
    )
    print(
        "PHASE5_EVIDENCE_LANE_AUTHORED_GRANULARITY_REVIEW="
        f"{str(report.authored_granularity_review_supported).lower()}"
    )
    print(
        "PHASE5_EVIDENCE_LANE_OPERATION_REPRESENTATION_REVIEW="
        f"{str(report.operation_representation_review_supported).lower()}"
    )

    for observation in report.observations:
        if not observation.previously_failed_development_case:
            continue
        native = ",".join(
            f"{item.chunk_kind.value}:{item.native_lane_bm25_rank}"
            for item in observation.evidence
        )
        print(
            "PHASE5_EVIDENCE_LANE_FAILED_CASE="
            f"{observation.case_id},"
            f"native:{native},"
            f"full_gold_k20:{str(observation.full_gold_native_lane_k20).lower()}"
        )

    print("PHASE5_RUNTIME_RETRIEVER_CHANGED=false")
    print("PHASE5_CORPUS_MUTATED=false")
    print("PHASE5_CANDIDATE_IMPLEMENTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")


if __name__ == "__main__":
    main()
