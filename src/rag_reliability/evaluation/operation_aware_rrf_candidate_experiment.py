"""Execute the single frozen Phase 5 operation-aware RRF candidate.

The candidate is evaluation-only and TUNING-only. It reconstructs the frozen
RRF incumbent, resolves operation identity from query-only runtime input, then
stable-partitions the incumbent ranking by exact Phase 3D linked-operation
lineage. Evaluator gold is used only after candidate ranking for measurement.
"""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import RetrievalConfig, SourcePolicyConfig
from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.runtime import (
    RetrievalRequest,
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.operation_aware_rrf_protocol import (
    Phase5OperationAwareRrfProtocolV1,
)
from rag_reliability.evaluation.operation_aware_rrf_protocol_freeze import (
    Phase5OperationAwareRrfProtocolFreezeReceipt,
)
from rag_reliability.evaluation.operation_resolver_characterization import (
    Phase5OperationResolverCharacterizationReport,
)
from rag_reliability.evaluation.retrieval_characterization import (
    Phase5TopKCurvePoint,
    _context_prefix_characters,
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    Phase5RrfHybridCandidateExperimentReport,
    _fuse_rankings,
)
from rag_reliability.runtime.filtering import (
    CurrentGithubRestSourcePolicyFilter,
)
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_catalog import (
    load_runtime_operation_catalog,
)
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    OperationResolution,
    ResolutionStatus,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

_PROTOCOL_PATH = Path("artifacts") / "development" / "phase5_operation_aware_rrf_protocol_v1.json"
_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_operation_aware_rrf_protocol_freeze_v1.json"
)
_INCUMBENT_PATH = (
    Path("artifacts") / "development" / "phase5_rrf_hybrid_candidate_experiment_v1.json"
)
_RESOLVER_CHARACTERIZATION_PATH = (
    Path("artifacts") / "development" / "phase5_operation_resolver_characterization_v2.json"
)
_CHUNK_MANIFEST_PATH = Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
_OUTPUT_PATH = (
    Path("artifacts") / "development" / "phase5_operation_aware_rrf_candidate_experiment_v1.json"
)

_PROTOCOL_SHA256: Literal["d1ddc3cf8920f72612dbddef410d17260ca3b07e9a5d7d380bb8f4cfa3f7cb95"] = (
    "d1ddc3cf8920f72612dbddef410d17260ca3b07e9a5d7d380bb8f4cfa3f7cb95"
)

_FREEZE_SHA256: Literal["47fcbeacc808168bfd94f399b59b54c88aa4e16d3a7eaa55e8dc6ae4487caa98"] = (
    "47fcbeacc808168bfd94f399b59b54c88aa4e16d3a7eaa55e8dc6ae4487caa98"
)

_INCUMBENT_SHA256: Literal["b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"] = (
    "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
)

_RESOLVER_CHARACTERIZATION_SHA256: Literal[
    "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
] = "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"

_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

_TOP_K_CURVE: tuple[int, ...] = (
    2,
    3,
    5,
    10,
    20,
    50,
    100,
    200,
    500,
    1333,
)

_DECISION_PROMOTE: Literal["PROMOTE"] = "PROMOTE"
_DECISION_REJECT: Literal["REJECT"] = "REJECT"
_DECISION_STOP: Literal["STOP_AND_REFRAME"] = "STOP_AND_REFRAME"

ExperimentDecision = Literal[
    "PROMOTE",
    "REJECT",
    "STOP_AND_REFRAME",
]

RankOutcome = Literal[
    "improved",
    "unchanged",
    "regressed",
    "unretrievable",
]


