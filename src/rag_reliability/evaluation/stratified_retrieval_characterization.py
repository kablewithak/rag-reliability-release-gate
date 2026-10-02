"""Characterize the single frozen Phase 5 stratified retrieval candidate."""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import (
    ContextConfig,
    RetrievalConfig,
    SourcePolicyConfig,
)
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import (
    ContextBuildRequest,
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.corpus.chunking import ChunkKind
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.evidence_lane_diagnostic import (
    _global_incumbent_once,
    _lineage_map,
    _load_manifest,
    _partition_documents_by_lane,
)
from rag_reliability.evaluation.retrieval_characterization import (
    Phase5TopKCurvePoint,
    _context_prefix_characters,
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
)
from rag_reliability.evaluation.semantic_runtime_development_confirmation import (
    _load_development_cases,
)
from rag_reliability.evaluation.stratified_retrieval_candidate import (
    IncumbentPreservingStratifiedRrfRanker,
)
from rag_reliability.evaluation.stratified_retrieval_candidate_protocol import (
    Phase5StratifiedRetrievalCandidateProtocolV1,
)
from rag_reliability.evaluation.stratified_retrieval_candidate_protocol_freeze import (
    Phase5StratifiedRetrievalCandidateProtocolFreezeV1,
)
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import ContextBudgetExhaustedError
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.operation_catalog import load_runtime_operation_catalog
from rag_reliability.runtime.operation_resolution import DeterministicOperationResolver
from rag_reliability.runtime.retrieval import LexicalRetriever

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_stratified_retrieval_candidate_protocol_v1.json"
)
_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_stratified_retrieval_candidate_protocol_freeze_v1.json"
)
_EVIDENCE_LANE_DIAGNOSTIC_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_evidence_lane_diagnostic_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_stratified_retrieval_characterization_v1.json"
)

_PROTOCOL_SHA256: Sha256 = (
    "1439cbbd96eaf3e3ee4de48634969745c90e9ce62ba31855409b667f9721f009"
)
_PROTOCOL_FREEZE_SHA256: Sha256 = (
    "311a514388bf748d00389019a6247654ac0eece3f7281d4c0a9cf2b0c1df2d47"
)
_EVIDENCE_LANE_DIAGNOSTIC_SHA256: Sha256 = (
    "bd3aa5893b7447fb91cf586dd2f2568e18fe6915d162bf2f04e43fad2c433b8e"
)
_CHUNK_MANIFEST_SHA256: Sha256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)
_DEVELOPMENT_SHA256: Sha256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SHA256: Sha256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)

_FAILED_DEVELOPMENT_CASE_IDS = (
    "phase4-dev-breaking-version-migration",
    "phase4-dev-repos-accept-invitation-current",
    "phase4-dev-repos-accept-invitation-success",
    "phase4-dev-troubleshooting-method-and-rate-limit",
)

_TOP_K_CURVE = (2, 3, 5, 10, 20)

Decision = Literal["PROMOTE", "REJECT", "STOP_AND_REFRAME"]
Role = Literal["development", "tuning"]
RankOutcome = Literal["improved", "unchanged", "regressed", "unretrievable"]


class StratifiedRequiredEvidenceRankV1(ContractModel):
    evidence_id: NonEmptyStr
    incumbent_raw_rank: int | None = Field(default=None, ge=1)
    candidate_raw_rank: int | None = Field(default=None, ge=1)
    incumbent_eligible_rank: int | None = Field(default=None, ge=1)
    candidate_eligible_rank: int | None = Field(default=None, ge=1)
    incumbent_in_context: bool
    candidate_in_context: bool


