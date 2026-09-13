"""Fixed lexical+BM25 reciprocal-rank-fusion experiment for Phase 5.

This experiment tests one predeclared RRF candidate against the frozen lexical
and BM25 TUNING evidence. It is evaluation-only: no runtime component is
changed, no DEVELOPMENT gold is used, no HELD_OUT outcome is exposed, no
provider is invoked, and B0 remains unauthorized.
"""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import (
    CanonicalConfigModel,
    RetrievalConfig,
    SourcePolicyConfig,
)
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.runtime import (
    RetrievalRequest,
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    Phase5Bm25CandidateExperimentReport,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.retrieval_characterization import (
    Phase5TopKCurvePoint,
    Phase5TuningRetrievalCharacterizationReport,
    _context_prefix_characters,
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.runtime.filtering import (
    CurrentGithubRestSourcePolicyFilter,
)
from rag_reliability.runtime.retrieval import LexicalRetriever

_LEXICAL_BASELINE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_tuning_retrieval_characterization_v1.json"
)

_BM25_EXPERIMENT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_bm25_candidate_experiment_v1.json"
)

_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_rrf_hybrid_candidate_experiment_v1.json"
)

_LEXICAL_BASELINE_SHA256: Literal[
    "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"
] = "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"

_BM25_EXPERIMENT_SHA256: Literal[
    "ef58106aef6087f7e4761df6afbe1e0c3819ffa8304c7b11c4c446faa6437370"
] = "ef58106aef6087f7e4761df6afbe1e0c3819ffa8304c7b11c4c446faa6437370"

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


class Phase5RrfHybridCandidateConfig(CanonicalConfigModel):
    """One fixed, non-swept reciprocal-rank-fusion candidate."""

    candidate_version: Literal[
        "phase5-rrf-hybrid-candidate-v1"
    ] = "phase5-rrf-hybrid-candidate-v1"

    retriever_id: Literal[
        "lexical-bm25-rrf-evaluation-candidate-v1"
    ] = "lexical-bm25-rrf-evaluation-candidate-v1"

    characterization_top_k: Literal[1333] = 1333
    fusion_constant: Literal[60] = 60

    lexical_weight: Literal[1] = 1
    bm25_weight: Literal[1] = 1

    parameter_sweep_used: Literal[False] = False
    tuning_parameter_optimization_used: Literal[False] = False


class Phase5RrfRequiredEvidenceRank(ContractModel):
    evidence_id: NonEmptyStr
    raw_rank: int | None = Field(default=None, ge=1)
    eligible_rank: int | None = Field(default=None, ge=1)
    survived_source_filter: bool

    @model_validator(mode="after")
    def validate_rank_boundary(self) -> Self:
        if self.eligible_rank is not None and self.raw_rank is None:
            raise ValueError(
                "eligible evidence cannot exist without a raw hybrid rank"
            )

        if self.survived_source_filter != (self.eligible_rank is not None):
            raise ValueError(
                "source-filter survival does not reconcile with eligible rank"
            )

        return self