class Phase5OperationAwareRequiredEvidenceRank(ContractModel):
    """Incumbent and candidate rank for one evaluator-owned gold evidence ID."""

    evidence_id: NonEmptyStr
    incumbent_raw_rank: int | None = Field(default=None, ge=1)
    candidate_raw_rank: int | None = Field(default=None, ge=1)
    candidate_eligible_rank: int | None = Field(default=None, ge=1)
    candidate_survived_source_filter: bool

    @model_validator(mode="after")
    def validate_rank_boundary(self) -> Self:
        if self.candidate_eligible_rank is not None and self.candidate_raw_rank is None:
            raise ValueError("eligible evidence cannot exist without candidate raw rank")

        if self.candidate_survived_source_filter != (self.candidate_eligible_rank is not None):
            raise ValueError("candidate source-filter survival does not reconcile")

        return self


class Phase5OperationAwareCaseComparison(ContractModel):
    """One answerable TUNING case measured after candidate ranking."""

    case_id: NonEmptyStr
    resolution_status: ResolutionStatus
    resolved_operation_id: NonEmptyStr | None = None
    promoted_item_count: int = Field(ge=0)

    incumbent_minimum_raw_top_k: int = Field(ge=1)
    incumbent_minimum_eligible_items: int = Field(ge=1)
    incumbent_context_prefix_characters: int = Field(ge=1)

    candidate_minimum_raw_top_k: int | None = Field(default=None, ge=1)
    candidate_minimum_eligible_items: int | None = Field(default=None, ge=1)
    candidate_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    required_evidence_ranks: tuple[
        Phase5OperationAwareRequiredEvidenceRank,
        ...,
    ] = Field(min_length=1)

    full_gold_retrievable: bool
    full_gold_filter_eligible: bool
    fallback_order_preserved: bool | None = None
    deterministic_across_repeats: bool

    rank_outcome_vs_incumbent: RankOutcome
    full_gold_k20_regression: bool

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if self.resolution_status is ResolutionStatus.RESOLVED:
            if self.resolved_operation_id is None:
                raise ValueError("resolved case requires one resolved operation ID")
            if self.fallback_order_preserved is not None:
                raise ValueError("resolved case cannot carry fallback-order verdict")
        else:
            if self.resolved_operation_id is not None:
                raise ValueError("non-resolved case cannot carry resolved operation ID")
            if self.promoted_item_count != 0:
                raise ValueError("fallback case cannot promote operation lineage")
            if self.fallback_order_preserved is None:
                raise ValueError("fallback case requires exact-order verdict")

        if self.full_gold_retrievable != (self.candidate_minimum_raw_top_k is not None):
            raise ValueError("candidate raw rank does not reconcile")

        if self.full_gold_filter_eligible != (
            self.candidate_minimum_eligible_items is not None
            and self.candidate_context_prefix_characters is not None
        ):
            raise ValueError("candidate eligible/context state does not reconcile")

        candidate_raw = self.candidate_minimum_raw_top_k
        if candidate_raw is None:
            expected: RankOutcome = "unretrievable"
        elif candidate_raw < self.incumbent_minimum_raw_top_k:
            expected = "improved"
        elif candidate_raw == self.incumbent_minimum_raw_top_k:
            expected = "unchanged"
        else:
            expected = "regressed"

        if self.rank_outcome_vs_incumbent != expected:
            raise ValueError("candidate/incumbent rank outcome does not reconcile")

        incumbent_k20 = self.incumbent_minimum_raw_top_k <= 20
        candidate_k20 = candidate_raw is not None and candidate_raw <= 20
        if self.full_gold_k20_regression != (incumbent_k20 and not candidate_k20):
            raise ValueError("k20 regression verdict does not reconcile")

        return self