class StratifiedCaseResultV1(ContractModel):
    role: Role
    case_id: NonEmptyStr
    previously_failed_development_case: bool

    required_evidence_count: int = Field(ge=1)
    required_evidence_ranks: tuple[
        StratifiedRequiredEvidenceRankV1,
        ...,
    ] = Field(min_length=1)

    incumbent_minimum_raw_top_k: int | None = Field(default=None, ge=1)
    candidate_minimum_raw_top_k: int | None = Field(default=None, ge=1)
    candidate_minimum_eligible_items: int | None = Field(default=None, ge=1)
    candidate_context_prefix_characters: int | None = Field(default=None, ge=1)

    incumbent_full_gold_k20: bool
    candidate_full_gold_k20: bool
    candidate_full_gold_eligible15: bool
    incumbent_full_gold_context: bool
    candidate_full_gold_context: bool

    candidate_context_item_count: int = Field(ge=0, le=15)
    candidate_assembled_context_characters: int = Field(ge=0, le=69663)

    rank_outcome_vs_incumbent: RankOutcome
    previously_passing_k20_regression: bool
    source_filter_regression: bool
    context_inclusion_regression: bool
    refusal_or_fallback_regression: bool
    deterministic_across_repeats: bool

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if len(self.required_evidence_ranks) != self.required_evidence_count:
            raise ValueError("required-evidence rank count does not reconcile")

        if self.previously_failed_development_case != (
            self.role == "development"
            and self.case_id in _FAILED_DEVELOPMENT_CASE_IDS
        ):
            raise ValueError("failed DEVELOPMENT identity drifted")

        if self.previously_passing_k20_regression != (
            self.incumbent_full_gold_k20
            and not self.candidate_full_gold_k20
        ):
            raise ValueError("k20 regression flag does not reconcile")

        if self.context_inclusion_regression != (
            self.incumbent_full_gold_context
            and not self.candidate_full_gold_context
        ):
            raise ValueError("context regression flag does not reconcile")

        return self


class Phase5StratifiedRetrievalCharacterizationV1(ContractModel):
    report_version: Literal[
        "phase5-stratified-retrieval-characterization-v1"
    ] = "phase5-stratified-retrieval-characterization-v1"

    evidence_class: Literal[
        "development_tuning_candidate_characterization"
    ] = "development_tuning_candidate_characterization"

    run_validity: Literal["VALID"] = "VALID"

    protocol_sha256: Sha256 = _PROTOCOL_SHA256
    protocol_freeze_sha256: Sha256 = _PROTOCOL_FREEZE_SHA256
    evidence_lane_diagnostic_sha256: Sha256 = _EVIDENCE_LANE_DIAGNOSTIC_SHA256
    chunk_manifest_sha256: Sha256 = _CHUNK_MANIFEST_SHA256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SHA256

    candidate_id: Literal[
        "phase5-incumbent-preserving-stratified-rrf-v1"
    ] = "phase5-incumbent-preserving-stratified-rrf-v1"

    development_answerable_case_count: Literal[20] = 20
    tuning_answerable_case_count: Literal[15] = 15
    total_answerable_case_count: Literal[35] = 35
    required_evidence_reference_count: Literal[43] = 43
    deterministic_repeat_count: Literal[3] = 3

    failed_development_recovered_count: int = Field(ge=0, le=4)

    top_k_curve: tuple[Phase5TopKCurvePoint, ...] = Field(
        min_length=5,
        max_length=5,
    )

    maximum_minimum_raw_top_k: int | None = Field(default=None, ge=1)
    maximum_minimum_eligible_items: int | None = Field(default=None, ge=1)
    maximum_context_prefix_characters: int | None = Field(default=None, ge=1)
    maximum_assembled_context_characters: int = Field(ge=0, le=69663)

    full_gold_k20_case_count: int = Field(ge=0, le=35)
    full_gold_eligible15_case_count: int = Field(ge=0, le=35)
    context_complete_case_count: int = Field(ge=0, le=35)

    improved_vs_incumbent_case_count: int = Field(ge=0, le=35)
    unchanged_vs_incumbent_case_count: int = Field(ge=0, le=35)
    regressed_vs_incumbent_case_count: int = Field(ge=0, le=35)
    unretrievable_case_count: int = Field(ge=0, le=35)

    previously_passing_k20_regression_count: int = Field(ge=0, le=35)
    source_filter_regression_count: int = Field(ge=0, le=35)
    context_inclusion_regression_count: int = Field(ge=0, le=35)
    refusal_or_fallback_regression_count: int = Field(ge=0, le=35)
    nondeterministic_case_count: int = Field(ge=0, le=35)

    case_results: tuple[
        StratifiedCaseResultV1,
        ...,
    ] = Field(min_length=35, max_length=35)

    promotion_gate_passed: bool
    promotion_gate_failures: tuple[NonEmptyStr, ...]
    characterization_decision: Decision

    candidate_implemented: Literal[True] = True
    candidate_executed: Literal[True] = True
    runtime_retriever_changed: Literal[False] = False

    evaluator_fields_passed_to_candidate: Literal[False] = False
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

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if tuple(point.top_k for point in self.top_k_curve) != _TOP_K_CURVE:
            raise ValueError("top-k curve drifted")

        identities = tuple(
            (result.role, result.case_id)
            for result in self.case_results
        )
        if len(identities) != len(set(identities)):
            raise ValueError("characterization case identities must be unique")

        if sum(result.required_evidence_count for result in self.case_results) != 43:
            raise ValueError("required-evidence denominator drifted")

        counts = (
            self.improved_vs_incumbent_case_count
            + self.unchanged_vs_incumbent_case_count
            + self.regressed_vs_incumbent_case_count
            + self.unretrievable_case_count
        )
        if counts != 35:
            raise ValueError("rank-outcome counts do not reconcile")

        integrity_failure = (
            self.nondeterministic_case_count > 0
            or self.evaluator_fields_passed_to_candidate
        )

        expected: Decision
        if integrity_failure:
            expected = "STOP_AND_REFRAME"
        elif self.promotion_gate_passed:
            expected = "PROMOTE"
        else:
            expected = "REJECT"

        if self.characterization_decision != expected:
            raise ValueError("characterization decision does not reconcile")

        forbidden = (
            self.runtime_retriever_changed
            or self.evaluator_fields_passed_to_candidate
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
        )
        if forbidden:
            raise ValueError("characterization overclaimed downstream state")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(path: Path, expected_sha256: str) -> bytes:
    content = path.read_bytes()
    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"
    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(f"frozen artifact sidecar mismatch: {path}")

    return content