class Phase5RrfCaseComparison(ContractModel):
    case_id: NonEmptyStr
    required_evidence_count: int = Field(ge=1)

    lexical_minimum_raw_top_k: int = Field(ge=1)
    bm25_minimum_raw_top_k: int = Field(ge=1)
    hybrid_minimum_raw_top_k: int | None = Field(default=None, ge=1)

    lexical_minimum_eligible_items: int = Field(ge=1)
    bm25_minimum_eligible_items: int = Field(ge=1)
    hybrid_minimum_eligible_items: int | None = Field(default=None, ge=1)

    lexical_context_prefix_characters: int = Field(ge=1)
    bm25_context_prefix_characters: int = Field(ge=1)
    hybrid_context_prefix_characters: int | None = Field(default=None, ge=1)

    hybrid_required_evidence_ranks: tuple[
        Phase5RrfRequiredEvidenceRank,
        ...,
    ]

    full_gold_retrievable: bool
    full_gold_filter_eligible: bool

    lexical_rank_outcome: Literal[
        "improved",
        "unchanged",
        "regressed",
        "unretrievable",
    ]

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if (
            len(self.hybrid_required_evidence_ranks)
            != self.required_evidence_count
        ):
            raise ValueError(
                "hybrid required-evidence rank count does not reconcile"
            )

        if self.full_gold_retrievable != (
            self.hybrid_minimum_raw_top_k is not None
        ):
            raise ValueError(
                "hybrid raw rank does not reconcile with retrievability"
            )

        if self.full_gold_filter_eligible != (
            self.hybrid_minimum_eligible_items is not None
            and self.hybrid_context_prefix_characters is not None
        ):
            raise ValueError(
                "hybrid eligible/context state does not reconcile"
            )

        if not self.full_gold_retrievable:
            expected = "unretrievable"
        elif (
            cast(int, self.hybrid_minimum_raw_top_k)
            < self.lexical_minimum_raw_top_k
        ):
            expected = "improved"
        elif (
            cast(int, self.hybrid_minimum_raw_top_k)
            == self.lexical_minimum_raw_top_k
        ):
            expected = "unchanged"
        else:
            expected = "regressed"

        if self.lexical_rank_outcome != expected:
            raise ValueError(
                "hybrid/lexical rank outcome does not reconcile"
            )

        return self


class Phase5RrfPromotionGate(ContractModel):
    """Predeclared gate; values are derived only after candidate execution."""

    full_gold_cases_at_k20_required: Literal[15] = 15
    micro_gold_recall_at_k20_required: Literal["1.0"] = "1.0"
    maximum_raw_top_k_allowed: Literal[20] = 20
    maximum_eligible_items_allowed: Literal[20] = 20
    maximum_context_prefix_characters_exclusive: Literal[133880] = 133880
    unretrievable_cases_allowed: Literal[0] = 0
    filter_ineligible_cases_allowed: Literal[0] = 0