class Phase5OperationAwareRrfCandidateExperimentReport(ContractModel):
    """TUNING-only evidence for the one frozen operation-aware RRF candidate."""

    report_version: Literal["phase5-operation-aware-rrf-candidate-experiment-v1"] = (
        "phase5-operation-aware-rrf-candidate-experiment-v1"
    )

    evidence_class: Literal["intervention_tuning_only"] = "intervention_tuning_only"

    protocol_sha256: Literal["d1ddc3cf8920f72612dbddef410d17260ca3b07e9a5d7d380bb8f4cfa3f7cb95"] = (
        _PROTOCOL_SHA256
    )

    protocol_freeze_receipt_sha256: Literal[
        "47fcbeacc808168bfd94f399b59b54c88aa4e16d3a7eaa55e8dc6ae4487caa98"
    ] = _FREEZE_SHA256

    incumbent_rrf_sha256: Literal[
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    ] = _INCUMBENT_SHA256

    resolver_characterization_sha256: Literal[
        "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
    ] = _RESOLVER_CHARACTERIZATION_SHA256

    candidate_id: Literal["phase5-operation-aware-rrf-stable-partition-v1"] = (
        "phase5-operation-aware-rrf-stable-partition-v1"
    )

    answerable_case_count: Literal[15] = 15
    required_evidence_reference_count: Literal[18] = 18
    deterministic_repeat_count: Literal[3] = 3

    resolved_case_count: int = Field(ge=0, le=15)
    ambiguous_case_count: int = Field(ge=0, le=15)
    unresolved_case_count: int = Field(ge=0, le=15)

    candidate_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    candidate_maximum_minimum_raw_top_k: int | None = Field(default=None, ge=1)
    candidate_maximum_minimum_eligible_items: int | None = Field(
        default=None,
        ge=1,
    )
    candidate_maximum_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    improved_vs_incumbent_case_count: int = Field(ge=0, le=15)
    unchanged_vs_incumbent_case_count: int = Field(ge=0, le=15)
    regressed_vs_incumbent_case_count: int = Field(ge=0, le=15)
    unretrievable_case_count: int = Field(ge=0, le=15)
    filter_ineligible_case_count: int = Field(ge=0, le=15)

    full_gold_k20_regression_count: int = Field(ge=0, le=15)
    fallback_order_mismatch_count: int = Field(ge=0, le=15)
    nondeterministic_case_count: int = Field(ge=0, le=15)

    case_comparisons: tuple[
        Phase5OperationAwareCaseComparison,
        ...,
    ] = Field(min_length=15, max_length=15)

    promotion_gate_passed: bool
    promotion_gate_failures: tuple[NonEmptyStr, ...]
    experiment_decision: ExperimentDecision

    evaluator_fields_passed_to_candidate: Literal[False] = False
    development_gold_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False

    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_capacity_gate_satisfied: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    semantic_runtime_promotion_authorized: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if (
            self.resolved_case_count + self.ambiguous_case_count + self.unresolved_case_count
            != self.answerable_case_count
        ):
            raise ValueError("resolver status counts do not reconcile")

        if (
            self.improved_vs_incumbent_case_count
            + self.unchanged_vs_incumbent_case_count
            + self.regressed_vs_incumbent_case_count
            + self.unretrievable_case_count
            != self.answerable_case_count
        ):
            raise ValueError("candidate rank-outcome counts do not reconcile")

        if tuple(point.top_k for point in self.candidate_top_k_curve) != _TOP_K_CURVE:
            raise ValueError("candidate top-k curve drifted")

        if self.promotion_gate_passed != (len(self.promotion_gate_failures) == 0):
            raise ValueError("promotion-gate verdict does not reconcile")

        integrity_failure = (
            self.fallback_order_mismatch_count > 0
            or self.nondeterministic_case_count > 0
            or self.evaluator_fields_passed_to_candidate
        )

        if integrity_failure:
            expected_decision: ExperimentDecision = _DECISION_STOP
        elif self.promotion_gate_passed:
            expected_decision = _DECISION_PROMOTE
        else:
            expected_decision = _DECISION_REJECT

        if self.experiment_decision != expected_decision:
            raise ValueError("experiment decision does not reconcile")

        if (
            self.development_gold_used
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.runtime_retriever_changed
            or self.retrieval_configuration_selected
            or self.semantic_runtime_capacity_gate_satisfied
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.semantic_runtime_promotion_authorized
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("candidate experiment overclaimed execution state")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(path: Path, expected_sha256: str) -> bytes:
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise ValueError(f"frozen artifact sidecar mismatch: {path}")

    return content


def _load_controls(
    repo_root: Path,
) -> tuple[
    Phase5OperationAwareRrfProtocolV1,
    Phase5OperationAwareRrfProtocolFreezeReceipt,
    Phase5RrfHybridCandidateExperimentReport,
    Phase5OperationResolverCharacterizationReport,
    Phase3dChunkManifest,
]:
    protocol = Phase5OperationAwareRrfProtocolV1.model_validate_json(
        _verified_bytes(repo_root / _PROTOCOL_PATH, _PROTOCOL_SHA256)
    )
    freeze = Phase5OperationAwareRrfProtocolFreezeReceipt.model_validate_json(
        _verified_bytes(repo_root / _FREEZE_PATH, _FREEZE_SHA256)
    )
    incumbent = Phase5RrfHybridCandidateExperimentReport.model_validate_json(
        _verified_bytes(repo_root / _INCUMBENT_PATH, _INCUMBENT_SHA256)
    )
    resolver_characterization = Phase5OperationResolverCharacterizationReport.model_validate_json(
        _verified_bytes(
            repo_root / _RESOLVER_CHARACTERIZATION_PATH,
            _RESOLVER_CHARACTERIZATION_SHA256,
        )
    )
    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            repo_root / _CHUNK_MANIFEST_PATH,
            _CHUNK_MANIFEST_SHA256,
        )
    )

    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("Slice 2 freeze does not bind the expected protocol")

    if protocol.rrf_incumbent_sha256 != _INCUMBENT_SHA256:
        raise ValueError("Slice 2 protocol does not bind the expected RRF incumbent")

    if not resolver_characterization.acceptance_passed:
        raise ValueError("operation resolver characterization is not accepted")

    return (
        protocol,
        freeze,
        incumbent,
        resolver_characterization,
        manifest,
    )