def _load_controls(
    repo_root: Path,
) -> tuple[
    Phase5StratifiedRetrievalCandidateProtocolV1,
    Phase5StratifiedRetrievalCandidateProtocolFreezeV1,
]:
    protocol = Phase5StratifiedRetrievalCandidateProtocolV1.model_validate_json(
        _verified_bytes(repo_root / _PROTOCOL_PATH, _PROTOCOL_SHA256)
    )
    freeze = Phase5StratifiedRetrievalCandidateProtocolFreezeV1.model_validate_json(
        _verified_bytes(
            repo_root / _PROTOCOL_FREEZE_PATH,
            _PROTOCOL_FREEZE_SHA256,
        )
    )

    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("stratified freeze does not bind expected protocol")

    if not freeze.protocol_frozen:
        raise ValueError("stratified protocol is not frozen")

    if protocol.candidate.candidate_count != 1:
        raise ValueError("stratified protocol does not bind one candidate")

    _verified_bytes(
        repo_root / _EVIDENCE_LANE_DIAGNOSTIC_PATH,
        _EVIDENCE_LANE_DIAGNOSTIC_SHA256,
    )
    if (
        protocol.evidence_lane_diagnostic_sha256
        != _EVIDENCE_LANE_DIAGNOSTIC_SHA256
    ):
        raise ValueError("stratified protocol diagnostic identity drifted")

    return protocol, freeze


async def _build_context(
    *,
    builder: BoundedContextBuilder,
    query: str,
    evidence: tuple[RetrievedEvidence, ...],
) -> tuple[tuple[str, ...], int, int]:
    if not evidence:
        return (), 0, 0

    try:
        context = await builder.build(
            ContextBuildRequest(
                query=query,
                evidence=evidence,
            )
        )
    except ContextBudgetExhaustedError:
        return (), 0, 0

    return (
        tuple(item.evidence_id for item in context.items),
        len(context.items),
        len(context.assembled_context),
    )