class Phase5RrfHybridCandidateExperimentReport(ContractModel):
    report_version: Literal[
        "phase5-rrf-hybrid-candidate-experiment-v1"
    ] = "phase5-rrf-hybrid-candidate-experiment-v1"

    evidence_class: Literal[
        "intervention_tuning_only"
    ] = "intervention_tuning_only"

    lexical_baseline_sha256: Literal[
        "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"
    ] = _LEXICAL_BASELINE_SHA256

    bm25_experiment_sha256: Literal[
        "ef58106aef6087f7e4761df6afbe1e0c3819ffa8304c7b11c4c446faa6437370"
    ] = _BM25_EXPERIMENT_SHA256

    candidate_config: Phase5RrfHybridCandidateConfig
    candidate_configuration_id: Sha256
    promotion_gate: Phase5RrfPromotionGate

    tuning_case_count: Literal[18] = 18
    answerable_case_count: Literal[15] = 15
    refusal_case_count: Literal[3] = 3
    required_evidence_reference_count: Literal[18] = 18

    lexical_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    bm25_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    hybrid_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    hybrid_maximum_minimum_raw_top_k: int | None = Field(
        default=None,
        ge=1,
    )
    hybrid_maximum_minimum_eligible_items: int | None = Field(
        default=None,
        ge=1,
    )
    hybrid_maximum_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    improved_vs_lexical_case_count: int = Field(ge=0)
    unchanged_vs_lexical_case_count: int = Field(ge=0)
    regressed_vs_lexical_case_count: int = Field(ge=0)
    unretrievable_case_count: int = Field(ge=0)
    filter_ineligible_case_count: int = Field(ge=0)

    case_comparisons: tuple[
        Phase5RrfCaseComparison,
        ...,
    ] = Field(min_length=15, max_length=15)

    promotion_gate_passed: bool
    promotion_gate_failures: tuple[NonEmptyStr, ...]

    development_gold_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False

    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if self.candidate_configuration_id != (
            self.candidate_config.configuration_id
        ):
            raise ValueError(
                "hybrid candidate configuration identity mismatch"
            )

        if (
            self.improved_vs_lexical_case_count
            + self.unchanged_vs_lexical_case_count
            + self.regressed_vs_lexical_case_count
            + self.unretrievable_case_count
            != self.answerable_case_count
        ):
            raise ValueError(
                "hybrid case outcome counts do not reconcile"
            )

        for curve in (
            self.lexical_top_k_curve,
            self.bm25_top_k_curve,
            self.hybrid_top_k_curve,
        ):
            if tuple(point.top_k for point in curve) != _TOP_K_CURVE:
                raise ValueError(
                    "hybrid experiment top-k curve drifted"
                )

        if self.promotion_gate_passed != (
            len(self.promotion_gate_failures) == 0
        ):
            raise ValueError(
                "promotion gate result does not reconcile with failures"
            )

        if (
            self.development_gold_used
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.runtime_retriever_changed
            or self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError(
                "hybrid candidate experiment overclaimed execution state"
            )

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_json_bytes(
    path: Path,
    expected_sha256: str,
) -> bytes:
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(
            f"frozen experiment artifact hash mismatch: {path}"
        )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    expected_sidecar = (
        f"{expected_sha256}  {path.name}"
    )

    if sidecar.read_text(
        encoding="utf-8"
    ).strip() != expected_sidecar:
        raise ValueError(
            f"frozen experiment artifact sidecar mismatch: {path}"
        )

    return content


def _load_prior_evidence(
    repo_root: Path,
) -> tuple[
    Phase5TuningRetrievalCharacterizationReport,
    Phase5Bm25CandidateExperimentReport,
]:
    lexical = (
        Phase5TuningRetrievalCharacterizationReport
        .model_validate_json(
            _verified_json_bytes(
                repo_root / _LEXICAL_BASELINE_PATH,
                _LEXICAL_BASELINE_SHA256,
            )
        )
    )

    bm25 = (
        Phase5Bm25CandidateExperimentReport
        .model_validate_json(
            _verified_json_bytes(
                repo_root / _BM25_EXPERIMENT_PATH,
                _BM25_EXPERIMENT_SHA256,
            )
        )
    )

    if (
        bm25.baseline_characterization_sha256
        != _LEXICAL_BASELINE_SHA256
    ):
        raise ValueError(
            "BM25 experiment is not bound to the expected lexical baseline"
        )

    return lexical, bm25


def _fuse_rankings(
    *,
    lexical_items: tuple[RetrievedEvidence, ...],
    bm25_items: tuple[RetrievedEvidence, ...],
    config: Phase5RrfHybridCandidateConfig,
) -> tuple[RetrievedEvidence, ...]:
    lexical_by_id = {
        item.evidence_id: item
        for item in lexical_items
    }

    bm25_by_id = {
        item.evidence_id: item
        for item in bm25_items
    }

    lexical_rank = {
        item.evidence_id: item.rank
        for item in lexical_items
    }

    bm25_rank = {
        item.evidence_id: item.rank
        for item in bm25_items
    }

    evidence_ids = (
        set(lexical_by_id)
        | set(bm25_by_id)
    )

    fused: list[
        tuple[
            float,
            RetrievedEvidence,
        ]
    ] = []

    for evidence_id in evidence_ids:
        score = 0.0

        if evidence_id in lexical_rank:
            score += (
                config.lexical_weight
                / (
                    config.fusion_constant
                    + lexical_rank[evidence_id]
                )
            )

        if evidence_id in bm25_rank:
            score += (
                config.bm25_weight
                / (
                    config.fusion_constant
                    + bm25_rank[evidence_id]
                )
            )

        source = lexical_by_id.get(
            evidence_id,
            bm25_by_id[evidence_id],
        )

        fused.append(
            (
                score,
                source,
            )
        )

    fused.sort(
        key=lambda item: (
            -item[0],
            item[1].evidence_id,
        )
    )

    return tuple(
        RetrievedEvidence(
            evidence_id=source.evidence_id,
            source_ids=source.source_ids,
            document_ids=source.document_ids,
            content=source.content,
            rank=rank,
            score=score,
            authority_level=source.authority_level,
            source_state=source.source_state,
            product_scope=source.product_scope,
            api_version_or_snapshot=(
                source.api_version_or_snapshot
            ),
            synthetic_overlay=source.synthetic_overlay,
            eligible_as_final_citation=(
                source.eligible_as_final_citation
            ),
        )
        for rank, (
            score,
            source,
        ) in enumerate(
            fused[
                : config.characterization_top_k
            ],
            start=1,
        )
    )


def _hybrid_curve(
    comparisons: tuple[
        Phase5RrfCaseComparison,
        ...,
    ],
) -> tuple[
    Phase5TopKCurvePoint,
    ...,
]:
    reference_count = sum(
        comparison.required_evidence_count
        for comparison in comparisons
    )

    points: list[
        Phase5TopKCurvePoint
    ] = []

    for top_k in _TOP_K_CURVE:
        full_case_count = 0
        retrieved_reference_count = 0

        for comparison in comparisons:
            ranks = tuple(
                item.raw_rank
                for item in comparison.hybrid_required_evidence_ranks
            )

            retrieved_reference_count += sum(
                rank is not None
                and rank <= top_k
                for rank in ranks
            )

            if all(
                rank is not None
                and rank <= top_k
                for rank in ranks
            ):
                full_case_count += 1

        points.append(
            Phase5TopKCurvePoint(
                top_k=top_k,
                applicable_case_count=len(
                    comparisons
                ),
                full_gold_case_count=(
                    full_case_count
                ),
                full_gold_case_rate=(
                    full_case_count
                    / len(comparisons)
                ),
                required_evidence_reference_count=(
                    reference_count
                ),
                retrieved_required_evidence_count=(
                    retrieved_reference_count
                ),
                micro_gold_recall=(
                    retrieved_reference_count
                    / reference_count
                ),
            )
        )

    return tuple(points)


def _gate_failures(
    *,
    hybrid_curve: tuple[Phase5TopKCurvePoint, ...],
    maximum_raw_top_k: int | None,
    maximum_eligible_items: int | None,
    maximum_context_prefix: int | None,
    unretrievable_case_count: int,
    filter_ineligible_case_count: int,
) -> tuple[str, ...]:
    point_20 = next(
        point
        for point in hybrid_curve
        if point.top_k == 20
    )

    failures: list[str] = []

    if point_20.full_gold_case_count != 15:
        failures.append(
            "full_gold_cases_at_k20_below_15"
        )

    if abs(
        point_20.micro_gold_recall
        - 1.0
    ) > 1e-12:
        failures.append(
            "micro_gold_recall_at_k20_below_1"
        )

    if (
        maximum_raw_top_k is None
        or maximum_raw_top_k > 20
    ):
        failures.append(
            "maximum_raw_top_k_above_20"
        )

    if (
        maximum_eligible_items is None
        or maximum_eligible_items > 20
    ):
        failures.append(
            "maximum_eligible_items_above_20"
        )

    if (
        maximum_context_prefix is None
        or maximum_context_prefix >= 133880
    ):
        failures.append(
            "maximum_context_prefix_not_below_lexical_baseline"
        )

    if unretrievable_case_count != 0:
        failures.append(
            "unretrievable_gold_present"
        )

    if filter_ineligible_case_count != 0:
        failures.append(
            "filter_ineligible_gold_present"
        )

    return tuple(failures)


async def _build_report(
    repo_root: Path,
) -> Phase5RrfHybridCandidateExperimentReport:
    lexical_evidence, bm25_evidence = (
        _load_prior_evidence(
            repo_root
        )
    )

    cases = _load_tuning_cases(
        repo_root
    )

    (
        documents,
        _corpus_evidence_ids,
    ) = _load_indexed_documents(
        repo_root
    )

    answerable_cases = {
        case.case_id: case
        for case in cases
        if case.expected_response_mode
        is not ResponseMode.REFUSE
    }

    if len(answerable_cases) != 15:
        raise ValueError(
            "hybrid experiment requires 15 answerable TUNING cases"
        )

    lexical_cases = {
        result.case_id: result
        for result in lexical_evidence.case_results
        if result.expected_response_mode
        is not ResponseMode.REFUSE
    }

    bm25_cases = {
        result.case_id: result
        for result in bm25_evidence.case_comparisons
    }

    if (
        set(answerable_cases)
        != set(lexical_cases)
        or set(answerable_cases)
        != set(bm25_cases)
    ):
        raise ValueError(
            "lexical/BM25/hybrid TUNING case identities differ"
        )

    config = (
        Phase5RrfHybridCandidateConfig()
    )

    lexical_retriever = LexicalRetriever(
        config=RetrievalConfig(
            retriever_id="lexical-v1",
            top_k=(
                config.characterization_top_k
            ),
        ),
        documents=documents,
    )

    bm25_retriever = _Bm25CandidateRetriever(
        config=Phase5Bm25CandidateConfig(),
        documents=documents,
    )

    source_filter = (
        CurrentGithubRestSourcePolicyFilter(
            config=SourcePolicyConfig(
                policy_id="github-rest-current-v1"
            )
        )
    )

    comparisons: list[
        Phase5RrfCaseComparison
    ] = []

    for case_id in sorted(
        answerable_cases
    ):
        case = answerable_cases[
            case_id
        ]

        lexical_case = lexical_cases[
            case_id
        ]

        bm25_case = bm25_cases[
            case_id
        ]

        if (
            lexical_case.minimum_raw_top_k_for_full_gold is None
            or lexical_case.minimum_eligible_items_for_full_gold is None
            or lexical_case.context_prefix_characters_for_full_gold is None
            or bm25_case.candidate_minimum_raw_top_k is None
            or bm25_case.candidate_minimum_eligible_items is None
            or bm25_case.candidate_context_prefix_characters is None
        ):
            raise ValueError(
                "prior evidence lacks complete answerable-case floors"
            )

        lexical_items = (
            await lexical_retriever.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=(
                        config.characterization_top_k
                    ),
                )
            )
        ).items

        bm25_items = (
            bm25_retriever.retrieve(
                case.query
            )
        )

        hybrid_items = _fuse_rankings(
            lexical_items=lexical_items,
            bm25_items=bm25_items,
            config=config,
        )

        filtered = await source_filter.apply(
            SourceFilterRequest(
                candidates=hybrid_items
            )
        )

        raw_rank_by_id = {
            item.evidence_id: item.rank
            for item in hybrid_items
        }

        eligible_rank_by_id = {
            item.evidence_id: index
            for index, item in enumerate(
                filtered.eligible,
                start=1,
            )
        }

        rank_records = tuple(
            Phase5RrfRequiredEvidenceRank(
                evidence_id=evidence_id,
                raw_rank=raw_rank_by_id.get(
                    evidence_id
                ),
                eligible_rank=(
                    eligible_rank_by_id.get(
                        evidence_id
                    )
                ),
                survived_source_filter=(
                    evidence_id
                    in eligible_rank_by_id
                ),
            )
            for evidence_id
            in case.required_evidence_ids
        )

        full_retrievable = all(
            item.raw_rank is not None
            for item in rank_records
        )

        full_filter_eligible = all(
            item.eligible_rank is not None
            for item in rank_records
        )

        hybrid_raw: int | None = None

        if full_retrievable:
            hybrid_raw = max(
                cast(
                    int,
                    item.raw_rank,
                )
                for item in rank_records
            )

        hybrid_eligible: int | None = None
        hybrid_context: int | None = None

        if full_filter_eligible:
            hybrid_eligible = max(
                cast(
                    int,
                    item.eligible_rank,
                )
                for item in rank_records
            )

            hybrid_context = (
                _context_prefix_characters(
                    cast(
                        tuple[object, ...],
                        filtered.eligible,
                    ),
                    hybrid_eligible,
                )
            )

        lexical_raw = (
            lexical_case.minimum_raw_top_k_for_full_gold
        )

        if hybrid_raw is None:
            lexical_rank_outcome: Literal[
                "improved",
                "unchanged",
                "regressed",
                "unretrievable",
            ] = "unretrievable"
        elif hybrid_raw < lexical_raw:
            lexical_rank_outcome = "improved"
        elif hybrid_raw == lexical_raw:
            lexical_rank_outcome = "unchanged"
        else:
            lexical_rank_outcome = "regressed"

        comparisons.append(
            Phase5RrfCaseComparison(
                case_id=case_id,
                required_evidence_count=len(
                    case.required_evidence_ids
                ),
                lexical_minimum_raw_top_k=(
                    lexical_raw
                ),
                bm25_minimum_raw_top_k=(
                    bm25_case.candidate_minimum_raw_top_k
                ),
                hybrid_minimum_raw_top_k=(
                    hybrid_raw
                ),
                lexical_minimum_eligible_items=(
                    lexical_case.minimum_eligible_items_for_full_gold
                ),
                bm25_minimum_eligible_items=(
                    bm25_case.candidate_minimum_eligible_items
                ),
                hybrid_minimum_eligible_items=(
                    hybrid_eligible
                ),
                lexical_context_prefix_characters=(
                    lexical_case.context_prefix_characters_for_full_gold
                ),
                bm25_context_prefix_characters=(
                    bm25_case.candidate_context_prefix_characters
                ),
                hybrid_context_prefix_characters=(
                    hybrid_context
                ),
                hybrid_required_evidence_ranks=(
                    rank_records
                ),
                full_gold_retrievable=(
                    full_retrievable
                ),
                full_gold_filter_eligible=(
                    full_filter_eligible
                ),
                lexical_rank_outcome=(
                    lexical_rank_outcome
                ),
            )
        )

    typed_comparisons = tuple(
        comparisons
    )

    all_retrievable = all(
        comparison.full_gold_retrievable
        for comparison in typed_comparisons
    )

    all_filter_eligible = all(
        comparison.full_gold_filter_eligible
        for comparison in typed_comparisons
    )

    maximum_raw: int | None = None

    if all_retrievable:
        maximum_raw = max(
            cast(
                int,
                comparison.hybrid_minimum_raw_top_k,
            )
            for comparison in typed_comparisons
        )

    maximum_eligible: int | None = None
    maximum_context: int | None = None

    if all_filter_eligible:
        maximum_eligible = max(
            cast(
                int,
                comparison.hybrid_minimum_eligible_items,
            )
            for comparison in typed_comparisons
        )

        maximum_context = max(
            cast(
                int,
                comparison.hybrid_context_prefix_characters,
            )
            for comparison in typed_comparisons
        )

    hybrid_curve = _hybrid_curve(
        typed_comparisons
    )

    unretrievable_count = sum(
        not comparison.full_gold_retrievable
        for comparison in typed_comparisons
    )

    filter_ineligible_count = sum(
        not comparison.full_gold_filter_eligible
        for comparison in typed_comparisons
    )

    failures = _gate_failures(
        hybrid_curve=hybrid_curve,
        maximum_raw_top_k=maximum_raw,
        maximum_eligible_items=maximum_eligible,
        maximum_context_prefix=maximum_context,
        unretrievable_case_count=(
            unretrievable_count
        ),
        filter_ineligible_case_count=(
            filter_ineligible_count
        ),
    )

    return Phase5RrfHybridCandidateExperimentReport(
        candidate_config=config,
        candidate_configuration_id=(
            config.configuration_id
        ),
        promotion_gate=(
            Phase5RrfPromotionGate()
        ),
        lexical_top_k_curve=(
            lexical_evidence.top_k_curve
        ),
        bm25_top_k_curve=(
            bm25_evidence.candidate_top_k_curve
        ),
        hybrid_top_k_curve=(
            hybrid_curve
        ),
        hybrid_maximum_minimum_raw_top_k=(
            maximum_raw
        ),
        hybrid_maximum_minimum_eligible_items=(
            maximum_eligible
        ),
        hybrid_maximum_context_prefix_characters=(
            maximum_context
        ),
        improved_vs_lexical_case_count=sum(
            comparison.lexical_rank_outcome
            == "improved"
            for comparison in typed_comparisons
        ),
        unchanged_vs_lexical_case_count=sum(
            comparison.lexical_rank_outcome
            == "unchanged"
            for comparison in typed_comparisons
        ),
        regressed_vs_lexical_case_count=sum(
            comparison.lexical_rank_outcome
            == "regressed"
            for comparison in typed_comparisons
        ),
        unretrievable_case_count=(
            unretrievable_count
        ),
        filter_ineligible_case_count=(
            filter_ineligible_count
        ),
        case_comparisons=(
            typed_comparisons
        ),
        promotion_gate_passed=(
            len(failures) == 0
        ),
        promotion_gate_failures=(
            failures
        ),
    )


