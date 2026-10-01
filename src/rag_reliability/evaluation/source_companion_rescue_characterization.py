"""Single bounded characterization of the Phase 5 source-companion rescue."""

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
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
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
from rag_reliability.evaluation.source_companion_rescue_candidate import (
    CompanionChunkMetadata,
    SourceCompanionRescueCandidate,
)
from rag_reliability.evaluation.source_companion_rescue_protocol import (
    Phase5SourceCompanionRescueProtocolV1,
)
from rag_reliability.evaluation.source_companion_rescue_protocol_freeze import (
    Phase5SourceCompanionRescueProtocolFreezeV1,
)
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_catalog import load_runtime_operation_catalog
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    ResolutionStatus,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_source_companion_rescue_protocol_v1.json"
)
_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_source_companion_rescue_protocol_freeze_v1.json"
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
_CHUNK_MANIFEST_PATH = (
    Path("datasets")
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_source_companion_rescue_characterization_v1.json"
)

_PROTOCOL_SHA256: Literal[
    "885bb5727ecd9e3efd5fa19d520a2545715ddfb45c5d93012779e7fad90b6882"
] = "885bb5727ecd9e3efd5fa19d520a2545715ddfb45c5d93012779e7fad90b6882"

_PROTOCOL_FREEZE_SHA256: Literal[
    "72a9c461e0df2f2a8a72c3561d425bd2c434b3614baf79eecd2e3ade0b3eb90f"
] = "72a9c461e0df2f2a8a72c3561d425bd2c434b3614baf79eecd2e3ade0b3eb90f"

_DEVELOPMENT_REJECTION_SHA256: Literal[
    "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"
] = "21dd3c0e3c824c22232724bf52b5cc420eb41dff61ecc6833c164db24bf0441a"

_FAILURE_LOCALIZATION_SHA256: Literal[
    "5ac9f4b6f7e117a1adf699496ae4d8f3a4e0de7874d597f90c75d8a282cc61d6"
] = "5ac9f4b6f7e117a1adf699496ae4d8f3a4e0de7874d597f90c75d8a282cc61d6"

_PROMOTED_RETRIEVAL_SHA256: Literal[
    "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
] = "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"

_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

_TARGET_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)

CompanionRole = Literal[
    "development",
    "tuning",
]


class CompanionCaseObservation(ContractModel):
    role: Literal["development", "tuning"]
    case_id: NonEmptyStr

    baseline_required_evidence_ranks: tuple[int, ...] = Field(min_length=1)
    candidate_required_evidence_ranks: tuple[int, ...] = Field(min_length=1)

    baseline_full_gold_k20: bool
    candidate_full_gold_k20: bool

    changed_vs_incumbent: bool
    regressed_at_k20: bool
    target_cross_cutting_case: bool
    deterministic_across_repeats: bool

    resolution_status: ResolutionStatus