def _curve(
    results: tuple[StratifiedCaseResultV1, ...],
) -> tuple[Phase5TopKCurvePoint, ...]:
    denominator = sum(item.required_evidence_count for item in results)
    points: list[Phase5TopKCurvePoint] = []

    for top_k in _TOP_K_CURVE:
        full_cases = 0
        retrieved_refs = 0

        for result in results:
            ranks = tuple(
                item.candidate_raw_rank
                for item in result.required_evidence_ranks
            )
            retrieved_refs += sum(
                rank is not None and rank <= top_k
                for rank in ranks
            )
            if all(
                rank is not None and rank <= top_k
                for rank in ranks
            ):
                full_cases += 1

        points.append(
            Phase5TopKCurvePoint(
                top_k=top_k,
                applicable_case_count=len(results),
                full_gold_case_count=full_cases,
                full_gold_case_rate=full_cases / len(results),
                required_evidence_reference_count=denominator,
                retrieved_required_evidence_count=retrieved_refs,
                micro_gold_recall=retrieved_refs / denominator,
            )
        )

    return tuple(points)


def _gate_failures(
    *,
    protocol: Phase5StratifiedRetrievalCandidateProtocolV1,
    curve: tuple[Phase5TopKCurvePoint, ...],
    failed_development_recovered_count: int,
    maximum_raw: int | None,
    maximum_eligible: int | None,
    maximum_context_prefix: int | None,
    full_gold_k20_count: int,
    full_gold_eligible15_count: int,
    context_complete_count: int,
    previously_passing_k20_regression_count: int,
    source_filter_regression_count: int,
    context_inclusion_regression_count: int,
    refusal_or_fallback_regression_count: int,
    nondeterministic_count: int,
) -> tuple[str, ...]:
    gate = protocol.promotion_gate
    point_20 = next(point for point in curve if point.top_k == 20)
    failures: list[str] = []

    if (
        failed_development_recovered_count
        != gate.failed_development_cases_required_recovered
    ):
        failures.append("failed_development_recovery_below_4")

    if full_gold_k20_count != gate.full_gold_cases_at_k20_required:
        failures.append("full_gold_cases_at_k20_below_35")

    if abs(
        point_20.micro_gold_recall
        - float(gate.micro_gold_recall_at_k20_required)
    ) > 1e-12:
        failures.append("micro_gold_recall_at_k20_below_1")

    if maximum_raw is None or maximum_raw > gate.maximum_raw_top_k_allowed:
        failures.append("maximum_raw_top_k_above_20")

    if (
        maximum_eligible is None
        or maximum_eligible > gate.maximum_eligible_items_allowed
    ):
        failures.append("maximum_eligible_items_above_15")

    if (
        maximum_context_prefix is None
        or maximum_context_prefix
        > gate.maximum_context_prefix_characters_allowed
    ):
        failures.append("maximum_context_prefix_above_69663")

    if full_gold_eligible15_count != gate.total_answerable_case_count:
        failures.append("full_gold_eligible15_cases_below_35")

    if context_complete_count != gate.total_answerable_case_count:
        failures.append("bounded_context_incomplete")

    if (
        previously_passing_k20_regression_count
        != gate.previously_passing_full_gold_k20_regressions_allowed
    ):
        failures.append("previously_passing_k20_regression_present")

    if source_filter_regression_count != gate.source_filter_regressions_allowed:
        failures.append("source_filter_regression_present")

    if (
        context_inclusion_regression_count
        != gate.context_inclusion_regressions_allowed
    ):
        failures.append("context_inclusion_regression_present")

    if (
        refusal_or_fallback_regression_count
        != gate.refusal_or_fallback_regressions_allowed
    ):
        failures.append("refusal_or_fallback_regression_present")

    if nondeterministic_count != gate.nondeterministic_result_tolerance:
        failures.append("candidate_nondeterminism_present")

    return tuple(failures)


def _minimum_rank(
    ranks: tuple[int | None, ...],
) -> int | None:
    if not all(rank is not None for rank in ranks):
        return None
    return max(cast(int, rank) for rank in ranks)