def materialize_phase5_rrf_hybrid_candidate_experiment(
    repo_root: Path,
) -> tuple[
    Phase5RrfHybridCandidateExperimentReport,
    str,
]:
    report = asyncio.run(
        _build_report(
            repo_root
        )
    )

    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )

    return (
        report,
        digest,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    report, digest = (
        materialize_phase5_rrf_hybrid_candidate_experiment(
            repo_root
        )
    )

    print(
        "PHASE5_RRF_HYBRID_EXPERIMENT_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_RRF_HYBRID_CONFIGURATION_ID="
        f"{report.candidate_configuration_id}"
    )

    for lexical, bm25, hybrid in zip(
        report.lexical_top_k_curve,
        report.bm25_top_k_curve,
        report.hybrid_top_k_curve,
        strict=True,
    ):
        print(
            "PHASE5_RRF_HYBRID_COMPARISON="
            f"k:{hybrid.top_k},"
            f"lexical_full:{lexical.full_gold_case_count}/15,"
            f"bm25_full:{bm25.full_gold_case_count}/15,"
            f"hybrid_full:{hybrid.full_gold_case_count}/15,"
            f"lexical_micro:{lexical.micro_gold_recall:.6f},"
            f"bm25_micro:{bm25.micro_gold_recall:.6f},"
            f"hybrid_micro:{hybrid.micro_gold_recall:.6f}"
        )

    print(
        "PHASE5_RRF_HYBRID_CASE_OUTCOMES="
        f"improved:{report.improved_vs_lexical_case_count},"
        f"unchanged:{report.unchanged_vs_lexical_case_count},"
        f"regressed:{report.regressed_vs_lexical_case_count},"
        f"unretrievable:{report.unretrievable_case_count},"
        f"filter_ineligible:{report.filter_ineligible_case_count}"
    )

    print(
        "PHASE5_RRF_HYBRID_MAX_MIN_RAW_TOP_K="
        f"{report.hybrid_maximum_minimum_raw_top_k}"
    )
    print(
        "PHASE5_RRF_HYBRID_MAX_MIN_ELIGIBLE_ITEMS="
        f"{report.hybrid_maximum_minimum_eligible_items}"
    )
    print(
        "PHASE5_RRF_HYBRID_MAX_CONTEXT_PREFIX_CHARACTERS="
        f"{report.hybrid_maximum_context_prefix_characters}"
    )
    print(
        "PHASE5_RRF_HYBRID_PROMOTION_GATE_PASSED="
        f"{str(report.promotion_gate_passed).lower()}"
    )

    for failure in report.promotion_gate_failures:
        print(
            "PHASE5_RRF_HYBRID_PROMOTION_GATE_FAILURE="
            f"{failure}"
        )

    print(
        "PHASE5_RETRIEVAL_CONFIGURATION_SELECTED=false"
    )
    print(
        "PHASE5_RUNTIME_RETRIEVER_CHANGED=false"
    )
    print(
        "PHASE5_PROVIDER_INVOKED=false"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED=false"
    )
    print(
        "PHASE5_B0_EXECUTED=false"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false"
    )


if __name__ == "__main__":
    main()