def _lineage_map(
    manifest: Phase3dChunkManifest,
) -> dict[str, tuple[str, ...]]:
    return {chunk.chunk_id: tuple(chunk.linked_operation_ids) for chunk in manifest.chunks}


def _curve(
    comparisons: tuple[Phase5OperationAwareCaseComparison, ...],
) -> tuple[Phase5TopKCurvePoint, ...]:
    reference_count = sum(len(comparison.required_evidence_ranks) for comparison in comparisons)

    points: list[Phase5TopKCurvePoint] = []

    for top_k in _TOP_K_CURVE:
        full_case_count = 0
        retrieved_reference_count = 0

        for comparison in comparisons:
            ranks = tuple(item.candidate_raw_rank for item in comparison.required_evidence_ranks)

            retrieved_reference_count += sum(rank is not None and rank <= top_k for rank in ranks)

            if all(rank is not None and rank <= top_k for rank in ranks):
                full_case_count += 1

        points.append(
            Phase5TopKCurvePoint(
                top_k=top_k,
                applicable_case_count=len(comparisons),
                full_gold_case_count=full_case_count,
                full_gold_case_rate=full_case_count / len(comparisons),
                required_evidence_reference_count=reference_count,
                retrieved_required_evidence_count=retrieved_reference_count,
                micro_gold_recall=retrieved_reference_count / reference_count,
            )
        )

    return tuple(points)