async def _build_report(
    repo_root: Path,
) -> Phase5StratifiedRetrievalCharacterizationV1:
    protocol, _freeze = _load_controls(repo_root)

    manifest = _load_manifest(repo_root)
    if _CHUNK_MANIFEST_SHA256 != protocol.chunk_manifest_sha256:
        raise ValueError("stratified protocol chunk manifest drifted")

    documents, _evidence_ids = _load_indexed_documents(repo_root)
    lanes = _partition_documents_by_lane(
        documents=documents,
        manifest=manifest,
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

    if len(development_cases) != 20 or len(tuning_cases) != 15:
        raise ValueError("answerable DEVELOPMENT/TUNING counts drifted")

    cases: tuple[tuple[Role, EvaluationCase], ...] = (
        tuple(("development", case) for case in development_cases)
        + tuple(("tuning", case) for case in tuning_cases)
    )

    if sum(len(case.required_evidence_ids) for _, case in cases) != 43:
        raise ValueError("required-evidence denominator drifted")

    rrf_config = Phase5RrfHybridCandidateConfig()
    lexical = LexicalRetriever(
        config=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=rrf_config.characterization_top_k,
        ),
        documents=documents,
    )
    global_bm25 = _Bm25CandidateRetriever(
        config=Phase5Bm25CandidateConfig(),
        documents=documents,
    )
    lane_bm25 = {
        kind: _Bm25CandidateRetriever(
            config=Phase5Bm25CandidateConfig(),
            documents=lanes[kind],
        )
        for kind in ChunkKind
    }

    resolver = DeterministicOperationResolver(
        load_runtime_operation_catalog(repo_root)
    )
    lineage = _lineage_map(manifest)

    source_filter = CurrentGithubRestSourcePolicyFilter(
        config=SourcePolicyConfig(
            policy_id="github-rest-current-v1",
        )
    )
    context_builder = BoundedContextBuilder(
        ContextConfig(
            builder_id="bounded-context-v1",
            budget_unit_id="characters",
            max_budget=protocol.candidate.context_max_budget_characters,
            max_evidence_items=protocol.candidate.context_max_evidence_items,
        )
    )

    ranker = IncumbentPreservingStratifiedRrfRanker(
        contract=protocol.candidate,
    )

    results: list[StratifiedCaseResultV1] = []

    for role, case in sorted(
        cases,
        key=lambda item: (item[0], item[1].case_id),
    ):
        runtime_input = case.to_runtime_input()

        repeats: list[
            tuple[
                tuple[RetrievedEvidence, ...],
                tuple[
                    tuple[ChunkKind, tuple[RetrievedEvidence, ...]],
                    ...,
                ],
                tuple[RetrievedEvidence, ...],
            ]
        ] = []

        for _ in range(protocol.promotion_gate.deterministic_repeat_count):
            incumbent = await _global_incumbent_once(
                query=runtime_input.query,
                lexical=lexical,
                bm25=global_bm25,
                rrf_config=rrf_config,
                resolver=resolver,
                lineage=lineage,
            )
            native = {
                kind: lane_bm25[kind].retrieve(runtime_input.query)
                for kind in ChunkKind
            }
            candidate = ranker.rank_all(
                incumbent_items=incumbent,
                lane_rankings=native,
            )

            repeats.append(
                (
                    incumbent,
                    tuple((kind, native[kind]) for kind in ChunkKind),
                    candidate,
                )
            )

        first_incumbent, first_native_pairs, full_candidate = repeats[0]
        deterministic = all(
            repeat == repeats[0]
            for repeat in repeats[1:]
        )

        native_first = dict(first_native_pairs)
        if set(native_first) != set(ChunkKind):
            raise ValueError("candidate did not execute all frozen lanes")

        incumbent_top20 = first_incumbent[
            : protocol.candidate.final_retrieval_top_k
        ]
        candidate_top20 = ranker.runtime_top_k(full_candidate)

        incumbent_filtered = await source_filter.apply(
            SourceFilterRequest(candidates=incumbent_top20)
        )
        candidate_filtered = await source_filter.apply(
            SourceFilterRequest(candidates=candidate_top20)
        )

        (
            incumbent_context_ids,
            _incumbent_context_count,
            _incumbent_context_chars,
        ) = await _build_context(
            builder=context_builder,
            query=runtime_input.query,
            evidence=incumbent_filtered.eligible,
        )
        (
            candidate_context_ids,
            candidate_context_count,
            candidate_context_chars,
        ) = await _build_context(
            builder=context_builder,
            query=runtime_input.query,
            evidence=candidate_filtered.eligible,
        )

        incumbent_raw = {
            item.evidence_id: item.rank
            for item in first_incumbent
        }
        candidate_raw = {
            item.evidence_id: item.rank
            for item in full_candidate
        }
        incumbent_eligible = {
            item.evidence_id: index
            for index, item in enumerate(
                incumbent_filtered.eligible,
                start=1,
            )
        }
        candidate_eligible = {
            item.evidence_id: index
            for index, item in enumerate(
                candidate_filtered.eligible,
                start=1,
            )
        }

        incumbent_context = set(incumbent_context_ids)
        candidate_context = set(candidate_context_ids)
        candidate_top20_ids = {
            item.evidence_id
            for item in candidate_top20
        }

        # Evaluator-owned required evidence is consulted only after incumbent,
        # all native lanes, the candidate merge, filtering, and context outputs
        # have already been materialized above.
        rank_records = tuple(
            StratifiedRequiredEvidenceRankV1(
                evidence_id=evidence_id,
                incumbent_raw_rank=incumbent_raw.get(evidence_id),
                candidate_raw_rank=candidate_raw.get(evidence_id),
                incumbent_eligible_rank=incumbent_eligible.get(evidence_id),
                candidate_eligible_rank=candidate_eligible.get(evidence_id),
                incumbent_in_context=evidence_id in incumbent_context,
                candidate_in_context=evidence_id in candidate_context,
            )
            for evidence_id in case.required_evidence_ids
        )

        incumbent_minimum_raw = _minimum_rank(
            tuple(item.incumbent_raw_rank for item in rank_records)
        )
        candidate_minimum_raw = _minimum_rank(
            tuple(item.candidate_raw_rank for item in rank_records)
        )
        candidate_minimum_eligible = _minimum_rank(
            tuple(item.candidate_eligible_rank for item in rank_records)
        )

        candidate_context_prefix: int | None = None
        if candidate_minimum_eligible is not None:
            candidate_context_prefix = _context_prefix_characters(
                cast(
                    tuple[object, ...],
                    candidate_filtered.eligible,
                ),
                candidate_minimum_eligible,
            )

        incumbent_full_k20 = (
            incumbent_minimum_raw is not None
            and incumbent_minimum_raw <= 20
        )
        candidate_full_k20 = (
            candidate_minimum_raw is not None
            and candidate_minimum_raw <= 20
        )
        candidate_full_eligible15 = (
            candidate_minimum_eligible is not None
            and candidate_minimum_eligible <= 15
        )
        incumbent_full_context = all(
            item.incumbent_in_context
            for item in rank_records
        )
        candidate_full_context = all(
            item.candidate_in_context
            for item in rank_records
        )

        if candidate_minimum_raw is None:
            rank_outcome: RankOutcome = "unretrievable"
        elif incumbent_minimum_raw is None:
            rank_outcome = "improved"
        elif candidate_minimum_raw < incumbent_minimum_raw:
            rank_outcome = "improved"
        elif candidate_minimum_raw == incumbent_minimum_raw:
            rank_outcome = "unchanged"
        else:
            rank_outcome = "regressed"

        source_filter_regression = any(
            item.evidence_id in candidate_top20_ids
            and item.incumbent_eligible_rank is not None
            and item.candidate_eligible_rank is None
            for item in rank_records
        )

        refusal_or_fallback_regression = (
            bool(incumbent_context_ids)
            and not bool(candidate_context_ids)
        )

        results.append(
            StratifiedCaseResultV1(
                role=role,
                case_id=case.case_id,
                previously_failed_development_case=(
                    role == "development"
                    and case.case_id in _FAILED_DEVELOPMENT_CASE_IDS
                ),
                required_evidence_count=len(case.required_evidence_ids),
                required_evidence_ranks=rank_records,
                incumbent_minimum_raw_top_k=incumbent_minimum_raw,
                candidate_minimum_raw_top_k=candidate_minimum_raw,
                candidate_minimum_eligible_items=candidate_minimum_eligible,
                candidate_context_prefix_characters=candidate_context_prefix,
                incumbent_full_gold_k20=incumbent_full_k20,
                candidate_full_gold_k20=candidate_full_k20,
                candidate_full_gold_eligible15=candidate_full_eligible15,
                incumbent_full_gold_context=incumbent_full_context,
                candidate_full_gold_context=candidate_full_context,
                candidate_context_item_count=candidate_context_count,
                candidate_assembled_context_characters=candidate_context_chars,
                rank_outcome_vs_incumbent=rank_outcome,
                previously_passing_k20_regression=(
                    incumbent_full_k20
                    and not candidate_full_k20
                ),
                source_filter_regression=source_filter_regression,
                context_inclusion_regression=(
                    incumbent_full_context
                    and not candidate_full_context
                ),
                refusal_or_fallback_regression=refusal_or_fallback_regression,
                deterministic_across_repeats=deterministic,
            )
        )

    typed_results = tuple(results)
    curve = _curve(typed_results)

    all_raw = all(
        result.candidate_minimum_raw_top_k is not None
        for result in typed_results
    )
    all_eligible = all(
        result.candidate_minimum_eligible_items is not None
        for result in typed_results
    )
    all_context_prefix = all(
        result.candidate_context_prefix_characters is not None
        for result in typed_results
    )

    maximum_raw = (
        max(
            cast(int, result.candidate_minimum_raw_top_k)
            for result in typed_results
        )
        if all_raw
        else None
    )
    maximum_eligible = (
        max(
            cast(int, result.candidate_minimum_eligible_items)
            for result in typed_results
        )
        if all_eligible
        else None
    )
    maximum_context_prefix = (
        max(
            cast(int, result.candidate_context_prefix_characters)
            for result in typed_results
        )
        if all_context_prefix
        else None
    )

    failed_development_recovered_count = sum(
        result.previously_failed_development_case
        and result.candidate_full_gold_k20
        for result in typed_results
    )
    full_gold_k20_count = sum(
        result.candidate_full_gold_k20
        for result in typed_results
    )
    full_gold_eligible15_count = sum(
        result.candidate_full_gold_eligible15
        for result in typed_results
    )
    context_complete_count = sum(
        result.candidate_full_gold_context
        for result in typed_results
    )

    k20_regression_count = sum(
        result.previously_passing_k20_regression
        for result in typed_results
    )
    source_filter_regression_count = sum(
        result.source_filter_regression
        for result in typed_results
    )
    context_regression_count = sum(
        result.context_inclusion_regression
        for result in typed_results
    )
    fallback_regression_count = sum(
        result.refusal_or_fallback_regression
        for result in typed_results
    )
    nondeterministic_count = sum(
        not result.deterministic_across_repeats
        for result in typed_results
    )

    failures = _gate_failures(
        protocol=protocol,
        curve=curve,
        failed_development_recovered_count=failed_development_recovered_count,
        maximum_raw=maximum_raw,
        maximum_eligible=maximum_eligible,
        maximum_context_prefix=maximum_context_prefix,
        full_gold_k20_count=full_gold_k20_count,
        full_gold_eligible15_count=full_gold_eligible15_count,
        context_complete_count=context_complete_count,
        previously_passing_k20_regression_count=k20_regression_count,
        source_filter_regression_count=source_filter_regression_count,
        context_inclusion_regression_count=context_regression_count,
        refusal_or_fallback_regression_count=fallback_regression_count,
        nondeterministic_count=nondeterministic_count,
    )

    integrity_failure = nondeterministic_count > 0

    if integrity_failure:
        decision: Decision = "STOP_AND_REFRAME"
    elif failures:
        decision = "REJECT"
    else:
        decision = "PROMOTE"

    return Phase5StratifiedRetrievalCharacterizationV1(
        failed_development_recovered_count=failed_development_recovered_count,
        top_k_curve=curve,
        maximum_minimum_raw_top_k=maximum_raw,
        maximum_minimum_eligible_items=maximum_eligible,
        maximum_context_prefix_characters=maximum_context_prefix,
        maximum_assembled_context_characters=max(
            result.candidate_assembled_context_characters
            for result in typed_results
        ),
        full_gold_k20_case_count=full_gold_k20_count,
        full_gold_eligible15_case_count=full_gold_eligible15_count,
        context_complete_case_count=context_complete_count,
        improved_vs_incumbent_case_count=sum(
            result.rank_outcome_vs_incumbent == "improved"
            for result in typed_results
        ),
        unchanged_vs_incumbent_case_count=sum(
            result.rank_outcome_vs_incumbent == "unchanged"
            for result in typed_results
        ),
        regressed_vs_incumbent_case_count=sum(
            result.rank_outcome_vs_incumbent == "regressed"
            for result in typed_results
        ),
        unretrievable_case_count=sum(
            result.rank_outcome_vs_incumbent == "unretrievable"
            for result in typed_results
        ),
        previously_passing_k20_regression_count=k20_regression_count,
        source_filter_regression_count=source_filter_regression_count,
        context_inclusion_regression_count=context_regression_count,
        refusal_or_fallback_regression_count=fallback_regression_count,
        nondeterministic_case_count=nondeterministic_count,
        case_results=typed_results,
        promotion_gate_passed=len(failures) == 0,
        promotion_gate_failures=failures,
        characterization_decision=decision,
    )


