"""Fixed binary-IDF retrieval candidate experiment for Phase 5.

Hypothesis:
- plain lexical overlap underweights rare discriminative query terms;
- BM25 improves rarity weighting but can over-penalize long operation-core chunks;
- binary IDF-weighted overlap should preserve rarity weighting without term-frequency
  or document-length normalization.

Evaluation-only. No runtime component is changed, no DEVELOPMENT gold is used,
no HELD_OUT outcome is exposed, no provider is invoked, and B0 remains
unauthorized.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
from collections import Counter
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import (
    CanonicalConfigModel,
    SourcePolicyConfig,
)
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.runtime import (
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import _tokens
from rag_reliability.evaluation.retrieval_characterization import (
    Phase5TopKCurvePoint,
    _context_prefix_characters,
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateExperimentReport,
)
from rag_reliability.runtime.filtering import (
    CurrentGithubRestSourcePolicyFilter,
)
from rag_reliability.runtime.models import IndexedDocument

_RRF_BASELINE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_rrf_hybrid_candidate_experiment_v1.json"
)

_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_binary_idf_candidate_experiment_v1.json"
)

_RRF_BASELINE_SHA256: Literal[
    "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
] = "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"

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


class Phase5BinaryIdfCandidateConfig(CanonicalConfigModel):
    """One fixed binary-IDF candidate. No parameter sweep."""

    candidate_version: Literal[
        "phase5-binary-idf-candidate-v1"
    ] = "phase5-binary-idf-candidate-v1"

    retriever_id: Literal[
        "binary-idf-evaluation-candidate-v1"
    ] = "binary-idf-evaluation-candidate-v1"

    characterization_top_k: Literal[1333] = 1333

    idf_formula: Literal[
        "log_n_plus_1_over_df_plus_1_plus_1"
    ] = "log_n_plus_1_over_df_plus_1_plus_1"

    term_frequency_used: Literal[False] = False
    document_length_normalization_used: Literal[False] = False
    parameter_sweep_used: Literal[False] = False
    tuning_parameter_optimization_used: Literal[False] = False


class Phase5BinaryIdfRequiredEvidenceRank(ContractModel):
    evidence_id: NonEmptyStr
    raw_rank: int | None = Field(default=None, ge=1)
    eligible_rank: int | None = Field(default=None, ge=1)
    survived_source_filter: bool

    @model_validator(mode="after")
    def validate_rank_boundary(self) -> Self:
        if self.eligible_rank is not None and self.raw_rank is None:
            raise ValueError(
                "eligible evidence cannot exist without raw candidate rank"
            )

        if self.survived_source_filter != (self.eligible_rank is not None):
            raise ValueError(
                "source-filter survival does not reconcile with eligible rank"
            )

        return self


class Phase5BinaryIdfCaseComparison(ContractModel):
    case_id: NonEmptyStr
    required_evidence_count: int = Field(ge=1)

    rrf_minimum_raw_top_k: int = Field(ge=1)
    candidate_minimum_raw_top_k: int | None = Field(default=None, ge=1)

    rrf_minimum_eligible_items: int = Field(ge=1)
    candidate_minimum_eligible_items: int | None = Field(default=None, ge=1)

    rrf_context_prefix_characters: int = Field(ge=1)
    candidate_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    candidate_required_evidence_ranks: tuple[
        Phase5BinaryIdfRequiredEvidenceRank,
        ...,
    ]

    full_gold_retrievable: bool
    full_gold_filter_eligible: bool

    rrf_rank_outcome: Literal[
        "improved",
        "unchanged",
        "regressed",
        "unretrievable",
    ]

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if (
            len(self.candidate_required_evidence_ranks)
            != self.required_evidence_count
        ):
            raise ValueError(
                "candidate required-evidence rank count does not reconcile"
            )

        if self.full_gold_retrievable != (
            self.candidate_minimum_raw_top_k is not None
        ):
            raise ValueError(
                "candidate raw rank does not reconcile with retrievability"
            )

        if self.full_gold_filter_eligible != (
            self.candidate_minimum_eligible_items is not None
            and self.candidate_context_prefix_characters is not None
        ):
            raise ValueError(
                "candidate eligible/context state does not reconcile"
            )

        if not self.full_gold_retrievable:
            expected = "unretrievable"
        elif (
            cast(int, self.candidate_minimum_raw_top_k)
            < self.rrf_minimum_raw_top_k
        ):
            expected = "improved"
        elif (
            cast(int, self.candidate_minimum_raw_top_k)
            == self.rrf_minimum_raw_top_k
        ):
            expected = "unchanged"
        else:
            expected = "regressed"

        if self.rrf_rank_outcome != expected:
            raise ValueError(
                "candidate/RRF rank outcome does not reconcile"
            )

        return self


class Phase5BinaryIdfPromotionGate(ContractModel):
    """Predeclared before candidate execution."""

    full_gold_cases_at_k20_required: Literal[15] = 15
    micro_gold_recall_at_k20_required: Literal["1.0"] = "1.0"

    maximum_raw_top_k_allowed: Literal[20] = 20
    maximum_eligible_items_allowed: Literal[20] = 20

    maximum_context_prefix_characters_exclusive: Literal[
        102463
    ] = 102463

    unretrievable_cases_allowed: Literal[0] = 0
    filter_ineligible_cases_allowed: Literal[0] = 0


class Phase5BinaryIdfCandidateExperimentReport(ContractModel):
    report_version: Literal[
        "phase5-binary-idf-candidate-experiment-v1"
    ] = "phase5-binary-idf-candidate-experiment-v1"

    evidence_class: Literal[
        "intervention_tuning_only"
    ] = "intervention_tuning_only"

    rrf_baseline_sha256: Literal[
        "b9fe4f071d77e6ff56c0066c16f4f79f8da149f55cf82850e98549d6dd034179"
    ] = _RRF_BASELINE_SHA256

    candidate_config: Phase5BinaryIdfCandidateConfig
    candidate_configuration_id: Sha256
    promotion_gate: Phase5BinaryIdfPromotionGate

    tuning_case_count: Literal[18] = 18
    answerable_case_count: Literal[15] = 15
    refusal_case_count: Literal[3] = 3
    required_evidence_reference_count: Literal[18] = 18

    rrf_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    candidate_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    rrf_maximum_minimum_raw_top_k: Literal[23] = 23
    candidate_maximum_minimum_raw_top_k: int | None = Field(
        default=None,
        ge=1,
    )

    rrf_maximum_minimum_eligible_items: Literal[21] = 21
    candidate_maximum_minimum_eligible_items: int | None = Field(
        default=None,
        ge=1,
    )

    rrf_maximum_context_prefix_characters: Literal[102463] = 102463
    candidate_maximum_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    improved_vs_rrf_case_count: int = Field(ge=0)
    unchanged_vs_rrf_case_count: int = Field(ge=0)
    regressed_vs_rrf_case_count: int = Field(ge=0)
    unretrievable_case_count: int = Field(ge=0)
    filter_ineligible_case_count: int = Field(ge=0)

    case_comparisons: tuple[
        Phase5BinaryIdfCaseComparison,
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
                "candidate configuration identity mismatch"
            )

        if (
            self.improved_vs_rrf_case_count
            + self.unchanged_vs_rrf_case_count
            + self.regressed_vs_rrf_case_count
            + self.unretrievable_case_count
            != self.answerable_case_count
        ):
            raise ValueError(
                "candidate case-outcome counts do not reconcile"
            )

        for curve in (
            self.rrf_top_k_curve,
            self.candidate_top_k_curve,
        ):
            if tuple(point.top_k for point in curve) != _TOP_K_CURVE:
                raise ValueError(
                    "candidate experiment top-k curve drifted"
                )

        if self.promotion_gate_passed != (
            len(self.promotion_gate_failures) == 0
        ):
            raise ValueError(
                "promotion gate result does not reconcile"
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
                "candidate experiment overclaimed execution state"
            )

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _load_rrf_baseline(
    repo_root: Path,
) -> Phase5RrfHybridCandidateExperimentReport:
    path = repo_root / _RRF_BASELINE_PATH
    content = path.read_bytes()

    if _sha256_bytes(content) != _RRF_BASELINE_SHA256:
        raise ValueError(
            "RRF baseline experiment hash mismatch"
        )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    expected_sidecar = (
        f"{_RRF_BASELINE_SHA256}  {path.name}"
    )

    if sidecar.read_text(
        encoding="utf-8"
    ).strip() != expected_sidecar:
        raise ValueError(
            "RRF baseline sidecar mismatch"
        )

    report = (
        Phase5RrfHybridCandidateExperimentReport
        .model_validate_json(content)
    )

    if report.development_gold_used:
        raise ValueError(
            "RRF baseline violated DEVELOPMENT boundary"
        )

    if report.held_out_outcomes_exposed:
        raise ValueError(
            "RRF baseline exposed HELD_OUT"
        )

    return report


class _BinaryIdfCandidateRetriever:
    """Evaluation-only binary IDF scorer."""

    def __init__(
        self,
        *,
        config: Phase5BinaryIdfCandidateConfig,
        documents: tuple[IndexedDocument, ...],
    ) -> None:
        self._config = config
        self._documents = documents

        document_token_sets = tuple(
            frozenset(
                _tokens(document.content)
            )
            for document in documents
        )

        self._document_token_sets = (
            document_token_sets
        )

        document_frequency: Counter[str] = Counter()

        for tokens in document_token_sets:
            document_frequency.update(tokens)

        self._document_frequency = document_frequency

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    def retrieve(
        self,
        query: str,
    ) -> tuple[RetrievedEvidence, ...]:
        query_terms = tuple(
            sorted(
                set(
                    _tokens(query)
                )
            )
        )

        if not query_terms:
            return ()

        document_count = len(
            self._documents
        )

        scored: list[
            tuple[
                float,
                IndexedDocument,
            ]
        ] = []

        for (
            document,
            document_tokens,
        ) in zip(
            self._documents,
            self._document_token_sets,
            strict=True,
        ):
            score = 0.0

            for term in query_terms:
                if term not in document_tokens:
                    continue

                document_frequency = (
                    self._document_frequency[
                        term
                    ]
                )

                score += (
                    math.log(
                        (
                            document_count
                            + 1
                        )
                        / (
                            document_frequency
                            + 1
                        )
                    )
                    + 1.0
                )

            if score > 0.0:
                scored.append(
                    (
                        score,
                        document,
                    )
                )

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].evidence_id,
            )
        )

        return tuple(
            RetrievedEvidence(
                evidence_id=document.evidence_id,
                source_ids=document.source_ids,
                document_ids=document.document_ids,
                content=document.content,
                rank=rank,
                score=score,
                authority_level=document.authority_level,
                source_state=document.source_state,
                product_scope=document.product_scope,
                api_version_or_snapshot=(
                    document.api_version_or_snapshot
                ),
                synthetic_overlay=document.synthetic_overlay,
                eligible_as_final_citation=(
                    document.eligible_as_final_citation
                ),
            )
            for rank, (
                score,
                document,
            ) in enumerate(
                scored[
                    : self._config.characterization_top_k
                ],
                start=1,
            )
        )


def _candidate_curve(
    comparisons: tuple[
        Phase5BinaryIdfCaseComparison,
        ...,
    ],
) -> tuple[Phase5TopKCurvePoint, ...]:
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
                for item
                in comparison.candidate_required_evidence_ranks
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
    candidate_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ],
    maximum_raw_top_k: int | None,
    maximum_eligible_items: int | None,
    maximum_context_prefix: int | None,
    unretrievable_case_count: int,
    filter_ineligible_case_count: int,
) -> tuple[str, ...]:
    point_20 = next(
        point
        for point in candidate_curve
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
        or maximum_context_prefix >= 102463
    ):
        failures.append(
            "maximum_context_prefix_not_below_rrf_baseline"
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
) -> Phase5BinaryIdfCandidateExperimentReport:
    rrf_baseline = _load_rrf_baseline(
        repo_root
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
            "binary-IDF experiment requires 15 answerable TUNING cases"
        )

    rrf_cases = {
        comparison.case_id: comparison
        for comparison in rrf_baseline.case_comparisons
    }

    if set(answerable_cases) != set(
        rrf_cases
    ):
        raise ValueError(
            "RRF/binary-IDF TUNING case identities differ"
        )

    config = Phase5BinaryIdfCandidateConfig()

    candidate = _BinaryIdfCandidateRetriever(
        config=config,
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
        Phase5BinaryIdfCaseComparison
    ] = []

    for case_id in sorted(
        answerable_cases
    ):
        case = answerable_cases[
            case_id
        ]

        rrf_case = rrf_cases[
            case_id
        ]

        if (
            rrf_case.hybrid_minimum_raw_top_k is None
            or rrf_case.hybrid_minimum_eligible_items is None
            or rrf_case.hybrid_context_prefix_characters is None
        ):
            raise ValueError(
                "RRF baseline lacks complete answerable-case floors"
            )

        raw_items = candidate.retrieve(
            case.query
        )

        filtered = await source_filter.apply(
            SourceFilterRequest(
                candidates=raw_items
            )
        )

        raw_rank_by_id = {
            item.evidence_id: item.rank
            for item in raw_items
        }

        eligible_rank_by_id = {
            item.evidence_id: index
            for index, item in enumerate(
                filtered.eligible,
                start=1,
            )
        }

        rank_records = tuple(
            Phase5BinaryIdfRequiredEvidenceRank(
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

        candidate_raw: int | None = None

        if full_retrievable:
            candidate_raw = max(
                cast(
                    int,
                    item.raw_rank,
                )
                for item in rank_records
            )

        candidate_eligible: int | None = None
        candidate_context: int | None = None

        if full_filter_eligible:
            candidate_eligible = max(
                cast(
                    int,
                    item.eligible_rank,
                )
                for item in rank_records
            )

            candidate_context = (
                _context_prefix_characters(
                    cast(
                        tuple[object, ...],
                        filtered.eligible,
                    ),
                    candidate_eligible,
                )
            )

        rrf_raw = (
            rrf_case.hybrid_minimum_raw_top_k
        )

        if candidate_raw is None:
            outcome: Literal[
                "improved",
                "unchanged",
                "regressed",
                "unretrievable",
            ] = "unretrievable"
        elif candidate_raw < rrf_raw:
            outcome = "improved"
        elif candidate_raw == rrf_raw:
            outcome = "unchanged"
        else:
            outcome = "regressed"

        comparisons.append(
            Phase5BinaryIdfCaseComparison(
                case_id=case_id,
                required_evidence_count=len(
                    case.required_evidence_ids
                ),
                rrf_minimum_raw_top_k=(
                    rrf_raw
                ),
                candidate_minimum_raw_top_k=(
                    candidate_raw
                ),
                rrf_minimum_eligible_items=(
                    rrf_case.hybrid_minimum_eligible_items
                ),
                candidate_minimum_eligible_items=(
                    candidate_eligible
                ),
                rrf_context_prefix_characters=(
                    rrf_case.hybrid_context_prefix_characters
                ),
                candidate_context_prefix_characters=(
                    candidate_context
                ),
                candidate_required_evidence_ranks=(
                    rank_records
                ),
                full_gold_retrievable=(
                    full_retrievable
                ),
                full_gold_filter_eligible=(
                    full_filter_eligible
                ),
                rrf_rank_outcome=(
                    outcome
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
                comparison.candidate_minimum_raw_top_k,
            )
            for comparison in typed_comparisons
        )

    maximum_eligible: int | None = None
    maximum_context: int | None = None

    if all_filter_eligible:
        maximum_eligible = max(
            cast(
                int,
                comparison.candidate_minimum_eligible_items,
            )
            for comparison in typed_comparisons
        )

        maximum_context = max(
            cast(
                int,
                comparison.candidate_context_prefix_characters,
            )
            for comparison in typed_comparisons
        )

    candidate_curve = _candidate_curve(
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
        candidate_curve=candidate_curve,
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

    return Phase5BinaryIdfCandidateExperimentReport(
        candidate_config=config,
        candidate_configuration_id=(
            config.configuration_id
        ),
        promotion_gate=(
            Phase5BinaryIdfPromotionGate()
        ),
        rrf_top_k_curve=(
            rrf_baseline.hybrid_top_k_curve
        ),
        candidate_top_k_curve=(
            candidate_curve
        ),
        candidate_maximum_minimum_raw_top_k=(
            maximum_raw
        ),
        candidate_maximum_minimum_eligible_items=(
            maximum_eligible
        ),
        candidate_maximum_context_prefix_characters=(
            maximum_context
        ),
        improved_vs_rrf_case_count=sum(
            comparison.rrf_rank_outcome
            == "improved"
            for comparison in typed_comparisons
        ),
        unchanged_vs_rrf_case_count=sum(
            comparison.rrf_rank_outcome
            == "unchanged"
            for comparison in typed_comparisons
        ),
        regressed_vs_rrf_case_count=sum(
            comparison.rrf_rank_outcome
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


def materialize_phase5_binary_idf_candidate_experiment(
    repo_root: Path,
) -> tuple[
    Phase5BinaryIdfCandidateExperimentReport,
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
        materialize_phase5_binary_idf_candidate_experiment(
            repo_root
        )
    )

    print(
        "PHASE5_BINARY_IDF_EXPERIMENT_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_BINARY_IDF_CONFIGURATION_ID="
        f"{report.candidate_configuration_id}"
    )

    for rrf, candidate in zip(
        report.rrf_top_k_curve,
        report.candidate_top_k_curve,
        strict=True,
    ):
        print(
            "PHASE5_BINARY_IDF_COMPARISON="
            f"k:{candidate.top_k},"
            f"rrf_full:{rrf.full_gold_case_count}/15,"
            f"candidate_full:{candidate.full_gold_case_count}/15,"
            f"rrf_micro:{rrf.micro_gold_recall:.6f},"
            f"candidate_micro:{candidate.micro_gold_recall:.6f}"
        )

    print(
        "PHASE5_BINARY_IDF_CASE_OUTCOMES="
        f"improved:{report.improved_vs_rrf_case_count},"
        f"unchanged:{report.unchanged_vs_rrf_case_count},"
        f"regressed:{report.regressed_vs_rrf_case_count},"
        f"unretrievable:{report.unretrievable_case_count},"
        f"filter_ineligible:{report.filter_ineligible_case_count}"
    )

    print(
        "PHASE5_BINARY_IDF_RRF_MAX_MIN_RAW_TOP_K="
        f"{report.rrf_maximum_minimum_raw_top_k}"
    )
    print(
        "PHASE5_BINARY_IDF_CANDIDATE_MAX_MIN_RAW_TOP_K="
        f"{report.candidate_maximum_minimum_raw_top_k}"
    )
    print(
        "PHASE5_BINARY_IDF_RRF_MAX_MIN_ELIGIBLE_ITEMS="
        f"{report.rrf_maximum_minimum_eligible_items}"
    )
    print(
        "PHASE5_BINARY_IDF_CANDIDATE_MAX_MIN_ELIGIBLE_ITEMS="
        f"{report.candidate_maximum_minimum_eligible_items}"
    )
    print(
        "PHASE5_BINARY_IDF_RRF_MAX_CONTEXT_PREFIX_CHARACTERS="
        f"{report.rrf_maximum_context_prefix_characters}"
    )
    print(
        "PHASE5_BINARY_IDF_CANDIDATE_MAX_CONTEXT_PREFIX_CHARACTERS="
        f"{report.candidate_maximum_context_prefix_characters}"
    )
    print(
        "PHASE5_BINARY_IDF_PROMOTION_GATE_PASSED="
        f"{str(report.promotion_gate_passed).lower()}"
    )

    for failure in report.promotion_gate_failures:
        print(
            "PHASE5_BINARY_IDF_PROMOTION_GATE_FAILURE="
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
