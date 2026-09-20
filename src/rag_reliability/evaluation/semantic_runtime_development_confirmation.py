"""Confirm the frozen Phase 5 semantic-runtime candidate on DEVELOPMENT.

This experiment is confirmatory, not a tuning surface. It reconstructs the
promoted operation-aware RRF candidate, applies the frozen top-k/source-policy
boundary, then executes the real bounded context builder at the frozen
20 / 15 / 69663 candidate values. Evaluator gold is consulted only after
runtime-visible outputs exist.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import (
    ContextConfig,
    RetrievalConfig,
    SourcePolicyConfig,
)
from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import EvaluationRole, ResponseMode
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import (
    ContextBuildRequest,
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
from rag_reliability.evaluation.operation_aware_rrf_candidate_experiment import (
    Phase5OperationAwareRrfCandidateExperimentReport,
)
from rag_reliability.evaluation.retrieval_characterization import (
    Phase5TopKCurvePoint,
    _context_prefix_characters,
    _load_indexed_documents,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    _fuse_rankings,
)
from rag_reliability.evaluation.semantic_runtime_candidate_protocol import (
    Phase5SemanticRuntimeCandidateProtocolV1,
)
from rag_reliability.evaluation.semantic_runtime_candidate_protocol_freeze import (
    Phase5SemanticRuntimeCandidateProtocolFreezeReceipt,
)
from rag_reliability.runtime.context import BoundedContextBuilder
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

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_candidate_protocol_v1.json"
)
_PROTOCOL_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_candidate_protocol_freeze_v1.json"
)
_PROMOTED_RETRIEVAL_PATH = (
    Path("artifacts") / "development" / "phase5_operation_aware_rrf_candidate_experiment_v1.json"
)
_DEVELOPMENT_PATH = Path("artifacts") / "development" / "phase4c_development_cases_v1.json"
_CHUNK_MANIFEST_PATH = Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
_OUTPUT_PATH = (
    Path("artifacts") / "development" / "phase5_semantic_runtime_development_confirmation_v1.json"
)

_PROTOCOL_SHA256: Literal["b36813907d2f581e6cfd559b96978bb93cc00855655c2204905a0e33126e6931"] = (
    "b36813907d2f581e6cfd559b96978bb93cc00855655c2204905a0e33126e6931"
)

_PROTOCOL_FREEZE_SHA256: Literal[
    "b3401a81900d63cc612fb7855b52a13c9af376efc47a97c1aebda6a17cd273a0"
] = "b3401a81900d63cc612fb7855b52a13c9af376efc47a97c1aebda6a17cd273a0"

_PROMOTED_RETRIEVAL_SHA256: Literal[
    "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
] = "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"

_DEVELOPMENT_SHA256: Literal["53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"] = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)

_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

_TOP_K_CURVE: tuple[int, ...] = (2, 3, 5, 10, 20)

_DECISION_CONFIRM: Literal["CONFIRM"] = "CONFIRM"
_DECISION_REJECT: Literal["REJECT"] = "REJECT"
_DECISION_STOP: Literal["STOP_AND_REFRAME"] = "STOP_AND_REFRAME"

ConfirmationDecision = Literal[
    "CONFIRM",
    "REJECT",
    "STOP_AND_REFRAME",
]


class DevelopmentRequiredEvidenceRank(ContractModel):
    evidence_id: NonEmptyStr
    raw_rank: int | None = Field(default=None, ge=1)
    eligible_rank: int | None = Field(default=None, ge=1)
    included_in_context: bool


class DevelopmentAnswerableCaseResult(ContractModel):
    case_id: NonEmptyStr
    resolution_status: ResolutionStatus
    resolved_operation_id: NonEmptyStr | None = None

    required_evidence_count: int = Field(ge=1)
    required_evidence_ranks: tuple[
        DevelopmentRequiredEvidenceRank,
        ...,
    ] = Field(min_length=1)

    minimum_raw_top_k_for_full_gold: int | None = Field(default=None, ge=1)
    minimum_eligible_items_for_full_gold: int | None = Field(default=None, ge=1)
    context_prefix_characters_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )

    full_gold_retrievable_within_top20: bool
    full_gold_filter_eligible_within_15: bool
    full_gold_in_bounded_context: bool

    context_item_count: int = Field(ge=1, le=15)
    assembled_context_characters: int = Field(ge=1, le=69663)

    fallback_order_preserved: bool | None = None
    deterministic_across_repeats: bool

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if len(self.required_evidence_ranks) != self.required_evidence_count:
            raise ValueError("required-evidence rank count does not reconcile")

        if self.resolution_status is ResolutionStatus.RESOLVED:
            if self.resolved_operation_id is None:
                raise ValueError("resolved case requires operation ID")
            if self.fallback_order_preserved is not None:
                raise ValueError("resolved case cannot carry fallback-order verdict")
        else:
            if self.resolved_operation_id is not None:
                raise ValueError("fallback case cannot carry resolved operation ID")
            if self.fallback_order_preserved is None:
                raise ValueError("fallback case requires exact-order verdict")

        if self.full_gold_retrievable_within_top20 != (
            self.minimum_raw_top_k_for_full_gold is not None
            and self.minimum_raw_top_k_for_full_gold <= 20
        ):
            raise ValueError("raw top-k verdict does not reconcile")

        if self.full_gold_filter_eligible_within_15 != (
            self.minimum_eligible_items_for_full_gold is not None
            and self.minimum_eligible_items_for_full_gold <= 15
        ):
            raise ValueError("eligible-item verdict does not reconcile")

        if self.full_gold_in_bounded_context != all(
            item.included_in_context for item in self.required_evidence_ranks
        ):
            raise ValueError("bounded-context inclusion verdict does not reconcile")

        return self


class Phase5DevelopmentConfirmationReport(ContractModel):
    report_version: Literal["phase5-semantic-runtime-development-confirmation-v1"] = (
        "phase5-semantic-runtime-development-confirmation-v1"
    )

    evidence_class: Literal["development_confirmation_only"] = "development_confirmation_only"

    protocol_sha256: Literal["b36813907d2f581e6cfd559b96978bb93cc00855655c2204905a0e33126e6931"] = (
        _PROTOCOL_SHA256
    )

    protocol_freeze_sha256: Literal[
        "b3401a81900d63cc612fb7855b52a13c9af376efc47a97c1aebda6a17cd273a0"
    ] = _PROTOCOL_FREEZE_SHA256

    promoted_retrieval_sha256: Literal[
        "7888a6d79839b06b49aaa7e38878d4b19199bff973f806e53b05b15e1e011115"
    ] = _PROMOTED_RETRIEVAL_SHA256

    development_suite_sha256: Literal[
        "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
    ] = _DEVELOPMENT_SHA256

    development_case_count: Literal[24] = 24
    answerable_case_count: Literal[20] = 20
    refusal_case_count: Literal[4] = 4
    required_evidence_reference_count: Literal[25] = 25

    candidate_retrieval_top_k: Literal[20] = 20
    candidate_context_max_evidence_items: Literal[15] = 15
    candidate_context_max_budget: Literal[69663] = 69663

    deterministic_repeat_count: Literal[3] = 3

    resolved_answerable_case_count: int = Field(ge=0, le=20)
    ambiguous_answerable_case_count: int = Field(ge=0, le=20)
    unresolved_answerable_case_count: int = Field(ge=0, le=20)

    top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=5, max_length=5)

    maximum_minimum_raw_top_k: int | None = Field(default=None, ge=1)
    maximum_minimum_eligible_items: int | None = Field(default=None, ge=1)
    maximum_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )
    maximum_assembled_context_characters: int = Field(ge=1, le=69663)

    full_gold_answerable_case_count: int = Field(ge=0, le=20)
    context_complete_answerable_case_count: int = Field(ge=0, le=20)

    unretrievable_case_count: int = Field(ge=0, le=20)
    filter_ineligible_case_count: int = Field(ge=0, le=20)
    context_exclusion_case_count: int = Field(ge=0, le=20)

    fallback_order_mismatch_count: int = Field(ge=0, le=20)
    nondeterministic_case_count: int = Field(ge=0, le=20)

    case_results: tuple[
        DevelopmentAnswerableCaseResult,
        ...,
    ] = Field(min_length=20, max_length=20)

    confirmation_gate_passed: bool
    confirmation_gate_failures: tuple[NonEmptyStr, ...]
    confirmation_decision: ConfirmationDecision

    development_gold_used_for_confirmation_only: Literal[True] = True
    development_gold_used_for_tuning: Literal[False] = False
    tuning_parameters_changed: Literal[False] = False

    evaluator_fields_passed_to_candidate: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False

    runtime_retriever_integrated: Literal[False] = False
    runtime_configuration_materialized: Literal[False] = False
    semantic_runtime_capacity_gate_satisfied: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if (
            self.resolved_answerable_case_count
            + self.ambiguous_answerable_case_count
            + self.unresolved_answerable_case_count
            != self.answerable_case_count
        ):
            raise ValueError("resolver status counts do not reconcile")

        if tuple(point.top_k for point in self.top_k_curve) != _TOP_K_CURVE:
            raise ValueError("DEVELOPMENT top-k curve drifted")

        if self.confirmation_gate_passed != (len(self.confirmation_gate_failures) == 0):
            raise ValueError("confirmation verdict does not reconcile")

        integrity_failure = (
            self.fallback_order_mismatch_count > 0
            or self.nondeterministic_case_count > 0
            or self.evaluator_fields_passed_to_candidate
        )

        if integrity_failure:
            expected: ConfirmationDecision = _DECISION_STOP
        elif self.confirmation_gate_passed:
            expected = _DECISION_CONFIRM
        else:
            expected = _DECISION_REJECT

        if self.confirmation_decision != expected:
            raise ValueError("confirmation decision does not reconcile")

        if (
            self.development_gold_used_for_tuning
            or self.tuning_parameters_changed
            or self.evaluator_fields_passed_to_candidate
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.runtime_retriever_integrated
            or self.runtime_configuration_materialized
            or self.semantic_runtime_capacity_gate_satisfied
            or self.semantic_runtime_configuration_selected
            or self.semantic_runtime_configuration_frozen
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("DEVELOPMENT confirmation overclaimed execution state")

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


def _load_development_cases(repo_root: Path) -> tuple[EvaluationCase, ...]:
    content = _verified_bytes(
        repo_root / _DEVELOPMENT_PATH,
        _DEVELOPMENT_SHA256,
    )
    payload = json.loads(content)

    if not isinstance(payload, dict) or payload.get("case_count") != 24:
        raise ValueError("DEVELOPMENT suite shape drifted")

    raw_records = payload.get("records")
    if not isinstance(raw_records, list):
        raise ValueError("DEVELOPMENT records must be an array")

    cases: list[EvaluationCase] = []
    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            raise ValueError("DEVELOPMENT record must be an object")

        raw_case = raw_record.get("case")
        if not isinstance(raw_case, dict):
            raise ValueError("DEVELOPMENT record requires case object")

        case = EvaluationCase.model_validate(raw_case)
        if case.data_role is not EvaluationRole.DEVELOPMENT:
            raise ValueError("confirmation must remain DEVELOPMENT-only")
        cases.append(case)

    if len(cases) != 24:
        raise ValueError("DEVELOPMENT record count drifted")

    if len({case.case_id for case in cases}) != 24:
        raise ValueError("DEVELOPMENT case IDs must be unique")

    return tuple(cases)


def _load_controls(
    repo_root: Path,
) -> tuple[
    Phase5SemanticRuntimeCandidateProtocolV1,
    Phase5SemanticRuntimeCandidateProtocolFreezeReceipt,
    Phase5OperationAwareRrfCandidateExperimentReport,
    Phase3dChunkManifest,
]:
    protocol = Phase5SemanticRuntimeCandidateProtocolV1.model_validate_json(
        _verified_bytes(repo_root / _PROTOCOL_PATH, _PROTOCOL_SHA256)
    )
    freeze = Phase5SemanticRuntimeCandidateProtocolFreezeReceipt.model_validate_json(
        _verified_bytes(
            repo_root / _PROTOCOL_FREEZE_PATH,
            _PROTOCOL_FREEZE_SHA256,
        )
    )
    promoted = Phase5OperationAwareRrfCandidateExperimentReport.model_validate_json(
        _verified_bytes(
            repo_root / _PROMOTED_RETRIEVAL_PATH,
            _PROMOTED_RETRIEVAL_SHA256,
        )
    )
    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            repo_root / _CHUNK_MANIFEST_PATH,
            _CHUNK_MANIFEST_SHA256,
        )
    )

    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("candidate freeze does not bind expected protocol")

    if promoted.experiment_decision != "PROMOTE":
        raise ValueError("retrieval candidate is not promoted")

    candidate = protocol.candidate
    if (
        candidate.retrieval_top_k,
        candidate.context_max_evidence_items,
        candidate.context_max_budget,
    ) != (20, 15, 69663):
        raise ValueError("frozen candidate values drifted")

    return protocol, freeze, promoted, manifest


def _lineage_map(
    manifest: Phase3dChunkManifest,
) -> dict[str, tuple[str, ...]]:
    return {chunk.chunk_id: tuple(chunk.linked_operation_ids) for chunk in manifest.chunks}


def _candidate_once(
    *,
    query: str,
    generic_items: tuple[RetrievedEvidence, ...],
    resolver: DeterministicOperationResolver,
    lineage: dict[str, tuple[str, ...]],
) -> tuple[OperationResolution, tuple[RetrievedEvidence, ...]]:
    resolution = resolver.resolve(query)
    ranked = stable_partition_by_operation_lineage(
        items=generic_items,
        resolution=resolution,
        linked_operation_ids_by_evidence_id=lineage,
    )
    return resolution, ranked


def _curve(
    results: tuple[DevelopmentAnswerableCaseResult, ...],
) -> tuple[Phase5TopKCurvePoint, ...]:
    denominator = sum(item.required_evidence_count for item in results)
    points: list[Phase5TopKCurvePoint] = []

    for top_k in _TOP_K_CURVE:
        full_cases = 0
        retrieved_refs = 0

        for result in results:
            ranks = tuple(item.raw_rank for item in result.required_evidence_ranks)
            retrieved_refs += sum(rank is not None and rank <= top_k for rank in ranks)
            if all(rank is not None and rank <= top_k for rank in ranks):
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
    curve: tuple[Phase5TopKCurvePoint, ...],
    maximum_raw: int | None,
    maximum_eligible: int | None,
    maximum_context_prefix: int | None,
    full_gold_case_count: int,
    context_complete_case_count: int,
    unretrievable_count: int,
    filter_ineligible_count: int,
    context_exclusion_count: int,
    fallback_mismatch_count: int,
    nondeterministic_count: int,
) -> tuple[str, ...]:
    point_20 = next(point for point in curve if point.top_k == 20)
    failures: list[str] = []

    if full_gold_case_count != 20:
        failures.append("full_gold_answerable_cases_below_20")

    if point_20.full_gold_case_count != 20:
        failures.append("full_gold_cases_at_k20_below_20")

    if abs(point_20.micro_gold_recall - 1.0) > 1e-12:
        failures.append("micro_gold_recall_at_k20_below_1")

    if maximum_raw is None or maximum_raw > 20:
        failures.append("maximum_raw_top_k_above_20")

    if maximum_eligible is None or maximum_eligible > 15:
        failures.append("maximum_eligible_items_above_15")

    if maximum_context_prefix is None or maximum_context_prefix > 69663:
        failures.append("maximum_context_prefix_above_69663")

    if context_complete_case_count != 20:
        failures.append("bounded_context_incomplete")

    if unretrievable_count != 0:
        failures.append("unretrievable_gold_present")

    if filter_ineligible_count != 0:
        failures.append("filter_ineligible_gold_present")

    if context_exclusion_count != 0:
        failures.append("context_exclusion_present")

    if fallback_mismatch_count != 0:
        failures.append("generic_rrf_fallback_order_mismatch")

    if nondeterministic_count != 0:
        failures.append("candidate_nondeterminism_present")

    return tuple(failures)


async def _build_report(
    repo_root: Path,
) -> Phase5DevelopmentConfirmationReport:
    protocol, _freeze, _promoted, manifest = _load_controls(repo_root)
    cases = _load_development_cases(repo_root)
    documents, _ids = _load_indexed_documents(repo_root)

    answerable_cases = tuple(
        case for case in cases if case.expected_response_mode is not ResponseMode.REFUSE
    )
    refusal_cases = tuple(
        case for case in cases if case.expected_response_mode is ResponseMode.REFUSE
    )

    if len(answerable_cases) != 20 or len(refusal_cases) != 4:
        raise ValueError("DEVELOPMENT answerable/refusal counts drifted")

    if sum(len(case.required_evidence_ids) for case in answerable_cases) != 25:
        raise ValueError("DEVELOPMENT required-evidence denominator drifted")

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
    source_filter = CurrentGithubRestSourcePolicyFilter(
        config=SourcePolicyConfig(
            policy_id=protocol.candidate.source_policy_id,
        )
    )
    context_builder = BoundedContextBuilder(
        ContextConfig(
            builder_id=protocol.candidate.context_builder_id,
            budget_unit_id=protocol.candidate.context_budget_unit_id,
            max_budget=protocol.candidate.context_max_budget,
            max_evidence_items=protocol.candidate.context_max_evidence_items,
        )
    )
    resolver = DeterministicOperationResolver(load_runtime_operation_catalog(repo_root))
    lineage = _lineage_map(manifest)

    results: list[DevelopmentAnswerableCaseResult] = []

    for case in sorted(answerable_cases, key=lambda item: item.case_id):
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
        generic_items = _fuse_rankings(
            lexical_items=lexical_items,
            bm25_items=bm25_items,
            config=rrf_config,
        )

        repeats = tuple(
            _candidate_once(
                query=runtime_input.query,
                generic_items=generic_items,
                resolver=resolver,
                lineage=lineage,
            )
            for _ in range(3)
        )

        resolution, full_candidate = repeats[0]
        deterministic = all(
            repeated_resolution == resolution and repeated_items == full_candidate
            for repeated_resolution, repeated_items in repeats
        )

        runtime_top20 = full_candidate[: protocol.candidate.retrieval_top_k]
        generic_top20 = generic_items[: protocol.candidate.retrieval_top_k]

        fallback_order_preserved: bool | None = None
        resolved_operation_id: str | None = None

        if resolution.status is ResolutionStatus.RESOLVED:
            resolved_operation_id = resolution.operation_ids[0]
        else:
            fallback_order_preserved = runtime_top20 == generic_top20

        filtered = await source_filter.apply(SourceFilterRequest(candidates=runtime_top20))

        context = await context_builder.build(
            ContextBuildRequest(
                query=runtime_input.query,
                evidence=filtered.eligible,
            )
        )

        raw_by_id = {item.evidence_id: item.rank for item in full_candidate}
        eligible_by_id = {
            item.evidence_id: index for index, item in enumerate(filtered.eligible, start=1)
        }
        context_ids = {item.evidence_id for item in context.items}

        rank_records = tuple(
            DevelopmentRequiredEvidenceRank(
                evidence_id=evidence_id,
                raw_rank=raw_by_id.get(evidence_id),
                eligible_rank=eligible_by_id.get(evidence_id),
                included_in_context=evidence_id in context_ids,
            )
            for evidence_id in case.required_evidence_ids
        )

        all_raw = all(item.raw_rank is not None for item in rank_records)
        all_eligible = all(item.eligible_rank is not None for item in rank_records)

        minimum_raw: int | None = None
        if all_raw:
            minimum_raw = max(cast(int, item.raw_rank) for item in rank_records)

        minimum_eligible: int | None = None
        context_prefix: int | None = None
        if all_eligible:
            minimum_eligible = max(cast(int, item.eligible_rank) for item in rank_records)
            context_prefix = _context_prefix_characters(
                cast(tuple[object, ...], filtered.eligible),
                minimum_eligible,
            )

        results.append(
            DevelopmentAnswerableCaseResult(
                case_id=case.case_id,
                resolution_status=resolution.status,
                resolved_operation_id=resolved_operation_id,
                required_evidence_count=len(case.required_evidence_ids),
                required_evidence_ranks=rank_records,
                minimum_raw_top_k_for_full_gold=minimum_raw,
                minimum_eligible_items_for_full_gold=minimum_eligible,
                context_prefix_characters_for_full_gold=context_prefix,
                full_gold_retrievable_within_top20=(minimum_raw is not None and minimum_raw <= 20),
                full_gold_filter_eligible_within_15=(
                    minimum_eligible is not None and minimum_eligible <= 15
                ),
                full_gold_in_bounded_context=all(item.included_in_context for item in rank_records),
                context_item_count=len(context.items),
                assembled_context_characters=len(context.assembled_context),
                fallback_order_preserved=fallback_order_preserved,
                deterministic_across_repeats=deterministic,
            )
        )

    typed_results = tuple(results)
    curve = _curve(typed_results)

    full_gold_count = sum(
        result.full_gold_retrievable_within_top20 and result.full_gold_filter_eligible_within_15
        for result in typed_results
    )
    context_complete_count = sum(result.full_gold_in_bounded_context for result in typed_results)

    all_raw = all(result.minimum_raw_top_k_for_full_gold is not None for result in typed_results)
    all_eligible = all(
        result.minimum_eligible_items_for_full_gold is not None for result in typed_results
    )
    all_context_prefix = all(
        result.context_prefix_characters_for_full_gold is not None for result in typed_results
    )

    maximum_raw = (
        max(cast(int, result.minimum_raw_top_k_for_full_gold) for result in typed_results)
        if all_raw
        else None
    )
    maximum_eligible = (
        max(cast(int, result.minimum_eligible_items_for_full_gold) for result in typed_results)
        if all_eligible
        else None
    )
    maximum_context_prefix = (
        max(cast(int, result.context_prefix_characters_for_full_gold) for result in typed_results)
        if all_context_prefix
        else None
    )

    unretrievable_count = sum(
        not result.full_gold_retrievable_within_top20 for result in typed_results
    )
    filter_ineligible_count = sum(
        not result.full_gold_filter_eligible_within_15 for result in typed_results
    )
    context_exclusion_count = sum(
        not result.full_gold_in_bounded_context for result in typed_results
    )
    fallback_mismatch_count = sum(
        result.fallback_order_preserved is False for result in typed_results
    )
    nondeterministic_count = sum(
        not result.deterministic_across_repeats for result in typed_results
    )

    failures = _gate_failures(
        curve=curve,
        maximum_raw=maximum_raw,
        maximum_eligible=maximum_eligible,
        maximum_context_prefix=maximum_context_prefix,
        full_gold_case_count=full_gold_count,
        context_complete_case_count=context_complete_count,
        unretrievable_count=unretrievable_count,
        filter_ineligible_count=filter_ineligible_count,
        context_exclusion_count=context_exclusion_count,
        fallback_mismatch_count=fallback_mismatch_count,
        nondeterministic_count=nondeterministic_count,
    )

    integrity_failure = fallback_mismatch_count > 0 or nondeterministic_count > 0

    if integrity_failure:
        decision: ConfirmationDecision = _DECISION_STOP
    elif failures:
        decision = _DECISION_REJECT
    else:
        decision = _DECISION_CONFIRM

    return Phase5DevelopmentConfirmationReport(
        resolved_answerable_case_count=sum(
            result.resolution_status is ResolutionStatus.RESOLVED for result in typed_results
        ),
        ambiguous_answerable_case_count=sum(
            result.resolution_status is ResolutionStatus.AMBIGUOUS for result in typed_results
        ),
        unresolved_answerable_case_count=sum(
            result.resolution_status is ResolutionStatus.UNRESOLVED for result in typed_results
        ),
        top_k_curve=curve,
        maximum_minimum_raw_top_k=maximum_raw,
        maximum_minimum_eligible_items=maximum_eligible,
        maximum_context_prefix_characters=maximum_context_prefix,
        maximum_assembled_context_characters=max(
            result.assembled_context_characters for result in typed_results
        ),
        full_gold_answerable_case_count=full_gold_count,
        context_complete_answerable_case_count=context_complete_count,
        unretrievable_case_count=unretrievable_count,
        filter_ineligible_case_count=filter_ineligible_count,
        context_exclusion_case_count=context_exclusion_count,
        fallback_order_mismatch_count=fallback_mismatch_count,
        nondeterministic_case_count=nondeterministic_count,
        case_results=typed_results,
        confirmation_gate_passed=len(failures) == 0,
        confirmation_gate_failures=failures,
        confirmation_decision=decision,
    )


def materialize_phase5_semantic_runtime_development_confirmation(
    repo_root: Path,
) -> tuple[Phase5DevelopmentConfirmationReport, str]:
    report = asyncio.run(_build_report(repo_root))
    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_semantic_runtime_development_confirmation(repo_root)

    point_20 = next(point for point in report.top_k_curve if point.top_k == 20)

    print(f"PHASE5_DEVELOPMENT_CONFIRMATION_SHA256={digest}")
    print(
        "PHASE5_DEVELOPMENT_CONFIRMATION_K20="
        f"full_gold:{point_20.full_gold_case_count}/20,"
        f"micro:{point_20.micro_gold_recall:.6f}"
    )
    print(
        "PHASE5_DEVELOPMENT_CONFIRMATION_MAXIMA="
        f"raw:{report.maximum_minimum_raw_top_k},"
        f"eligible:{report.maximum_minimum_eligible_items},"
        f"context_prefix:{report.maximum_context_prefix_characters},"
        f"assembled:{report.maximum_assembled_context_characters}"
    )
    print(
        "PHASE5_DEVELOPMENT_CONFIRMATION_RESOLUTION="
        f"resolved:{report.resolved_answerable_case_count},"
        f"ambiguous:{report.ambiguous_answerable_case_count},"
        f"unresolved:{report.unresolved_answerable_case_count}"
    )
    print(
        "PHASE5_DEVELOPMENT_CONFIRMATION_INTEGRITY="
        f"unretrievable:{report.unretrievable_case_count},"
        f"filter_ineligible:{report.filter_ineligible_case_count},"
        f"context_exclusion:{report.context_exclusion_case_count},"
        f"fallback_mismatch:{report.fallback_order_mismatch_count},"
        f"nondeterministic:{report.nondeterministic_case_count}"
    )
    print(
        "PHASE5_DEVELOPMENT_CONFIRMATION_GATE_PASSED="
        f"{str(report.confirmation_gate_passed).lower()}"
    )

    for failure in report.confirmation_gate_failures:
        print(f"PHASE5_DEVELOPMENT_CONFIRMATION_FAILURE={failure}")

    print(f"PHASE5_DEVELOPMENT_CONFIRMATION_DECISION={report.confirmation_decision}")
    print("PHASE5_PROVIDER_INVOKED=false")
    print("PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false")
    print("PHASE5_SEMANTIC_RUNTIME_CAPACITY_GATE_SATISFIED=false")
    print("PHASE5_SEMANTIC_RUNTIME_CONFIGURATION_SELECTED=false")
    print("PHASE5_B0_EXECUTED=false")


if __name__ == "__main__":
    main()