def _gate_failures(
    *,
    candidate_curve: tuple[Phase5TopKCurvePoint, ...],
    maximum_raw_top_k: int | None,
    maximum_eligible_items: int | None,
    maximum_context_prefix: int | None,
    unretrievable_case_count: int,
    filter_ineligible_case_count: int,
    full_gold_k20_regression_count: int,
    fallback_order_mismatch_count: int,
    nondeterministic_case_count: int,
) -> tuple[str, ...]:
    point_20 = next(point for point in candidate_curve if point.top_k == 20)
    failures: list[str] = []

    if point_20.full_gold_case_count != 15:
        failures.append("full_gold_cases_at_k20_below_15")

    if abs(point_20.micro_gold_recall - 1.0) > 1e-12:
        failures.append("micro_gold_recall_at_k20_below_1")

    if maximum_raw_top_k is None or maximum_raw_top_k > 20:
        failures.append("maximum_raw_top_k_above_20")

    if maximum_eligible_items is None or maximum_eligible_items > 20:
        failures.append("maximum_eligible_items_above_20")

    if maximum_context_prefix is None or maximum_context_prefix > 102463:
        failures.append("maximum_context_prefix_worse_than_rrf_incumbent")

    if unretrievable_case_count != 0:
        failures.append("unretrievable_gold_present")

    if filter_ineligible_case_count != 0:
        failures.append("filter_ineligible_gold_present")

    if full_gold_k20_regression_count != 0:
        failures.append("incumbent_full_gold_k20_regression_present")

    if fallback_order_mismatch_count != 0:
        failures.append("generic_rrf_fallback_order_mismatch")

    if nondeterministic_case_count != 0:
        failures.append("candidate_nondeterminism_present")

    return tuple(failures)


def _candidate_repeats(
    *,
    query: str,
    generic_items: tuple[RetrievedEvidence, ...],
    resolver: DeterministicOperationResolver,
    lineage_by_evidence_id: dict[str, tuple[str, ...]],
) -> tuple[
    tuple[OperationResolution, tuple[RetrievedEvidence, ...]],
    ...,
]:
    outputs: list[tuple[OperationResolution, tuple[RetrievedEvidence, ...]]] = []

    for _ in range(3):
        resolution = resolver.resolve(query)
        ranked = stable_partition_by_operation_lineage(
            items=generic_items,
            resolution=resolution,
            linked_operation_ids_by_evidence_id=lineage_by_evidence_id,
        )
        outputs.append((resolution, ranked))

    return tuple(outputs)