def materialize_phase5_stratified_retrieval_characterization(
    repo_root: Path,
) -> tuple[
    Phase5StratifiedRetrievalCharacterizationV1,
    str,
]:
    report = asyncio.run(_build_report(repo_root))
    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_stratified_retrieval_characterization(
        repo_root
    )

    point_20 = next(
        point
        for point in report.top_k_curve
        if point.top_k == 20
    )

    print(f"PHASE5_STRATIFIED_CHARACTERIZATION_SHA256={digest}")
    print(
        "PHASE5_STRATIFIED_K20="
        f"full_gold:{point_20.full_gold_case_count}/35,"
        f"micro:{point_20.micro_gold_recall:.6f}"
    )
    print(
        "PHASE5_STRATIFIED_FAILED_DEV_RECOVERED="
        f"{report.failed_development_recovered_count}/4"
    )
    print(
        "PHASE5_STRATIFIED_MAXIMA="
        f"raw:{report.maximum_minimum_raw_top_k},"
        f"eligible:{report.maximum_minimum_eligible_items},"
        f"context_prefix:{report.maximum_context_prefix_characters},"
        f"assembled:{report.maximum_assembled_context_characters}"
    )
    print(
        "PHASE5_STRATIFIED_CASE_OUTCOMES="
        f"improved:{report.improved_vs_incumbent_case_count},"
        f"unchanged:{report.unchanged_vs_incumbent_case_count},"
        f"regressed:{report.regressed_vs_incumbent_case_count},"
        f"unretrievable:{report.unretrievable_case_count}"
    )
    print(
        "PHASE5_STRATIFIED_REGRESSIONS="
        f"k20:{report.previously_passing_k20_regression_count},"
        f"filter:{report.source_filter_regression_count},"
        f"context:{report.context_inclusion_regression_count},"
        f"fallback:{report.refusal_or_fallback_regression_count},"
        f"nondeterministic:{report.nondeterministic_case_count}"
    )
    print(
        "PHASE5_STRATIFIED_PROMOTION_GATE_PASSED="
        f"{str(report.promotion_gate_passed).lower()}"
    )

    for failure in report.promotion_gate_failures:
        print(f"PHASE5_STRATIFIED_GATE_FAILURE={failure}")

    print(
        "PHASE5_STRATIFIED_DECISION="
        f"{report.characterization_decision}"
    )
    print("PHASE5_RUNTIME_RETRIEVER_CHANGED=false")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false")
    print("PHASE5_RETRIEVAL_CONFIGURATION_SELECTED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")


if __name__ == "__main__":
    main()