class Phase5SourceCompanionRescueCharacterizationV1(ContractModel):
    report_version: Literal[
        "phase5-source-companion-rescue-characterization-v1"
    ] = "phase5-source-companion-rescue-characterization-v1"

    run_validity: Literal["VALID"] = "VALID"
    scientific_disposition: Literal[
        "PASS",
        "REJECT",
        "INCONCLUSIVE",
    ]

    protocol_sha256: Sha256 = _PROTOCOL_SHA256
    protocol_freeze_sha256: Sha256 = _PROTOCOL_FREEZE_SHA256
    development_rejection_sha256: Sha256 = _DEVELOPMENT_REJECTION_SHA256
    failure_localization_sha256: Sha256 = _FAILURE_LOCALIZATION_SHA256
    promoted_retrieval_sha256: Sha256 = _PROMOTED_RETRIEVAL_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256

    deterministic_repeat_count: Literal[3] = 3

    development_answerable_case_count: Literal[20] = 20
    tuning_answerable_case_count: Literal[15] = 15

    targeted_cross_cutting_case_count: Literal[2] = 2
    targeted_cross_cutting_cases_recovered_k20: int = Field(ge=0, le=2)

    previously_passing_development_case_count: int = Field(ge=0, le=20)
    development_k20_regression_count: int = Field(ge=0, le=20)
    tuning_k20_regression_count: int = Field(ge=0, le=15)
    nondeterministic_case_count: int = Field(ge=0, le=35)
    changed_case_count: int = Field(ge=0, le=35)

    evaluator_leakage_count: Literal[0] = 0
    provider_call_count: Literal[0] = 0

    observations: tuple[
        CompanionCaseObservation,
        ...,
    ] = Field(min_length=35, max_length=35)

    characterization_passed: bool
    characterization_failures: tuple[NonEmptyStr, ...]

    candidate_implemented: Literal[True] = True
    candidate_executed: Literal[True] = True

    composition_authorized: Literal[False] = False
    composed_candidate_executed: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    provider_invoked: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    baseline_readiness_review_required: Literal[True] = True
    automatic_composition_authorized: Literal[False] = False
    automatic_successor_experiment_authorized: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        case_ids = tuple(
            (item.role, item.case_id)
            for item in self.observations
        )

        if len(case_ids) != len(set(case_ids)):
            raise ValueError(
                "companion characterization case identities must be unique"
            )

        passed = (
            self.targeted_cross_cutting_cases_recovered_k20 == 2
            and self.development_k20_regression_count == 0
            and self.tuning_k20_regression_count == 0
            and self.nondeterministic_case_count == 0
            and self.evaluator_leakage_count == 0
        )

        if self.characterization_passed != passed:
            raise ValueError(
                "companion characterization verdict does not reconcile"
            )

        expected_disposition = "PASS" if passed else "REJECT"

        if self.scientific_disposition != expected_disposition:
            raise ValueError(
                "companion scientific disposition does not reconcile"
            )

        if (
            self.composition_authorized
            or self.composed_candidate_executed
            or self.post_reject_confirmation_inspected
            or self.post_reject_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.runtime_retriever_changed
            or self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError(
                "companion characterization overclaimed downstream state"
            )

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(
    repo_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> bytes:
    path = repo_root / relative_path
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(
            f"frozen artifact hash mismatch: {relative_path}"
        )

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(
            f"frozen artifact sidecar mismatch: {relative_path}"
        )

    return content


def _metadata_map(
    manifest: Phase3dChunkManifest,
) -> dict[str, CompanionChunkMetadata]:
    return {
        chunk.chunk_id: CompanionChunkMetadata(
            evidence_id=chunk.chunk_id,
            chunk_kind=chunk.chunk_kind,
            source_ids=tuple(
                sorted(
                    {
                        parent.source_id
                        for parent in chunk.parents
                    }
                )
            ),
            source_state=chunk.evidence_scope.source_state,
            authority_level=chunk.evidence_scope.authority_level,
        )
        for chunk in manifest.chunks
    }


def _lineage_map(
    manifest: Phase3dChunkManifest,
) -> dict[str, tuple[str, ...]]:
    return {
        chunk.chunk_id: tuple(chunk.linked_operation_ids)
        for chunk in manifest.chunks
    }


def _required_ranks(
    items: tuple[RetrievedEvidence, ...],
    case: EvaluationCase,
) -> tuple[int, ...]:
    by_id = {
        item.evidence_id: item.rank
        for item in items
    }

    ranks: list[int] = []

    for evidence_id in case.required_evidence_ids:
        rank = by_id.get(evidence_id)

        if rank is None:
            raise ValueError(
                f"required evidence absent from full ranking: {evidence_id}"
            )

        ranks.append(rank)

    return tuple(ranks)


def _full_gold_k20(
    ranks: tuple[int, ...],
) -> bool:
    return all(rank <= 20 for rank in ranks)


async def _incumbent_ranking(
    *,
    case: EvaluationCase,
    lexical: LexicalRetriever,
    bm25: _Bm25CandidateRetriever,
    rrf_config: Phase5RrfHybridCandidateConfig,
    resolver: DeterministicOperationResolver,
    lineage: dict[str, tuple[str, ...]],
) -> tuple[
    ResolutionStatus,
    tuple[RetrievedEvidence, ...],
]:
    lexical_items = (
        await lexical.retrieve(
            RetrievalRequest(
                query=case.query,
                top_k=rrf_config.characterization_top_k,
            )
        )
    ).items

    bm25_items = bm25.retrieve(case.query)

    generic_items = _fuse_rankings(
        lexical_items=lexical_items,
        bm25_items=bm25_items,
        config=rrf_config,
    )

    resolution = resolver.resolve(case.query)

    incumbent = stable_partition_by_operation_lineage(
        items=generic_items,
        resolution=resolution,
        linked_operation_ids_by_evidence_id=lineage,
    )

    return resolution.status, incumbent


def _load_localization_target_ids(
    repo_root: Path,
) -> tuple[str, str]:
    payload = json.loads(
        _verified_bytes(
            repo_root,
            _FAILURE_LOCALIZATION_PATH,
            _FAILURE_LOCALIZATION_SHA256,
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "failure localization artifact must be an object"
        )

    raw_cases = payload.get("case_diagnostics")

    if not isinstance(raw_cases, list):
        raise ValueError(
            "failure localization case diagnostics must be an array"
        )

    target_ids = tuple(
        sorted(
            str(item["case_id"])
            for item in raw_cases
            if isinstance(item, dict)
            and item.get("failure_class")
            == "cross_cutting_companion_evidence_miss"
        )
    )

    if target_ids != tuple(sorted(_TARGET_CASE_IDS)):
        raise ValueError(
            "localized cross-cutting target identities drifted"
        )

    return (
        _TARGET_CASE_IDS[0],
        _TARGET_CASE_IDS[1],
    )


async def _build_report(
    repo_root: Path,
) -> Phase5SourceCompanionRescueCharacterizationV1:
    protocol = (
        Phase5SourceCompanionRescueProtocolV1.model_validate_json(
            _verified_bytes(
                repo_root,
                _PROTOCOL_PATH,
                _PROTOCOL_SHA256,
            )
        )
    )

    freeze = (
        Phase5SourceCompanionRescueProtocolFreezeV1.model_validate_json(
            _verified_bytes(
                repo_root,
                _PROTOCOL_FREEZE_PATH,
                _PROTOCOL_FREEZE_SHA256,
            )
        )
    )

    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError(
            "source-companion freeze does not bind expected protocol"
        )

    if protocol.gate.provider_calls_allowed != 0:
        raise ValueError(
            "source-companion protocol unexpectedly allows provider calls"
        )

    if protocol.derivation.parameter_sweep_allowed:
        raise ValueError(
            "source-companion protocol unexpectedly allows parameter sweep"
        )

    _load_localization_target_ids(repo_root)

    development_rejection = (
        Phase5DevelopmentConfirmationReport.model_validate_json(
            _verified_bytes(
                repo_root,
                _DEVELOPMENT_REJECTION_PATH,
                _DEVELOPMENT_REJECTION_SHA256,
            )
        )
    )

    promoted = (
        Phase5OperationAwareRrfCandidateExperimentReport.model_validate_json(
            _verified_bytes(
                repo_root,
                _PROMOTED_RETRIEVAL_PATH,
                _PROMOTED_RETRIEVAL_SHA256,
            )
        )
    )

    if promoted.experiment_decision != "PROMOTE":
        raise ValueError(
            "incumbent operation-aware retrieval is not promoted"
        )

    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            repo_root,
            _CHUNK_MANIFEST_PATH,
            _CHUNK_MANIFEST_SHA256,
        )
    )

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
        raise ValueError(
            "DEVELOPMENT answerable count drifted"
        )

    if len(tuning_cases) != 15:
        raise ValueError(
            "TUNING answerable count drifted"
        )

    documents, _ = _load_indexed_documents(repo_root)

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

    resolver = DeterministicOperationResolver(
        load_runtime_operation_catalog(repo_root)
    )

    lineage = _lineage_map(manifest)

    candidate = SourceCompanionRescueCandidate(
        resolver=resolver,
        metadata_by_evidence_id=_metadata_map(manifest),
    )

    rejection_by_case = {
        item.case_id: item
        for item in development_rejection.case_results
    }

    observations: list[CompanionCaseObservation] = []

    all_cases: tuple[
        tuple[
            CompanionRole,
            EvaluationCase,
        ],
        ...,
    ] = (
        tuple(
            ("development", case)
            for case in development_cases
        )
        + tuple(
            ("tuning", case)
            for case in tuning_cases
        )
    )

    repeat_count = development_rejection.deterministic_repeat_count

    if repeat_count != 3:
        raise ValueError(
            "inherited deterministic repeat count drifted"
        )

    for role, case in all_cases:
        status, incumbent = await _incumbent_ranking(
            case=case,
            lexical=lexical,
            bm25=bm25,
            rrf_config=rrf_config,
            resolver=resolver,
            lineage=lineage,
        )

        baseline_ranks = _required_ranks(
            incumbent,
            case,
        )

        if role == "development":
            recorded = rejection_by_case[case.case_id]
            recorded_ranks = tuple(
                item.raw_rank
                for item in recorded.required_evidence_ranks
            )

            if any(rank is None for rank in recorded_ranks):
                raise ValueError(
                    "DEVELOPMENT incumbent evidence rank unexpectedly missing"
                )

            expected_ranks = tuple(
                int(rank)
                for rank in recorded_ranks
                if rank is not None
            )

            if baseline_ranks != expected_ranks:
                raise ValueError(
                    "DEVELOPMENT incumbent reproduction drifted: "
                    f"{case.case_id}"
                )

        repeats = tuple(
            candidate.rank(
                query=case.query,
                current_ranked_retrieval=incumbent,
            )
            for _ in range(repeat_count)
        )

        first_resolution, first_items = repeats[0]

        deterministic = all(
            repeated_resolution == first_resolution
            and repeated_items == first_items
            for repeated_resolution, repeated_items in repeats[1:]
        )

        if first_resolution.status is not status:
            raise ValueError(
                "candidate resolution drifted from incumbent: "
                f"{case.case_id}"
            )

        candidate_ranks = _required_ranks(
            first_items,
            case,
        )

        baseline_full = _full_gold_k20(
            baseline_ranks
        )
        candidate_full = _full_gold_k20(
            candidate_ranks
        )

        observations.append(
            CompanionCaseObservation(
                role=role,
                case_id=case.case_id,
                baseline_required_evidence_ranks=baseline_ranks,
                candidate_required_evidence_ranks=candidate_ranks,
                baseline_full_gold_k20=baseline_full,
                candidate_full_gold_k20=candidate_full,
                changed_vs_incumbent=(
                    first_items != incumbent
                ),
                regressed_at_k20=(
                    baseline_full
                    and not candidate_full
                ),
                target_cross_cutting_case=(
                    role == "development"
                    and case.case_id in _TARGET_CASE_IDS
                ),
                deterministic_across_repeats=deterministic,
                resolution_status=status,
            )
        )

    typed = tuple(
        sorted(
            observations,
            key=lambda item: (
                item.role,
                item.case_id,
            ),
        )
    )

    target_recovered = sum(
        item.target_cross_cutting_case
        and item.candidate_full_gold_k20
        for item in typed
    )

    development_regressions = sum(
        item.role == "development"
        and item.regressed_at_k20
        for item in typed
    )

    tuning_regressions = sum(
        item.role == "tuning"
        and item.regressed_at_k20
        for item in typed
    )

    nondeterministic = sum(
        not item.deterministic_across_repeats
        for item in typed
    )

    failures: list[str] = []

    if target_recovered != 2:
        failures.append(
            "targeted_cross_cutting_cases_not_both_recovered_at_k20"
        )

    if development_regressions != 0:
        failures.append(
            "previously_passing_development_k20_regression_present"
        )

    if tuning_regressions != 0:
        failures.append(
            "tuning_k20_regression_present"
        )

    if nondeterministic != 0:
        failures.append(
            "fallback_nondeterminism_present"
        )

    disposition: Literal[
        "PASS",
        "REJECT",
        "INCONCLUSIVE",
    ] = "PASS" if not failures else "REJECT"

    return Phase5SourceCompanionRescueCharacterizationV1(
        scientific_disposition=disposition,
        targeted_cross_cutting_cases_recovered_k20=target_recovered,
        previously_passing_development_case_count=sum(
            item.role == "development"
            and item.baseline_full_gold_k20
            for item in typed
        ),
        development_k20_regression_count=development_regressions,
        tuning_k20_regression_count=tuning_regressions,
        nondeterministic_case_count=nondeterministic,
        changed_case_count=sum(
            item.changed_vs_incumbent
            for item in typed
        ),
        observations=typed,
        characterization_passed=not failures,
        characterization_failures=tuple(failures),
    )


def materialize_phase5_source_companion_rescue_characterization(
    repo_root: Path,
) -> tuple[
    Phase5SourceCompanionRescueCharacterizationV1,
    str,
]:
    report = asyncio.run(
        _build_report(repo_root)
    )

    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )

    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    report, digest = (
        materialize_phase5_source_companion_rescue_characterization(
            repo_root
        )
    )

    print(
        "PHASE5_SOURCE_COMPANION_CHARACTERIZATION_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_SOURCE_COMPANION_RUN_VALIDITY="
        f"{report.run_validity}"
    )
    print(
        "PHASE5_SOURCE_COMPANION_SCIENTIFIC_DISPOSITION="
        f"{report.scientific_disposition}"
    )
    print(
        "PHASE5_SOURCE_COMPANION_TARGET_RECOVERY="
        f"{report.targeted_cross_cutting_cases_recovered_k20}/2"
    )
    print(
        "PHASE5_SOURCE_COMPANION_REGRESSIONS="
        f"development:{report.development_k20_regression_count},"
        f"tuning:{report.tuning_k20_regression_count}"
    )
    print(
        "PHASE5_SOURCE_COMPANION_DETERMINISM="
        f"nondeterministic:{report.nondeterministic_case_count}"
    )
    print(
        "PHASE5_SOURCE_COMPANION_CHANGED_CASES="
        f"{report.changed_case_count}"
    )

    for failure in report.characterization_failures:
        print(
            "PHASE5_SOURCE_COMPANION_FAILURE="
            f"{failure}"
        )

    print("PHASE5_COMPOSITION_AUTHORIZED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")


if __name__ == "__main__":
    main()