async def _build_report(
    repo_root: Path,
) -> Phase5OperationAwareRrfCandidateExperimentReport:
    (
        protocol,
        _freeze,
        incumbent,
        _resolver_characterization,
        manifest,
    ) = _load_controls(repo_root)

    cases = _load_tuning_cases(repo_root)
    documents, _evidence_ids = _load_indexed_documents(repo_root)

    answerable_cases = {
        case.case_id: case
        for case in cases
        if case.expected_response_mode is not ResponseMode.REFUSE
    }

    if len(answerable_cases) != 15:
        raise ValueError("operation-aware experiment requires 15 answerable TUNING cases")

    incumbent_cases = {comparison.case_id: comparison for comparison in incumbent.case_comparisons}

    if set(answerable_cases) != set(incumbent_cases):
        raise ValueError("candidate and incumbent answerable case identities differ")

    config = Phase5RrfHybridCandidateConfig()

    lexical_retriever = LexicalRetriever(
        config=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=config.characterization_top_k,
        ),
        documents=documents,
    )

    bm25_retriever = _Bm25CandidateRetriever(
        config=Phase5Bm25CandidateConfig(),
        documents=documents,
    )

    source_filter = CurrentGithubRestSourcePolicyFilter(
        config=SourcePolicyConfig(policy_id="github-rest-current-v1")
    )

    resolver = DeterministicOperationResolver(load_runtime_operation_catalog(repo_root))
    lineage_by_evidence_id = _lineage_map(manifest)

    comparisons: list[Phase5OperationAwareCaseComparison] = []

    for case_id in sorted(answerable_cases):
        case = answerable_cases[case_id]
        incumbent_case = incumbent_cases[case_id]

        incumbent_raw = incumbent_case.hybrid_minimum_raw_top_k
        incumbent_eligible = incumbent_case.hybrid_minimum_eligible_items
        incumbent_context = incumbent_case.hybrid_context_prefix_characters

        if incumbent_raw is None or incumbent_eligible is None or incumbent_context is None:
            raise ValueError(f"incumbent case lacks complete floors: {case_id}")

        lexical_items = (
            await lexical_retriever.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=config.characterization_top_k,
                )
            )
        ).items

        bm25_items = bm25_retriever.retrieve(case.query)

        generic_items = _fuse_rankings(
            lexical_items=lexical_items,
            bm25_items=bm25_items,
            config=config,
        )

        generic_filtered = await source_filter.apply(SourceFilterRequest(candidates=generic_items))
        generic_raw_by_id = {item.evidence_id: item.rank for item in generic_items}
        generic_eligible_by_id = {
            item.evidence_id: index for index, item in enumerate(generic_filtered.eligible, start=1)
        }

        incumbent_rank_by_id = {
            item.evidence_id: item for item in incumbent_case.hybrid_required_evidence_ranks
        }

        for evidence_id in case.required_evidence_ids:
            incumbent_rank = incumbent_rank_by_id[evidence_id]
            if generic_raw_by_id.get(evidence_id) != incumbent_rank.raw_rank:
                raise ValueError(f"recomputed RRF raw rank drifted: {case_id}")
            if generic_eligible_by_id.get(evidence_id) != incumbent_rank.eligible_rank:
                raise ValueError(f"recomputed RRF eligible rank drifted: {case_id}")

        repeat_outputs = _candidate_repeats(
            query=case.query,
            generic_items=generic_items,
            resolver=resolver,
            lineage_by_evidence_id=lineage_by_evidence_id,
        )

        resolution = repeat_outputs[0][0]
        candidate_items = repeat_outputs[0][1]

        deterministic = all(
            repeated_resolution == resolution and repeated_items == candidate_items
            for repeated_resolution, repeated_items in repeat_outputs
        )

        generic_scores = {item.evidence_id: item.score for item in generic_items}
        candidate_scores = {item.evidence_id: item.score for item in candidate_items}

        if generic_scores != candidate_scores:
            raise ValueError("operation-aware candidate changed RRF score values")

        fallback_order_preserved: bool | None = None
        resolved_operation_id: str | None = None
        promoted_item_count = 0

        if resolution.status is ResolutionStatus.RESOLVED:
            resolved_operation_id = resolution.operation_ids[0]
            promoted_item_count = sum(
                resolved_operation_id in lineage_by_evidence_id.get(item.evidence_id, ())
                for item in generic_items
            )
        else:
            fallback_order_preserved = candidate_items == generic_items

        filtered = await source_filter.apply(SourceFilterRequest(candidates=candidate_items))

        candidate_raw_by_id = {item.evidence_id: item.rank for item in candidate_items}
        candidate_eligible_by_id = {
            item.evidence_id: index for index, item in enumerate(filtered.eligible, start=1)
        }

        rank_records = tuple(
            Phase5OperationAwareRequiredEvidenceRank(
                evidence_id=evidence_id,
                incumbent_raw_rank=incumbent_rank_by_id[evidence_id].raw_rank,
                candidate_raw_rank=candidate_raw_by_id.get(evidence_id),
                candidate_eligible_rank=candidate_eligible_by_id.get(evidence_id),
                candidate_survived_source_filter=(evidence_id in candidate_eligible_by_id),
            )
            for evidence_id in case.required_evidence_ids
        )

        full_retrievable = all(item.candidate_raw_rank is not None for item in rank_records)
        full_filter_eligible = all(
            item.candidate_eligible_rank is not None for item in rank_records
        )

        candidate_raw: int | None = None
        if full_retrievable:
            candidate_raw = max(cast(int, item.candidate_raw_rank) for item in rank_records)

        candidate_eligible: int | None = None
        candidate_context: int | None = None
        if full_filter_eligible:
            candidate_eligible = max(
                cast(int, item.candidate_eligible_rank) for item in rank_records
            )
            candidate_context = _context_prefix_characters(
                cast(tuple[object, ...], filtered.eligible),
                candidate_eligible,
            )

        if candidate_raw is None:
            rank_outcome: RankOutcome = "unretrievable"
        elif candidate_raw < incumbent_raw:
            rank_outcome = "improved"
        elif candidate_raw == incumbent_raw:
            rank_outcome = "unchanged"
        else:
            rank_outcome = "regressed"

        incumbent_k20 = incumbent_raw <= 20
        candidate_k20 = candidate_raw is not None and candidate_raw <= 20

        comparisons.append(
            Phase5OperationAwareCaseComparison(
                case_id=case_id,
                resolution_status=resolution.status,
                resolved_operation_id=resolved_operation_id,
                promoted_item_count=promoted_item_count,
                incumbent_minimum_raw_top_k=incumbent_raw,
                incumbent_minimum_eligible_items=incumbent_eligible,
                incumbent_context_prefix_characters=incumbent_context,
                candidate_minimum_raw_top_k=candidate_raw,
                candidate_minimum_eligible_items=candidate_eligible,
                candidate_context_prefix_characters=candidate_context,
                required_evidence_ranks=rank_records,
                full_gold_retrievable=full_retrievable,
                full_gold_filter_eligible=full_filter_eligible,
                fallback_order_preserved=fallback_order_preserved,
                deterministic_across_repeats=deterministic,
                rank_outcome_vs_incumbent=rank_outcome,
                full_gold_k20_regression=incumbent_k20 and not candidate_k20,
            )
        )

    typed_comparisons = tuple(comparisons)

    all_retrievable = all(comparison.full_gold_retrievable for comparison in typed_comparisons)
    all_filter_eligible = all(
        comparison.full_gold_filter_eligible for comparison in typed_comparisons
    )

    maximum_raw: int | None = None
    if all_retrievable:
        maximum_raw = max(
            cast(int, comparison.candidate_minimum_raw_top_k) for comparison in typed_comparisons
        )

    maximum_eligible: int | None = None
    maximum_context: int | None = None
    if all_filter_eligible:
        maximum_eligible = max(
            cast(int, comparison.candidate_minimum_eligible_items)
            for comparison in typed_comparisons
        )
        maximum_context = max(
            cast(int, comparison.candidate_context_prefix_characters)
            for comparison in typed_comparisons
        )

    candidate_curve = _curve(typed_comparisons)

    unretrievable_count = sum(
        not comparison.full_gold_retrievable for comparison in typed_comparisons
    )
    filter_ineligible_count = sum(
        not comparison.full_gold_filter_eligible for comparison in typed_comparisons
    )
    k20_regression_count = sum(
        comparison.full_gold_k20_regression for comparison in typed_comparisons
    )
    fallback_mismatch_count = sum(
        comparison.fallback_order_preserved is False for comparison in typed_comparisons
    )
    nondeterministic_count = sum(
        not comparison.deterministic_across_repeats for comparison in typed_comparisons
    )

    failures = _gate_failures(
        candidate_curve=candidate_curve,
        maximum_raw_top_k=maximum_raw,
        maximum_eligible_items=maximum_eligible,
        maximum_context_prefix=maximum_context,
        unretrievable_case_count=unretrievable_count,
        filter_ineligible_case_count=filter_ineligible_count,
        full_gold_k20_regression_count=k20_regression_count,
        fallback_order_mismatch_count=fallback_mismatch_count,
        nondeterministic_case_count=nondeterministic_count,
    )

    integrity_failure = fallback_mismatch_count > 0 or nondeterministic_count > 0

    if integrity_failure:
        decision: ExperimentDecision = _DECISION_STOP
    elif failures:
        decision = _DECISION_REJECT
    else:
        decision = _DECISION_PROMOTE

    return Phase5OperationAwareRrfCandidateExperimentReport(
        resolved_case_count=sum(
            comparison.resolution_status is ResolutionStatus.RESOLVED
            for comparison in typed_comparisons
        ),
        ambiguous_case_count=sum(
            comparison.resolution_status is ResolutionStatus.AMBIGUOUS
            for comparison in typed_comparisons
        ),
        unresolved_case_count=sum(
            comparison.resolution_status is ResolutionStatus.UNRESOLVED
            for comparison in typed_comparisons
        ),
        candidate_top_k_curve=candidate_curve,
        candidate_maximum_minimum_raw_top_k=maximum_raw,
        candidate_maximum_minimum_eligible_items=maximum_eligible,
        candidate_maximum_context_prefix_characters=maximum_context,
        improved_vs_incumbent_case_count=sum(
            comparison.rank_outcome_vs_incumbent == "improved" for comparison in typed_comparisons
        ),
        unchanged_vs_incumbent_case_count=sum(
            comparison.rank_outcome_vs_incumbent == "unchanged" for comparison in typed_comparisons
        ),
        regressed_vs_incumbent_case_count=sum(
            comparison.rank_outcome_vs_incumbent == "regressed" for comparison in typed_comparisons
        ),
        unretrievable_case_count=unretrievable_count,
        filter_ineligible_case_count=filter_ineligible_count,
        full_gold_k20_regression_count=k20_regression_count,
        fallback_order_mismatch_count=fallback_mismatch_count,
        nondeterministic_case_count=nondeterministic_count,
        case_comparisons=typed_comparisons,
        promotion_gate_passed=len(failures) == 0,
        promotion_gate_failures=failures,
        experiment_decision=decision,
    )


def materialize_phase5_operation_aware_rrf_candidate_experiment(
    repo_root: Path,
) -> tuple[
    Phase5OperationAwareRrfCandidateExperimentReport,
    str,
]:
    """Materialize the single frozen operation-aware RRF candidate result."""

    report = asyncio.run(_build_report(repo_root))

    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )

    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_operation_aware_rrf_candidate_experiment(repo_root)

    point_20 = next(point for point in report.candidate_top_k_curve if point.top_k == 20)

    print(f"PHASE5_OPERATION_AWARE_RRF_EXPERIMENT_SHA256={digest}")
    print(
        "PHASE5_OPERATION_AWARE_RRF_RESOLUTION_COUNTS="
        f"resolved:{report.resolved_case_count},"
        f"ambiguous:{report.ambiguous_case_count},"
        f"unresolved:{report.unresolved_case_count}"
    )
    print(
        "PHASE5_OPERATION_AWARE_RRF_K20="
        f"full_gold:{point_20.full_gold_case_count}/15,"
        f"micro:{point_20.micro_gold_recall:.6f}"
    )
    print(
        "PHASE5_OPERATION_AWARE_RRF_MAXIMA="
        f"raw:{report.candidate_maximum_minimum_raw_top_k},"
        f"eligible:{report.candidate_maximum_minimum_eligible_items},"
        f"context:{report.candidate_maximum_context_prefix_characters}"
    )
    print(
        "PHASE5_OPERATION_AWARE_RRF_CASE_OUTCOMES="
        f"improved:{report.improved_vs_incumbent_case_count},"
        f"unchanged:{report.unchanged_vs_incumbent_case_count},"
        f"regressed:{report.regressed_vs_incumbent_case_count},"
        f"unretrievable:{report.unretrievable_case_count}"
    )
    print(
        "PHASE5_OPERATION_AWARE_RRF_INTEGRITY="
        f"k20_regressions:{report.full_gold_k20_regression_count},"
        f"fallback_mismatches:{report.fallback_order_mismatch_count},"
        f"nondeterministic:{report.nondeterministic_case_count}"
    )
    print(
        "PHASE5_OPERATION_AWARE_RRF_PROMOTION_GATE_PASSED="
        f"{str(report.promotion_gate_passed).lower()}"
    )

    for failure in report.promotion_gate_failures:
        print(f"PHASE5_OPERATION_AWARE_RRF_GATE_FAILURE={failure}")

    print(f"PHASE5_OPERATION_AWARE_RRF_DECISION={report.experiment_decision}")
    print("PHASE5_RETRIEVAL_CONFIGURATION_SELECTED=false")
    print("PHASE5_SEMANTIC_RUNTIME_CAPACITY_GATE_SATISFIED=false")
    print("PHASE5_SEMANTIC_RUNTIME_CONFIGURATION_FROZEN=false")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false")


if __name__ == "__main__":
    main()
