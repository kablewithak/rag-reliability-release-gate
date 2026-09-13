"""Fixed BM25 candidate experiment against the Phase 5 TUNING baseline.

This is an evaluation-only intervention. It compares one non-tuned BM25
candidate with the already-materialized lexical characterization on exactly the
same TUNING cases and frozen corpus. It does not mutate runtime configuration,
invoke a provider, access DEVELOPMENT gold, expose HELD_OUT, or authorize B0.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
from collections import Counter
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import CanonicalConfigModel, SourcePolicyConfig
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.runtime import (
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
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
from rag_reliability.runtime.models import IndexedDocument

_BASELINE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_tuning_retrieval_characterization_v1.json"
)

_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_bm25_candidate_experiment_v1.json"
)

_BASELINE_SHA256: Literal[
    "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"
] = "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")

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


class Phase5Bm25CandidateConfig(CanonicalConfigModel):
    """One fixed, non-swept BM25 candidate configuration."""

    candidate_version: Literal[
        "phase5-bm25-candidate-v1"
    ] = "phase5-bm25-candidate-v1"

    retriever_id: Literal[
        "bm25-evaluation-candidate-v1"
    ] = "bm25-evaluation-candidate-v1"

    top_k: Literal[1333] = 1333

    k1: float = Field(default=1.2, ge=1.2, le=1.2)
    b: float = Field(default=0.75, ge=0.75, le=0.75)

    parameter_sweep_used: Literal[False] = False
    tuning_parameter_optimization_used: Literal[False] = False


class Phase5Bm25RequiredEvidenceRank(ContractModel):
    evidence_id: NonEmptyStr
    raw_rank: int | None = Field(default=None, ge=1)
    eligible_rank: int | None = Field(default=None, ge=1)
    survived_source_filter: bool

    @model_validator(mode="after")
    def validate_rank_boundary(self) -> Self:
        if self.eligible_rank is not None and self.raw_rank is None:
            raise ValueError(
                "eligible evidence cannot exist without raw retrieval rank"
            )

        if self.survived_source_filter != (self.eligible_rank is not None):
            raise ValueError(
                "filter survival does not reconcile with eligible rank"
            )

        return self


class Phase5Bm25CaseComparison(ContractModel):
    case_id: NonEmptyStr
    required_evidence_count: int = Field(ge=1)

    baseline_minimum_raw_top_k: int = Field(ge=1)
    candidate_minimum_raw_top_k: int | None = Field(default=None, ge=1)

    baseline_minimum_eligible_items: int = Field(ge=1)
    candidate_minimum_eligible_items: int | None = Field(
        default=None,
        ge=1,
    )

    baseline_context_prefix_characters: int = Field(ge=1)
    candidate_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    candidate_required_evidence_ranks: tuple[
        Phase5Bm25RequiredEvidenceRank,
        ...,
    ]

    full_gold_retrievable: bool
    full_gold_filter_eligible: bool

    raw_rank_outcome: Literal[
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
                "candidate raw-rank floor does not reconcile with retrievability"
            )

        if self.full_gold_filter_eligible != (
            self.candidate_minimum_eligible_items is not None
            and self.candidate_context_prefix_characters is not None
        ):
            raise ValueError(
                "candidate eligible/context floors do not reconcile"
            )

        if not self.full_gold_retrievable:
            expected = "unretrievable"
        elif (
            cast(int, self.candidate_minimum_raw_top_k)
            < self.baseline_minimum_raw_top_k
        ):
            expected = "improved"
        elif (
            cast(int, self.candidate_minimum_raw_top_k)
            == self.baseline_minimum_raw_top_k
        ):
            expected = "unchanged"
        else:
            expected = "regressed"

        if self.raw_rank_outcome != expected:
            raise ValueError(
                "raw-rank outcome does not reconcile with before/after ranks"
            )

        return self


class Phase5Bm25CandidateExperimentReport(ContractModel):
    """Before/after TUNING evidence for one fixed BM25 candidate."""

    report_version: Literal[
        "phase5-bm25-candidate-experiment-v1"
    ] = "phase5-bm25-candidate-experiment-v1"

    evidence_class: Literal[
        "intervention_tuning_only"
    ] = "intervention_tuning_only"

    baseline_characterization_sha256: Literal[
        "c641483467147836b6cfcc80fc97022ac32cc7d4d7fac87e5428000d0010428e"
    ] = _BASELINE_SHA256

    candidate_configuration_id: Sha256
    candidate_config: Phase5Bm25CandidateConfig

    tuning_case_count: Literal[18] = 18
    answerable_case_count: Literal[15] = 15
    refusal_case_count: Literal[3] = 3

    required_evidence_reference_count: Literal[18] = 18
    unique_required_evidence_count: Literal[11] = 11

    baseline_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    candidate_top_k_curve: tuple[
        Phase5TopKCurvePoint,
        ...,
    ] = Field(min_length=10, max_length=10)

    baseline_maximum_minimum_raw_top_k: Literal[31] = 31
    candidate_maximum_minimum_raw_top_k: int | None = Field(
        default=None,
        ge=1,
    )

    baseline_maximum_minimum_eligible_items: Literal[26] = 26
    candidate_maximum_minimum_eligible_items: int | None = Field(
        default=None,
        ge=1,
    )

    baseline_maximum_context_prefix_characters: Literal[
        133880
    ] = 133880
    candidate_maximum_context_prefix_characters: int | None = Field(
        default=None,
        ge=1,
    )

    improved_case_count: int = Field(ge=0)
    unchanged_case_count: int = Field(ge=0)
    regressed_case_count: int = Field(ge=0)
    unretrievable_case_count: int = Field(ge=0)

    case_comparisons: tuple[
        Phase5Bm25CaseComparison,
        ...,
    ] = Field(min_length=15, max_length=15)

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
        if (
            self.improved_case_count
            + self.unchanged_case_count
            + self.regressed_case_count
            + self.unretrievable_case_count
            != self.answerable_case_count
        ):
            raise ValueError(
                "case-outcome counts do not reconcile"
            )

        if self.candidate_configuration_id != (
            self.candidate_config.configuration_id
        ):
            raise ValueError(
                "candidate configuration identity mismatch"
            )

        if tuple(
            point.top_k
            for point in self.baseline_top_k_curve
        ) != _TOP_K_CURVE:
            raise ValueError(
                "baseline top-k curve drifted"
            )

        if tuple(
            point.top_k
            for point in self.candidate_top_k_curve
        ) != _TOP_K_CURVE:
            raise ValueError(
                "candidate top-k curve drifted"
            )

        if self.development_gold_used:
            raise ValueError(
                "BM25 candidate experiment cannot use DEVELOPMENT gold"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "BM25 candidate experiment cannot expose HELD_OUT"
            )

        if self.provider_invoked:
            raise ValueError(
                "BM25 candidate experiment cannot invoke provider"
            )

        if self.runtime_retriever_changed:
            raise ValueError(
                "evaluation candidate cannot mutate runtime retriever"
            )

        if (
            self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
        ):
            raise ValueError(
                "candidate experiment cannot select runtime configuration"
            )

        if self.baseline_execution_authorized or self.b0_executed:
            raise ValueError(
                "candidate experiment cannot authorize or execute B0"
            )

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_baseline(
    repo_root: Path,
) -> Phase5TuningRetrievalCharacterizationReport:
    path = (
        repo_root
        / _BASELINE_PATH
    )

    content = path.read_bytes()

    if _sha256_bytes(content) != _BASELINE_SHA256:
        raise ValueError(
            "baseline retrieval characterization hash mismatch"
        )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    if sidecar.read_text(
        encoding="utf-8"
    ).strip() != (
        f"{_BASELINE_SHA256}  {path.name}"
    ):
        raise ValueError(
            "baseline retrieval characterization sidecar mismatch"
        )

    baseline = (
        Phase5TuningRetrievalCharacterizationReport
        .model_validate_json(
            content
        )
    )

    if baseline.development_gold_used_for_characterization:
        raise ValueError(
            "baseline characterization violated DEVELOPMENT boundary"
        )

    if baseline.held_out_outcomes_exposed:
        raise ValueError(
            "baseline characterization exposed HELD_OUT"
        )

    return baseline


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(
        _TOKEN_PATTERN.findall(
            text.casefold()
        )
    )


class _Bm25CandidateRetriever:
    """Evaluation-only deterministic BM25 scorer."""

    def __init__(
        self,
        *,
        config: Phase5Bm25CandidateConfig,
        documents: tuple[IndexedDocument, ...],
    ) -> None:
        self._config = config
        self._documents = documents

        tokenized = tuple(
            _tokens(document.content)
            for document in documents
        )

        self._document_tokens = tokenized
        self._document_lengths = tuple(
            len(tokens)
            for tokens in tokenized
        )

        total_length = sum(
            self._document_lengths
        )

        if total_length <= 0:
            raise ValueError(
                "BM25 candidate requires non-empty corpus text"
            )

        self._average_document_length = (
            total_length
            / len(documents)
        )

        document_frequency: Counter[str] = Counter()

        for tokens in tokenized:
            document_frequency.update(
                set(tokens)
            )

        self._document_frequency = (
            document_frequency
        )

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
            tokens,
            document_length,
        ) in zip(
            self._documents,
            self._document_tokens,
            self._document_lengths,
            strict=True,
        ):
            frequencies = Counter(
                tokens
            )

            score = 0.0

            for term in query_terms:
                term_frequency = frequencies.get(
                    term,
                    0,
                )

                if term_frequency == 0:
                    continue

                document_frequency = (
                    self._document_frequency[
                        term
                    ]
                )

                inverse_document_frequency = (
                    math.log(
                        1.0
                        + (
                            (
                                document_count
                                - document_frequency
                                + 0.5
                            )
                            / (
                                document_frequency
                                + 0.5
                            )
                        )
                    )
                )

                denominator = (
                    term_frequency
                    + self._config.k1
                    * (
                        1.0
                        - self._config.b
                        + self._config.b
                        * (
                            document_length
                            / self._average_document_length
                        )
                    )
                )

                score += (
                    inverse_document_frequency
                    * (
                        term_frequency
                        * (
                            self._config.k1
                            + 1.0
                        )
                    )
                    / denominator
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
                evidence_id=(
                    document.evidence_id
                ),
                source_ids=(
                    document.source_ids
                ),
                document_ids=(
                    document.document_ids
                ),
                content=document.content,
                rank=rank,
                score=score,
                authority_level=(
                    document.authority_level
                ),
                source_state=(
                    document.source_state
                ),
                product_scope=(
                    document.product_scope
                ),
                api_version_or_snapshot=(
                    document.api_version_or_snapshot
                ),
                synthetic_overlay=(
                    document.synthetic_overlay
                ),
                eligible_as_final_citation=(
                    document.eligible_as_final_citation
                ),
            )
            for rank, (
                score,
                document,
            ) in enumerate(
                scored[
                    : self._config.top_k
                ],
                start=1,
            )
        )


def _candidate_curve(
    comparisons: tuple[
        Phase5Bm25CaseComparison,
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


async def _build_report(
    repo_root: Path,
) -> Phase5Bm25CandidateExperimentReport:
    baseline = _verified_baseline(
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
            "expected exactly 15 answerable TUNING cases"
        )

    baseline_cases = {
        result.case_id: result
        for result in baseline.case_results
        if result.expected_response_mode
        is not ResponseMode.REFUSE
    }

    if set(baseline_cases) != set(
        answerable_cases
    ):
        raise ValueError(
            "baseline/candidate TUNING case identities differ"
        )

    candidate_config = (
        Phase5Bm25CandidateConfig()
    )

    candidate = (
        _Bm25CandidateRetriever(
            config=candidate_config,
            documents=documents,
        )
    )

    source_filter = (
        CurrentGithubRestSourcePolicyFilter(
            config=SourcePolicyConfig(
                policy_id=(
                    "github-rest-current-v1"
                )
            )
        )
    )

    comparisons: list[
        Phase5Bm25CaseComparison
    ] = []

    for case_id in sorted(
        answerable_cases
    ):
        case = answerable_cases[
            case_id
        ]

        baseline_case = baseline_cases[
            case_id
        ]

        if (
            baseline_case.minimum_raw_top_k_for_full_gold
            is None
            or baseline_case.minimum_eligible_items_for_full_gold
            is None
            or baseline_case.context_prefix_characters_for_full_gold
            is None
        ):
            raise ValueError(
                "baseline answerable case lacks full-gold floors"
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
            Phase5Bm25RequiredEvidenceRank(
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
            rank.raw_rank is not None
            for rank in rank_records
        )

        full_filter_eligible = all(
            rank.eligible_rank is not None
            for rank in rank_records
        )

        minimum_raw: int | None = None

        if full_retrievable:
            minimum_raw = max(
                cast(
                    int,
                    rank.raw_rank,
                )
                for rank in rank_records
            )

        minimum_eligible: int | None = None
        context_prefix: int | None = None

        if full_filter_eligible:
            minimum_eligible = max(
                cast(
                    int,
                    rank.eligible_rank,
                )
                for rank in rank_records
            )

            context_prefix = (
                _context_prefix_characters(
                    cast(
                        tuple[object, ...],
                        filtered.eligible,
                    ),
                    minimum_eligible,
                )
            )

        if minimum_raw is None:
            raw_rank_outcome: Literal[
                "improved",
                "unchanged",
                "regressed",
                "unretrievable",
            ] = "unretrievable"
        elif minimum_raw < (
            baseline_case.minimum_raw_top_k_for_full_gold
        ):
            raw_rank_outcome = "improved"
        elif minimum_raw == (
            baseline_case.minimum_raw_top_k_for_full_gold
        ):
            raw_rank_outcome = "unchanged"
        else:
            raw_rank_outcome = "regressed"

        comparisons.append(
            Phase5Bm25CaseComparison(
                case_id=case_id,
                required_evidence_count=len(
                    case.required_evidence_ids
                ),
                baseline_minimum_raw_top_k=(
                    baseline_case.minimum_raw_top_k_for_full_gold
                ),
                candidate_minimum_raw_top_k=(
                    minimum_raw
                ),
                baseline_minimum_eligible_items=(
                    baseline_case.minimum_eligible_items_for_full_gold
                ),
                candidate_minimum_eligible_items=(
                    minimum_eligible
                ),
                baseline_context_prefix_characters=(
                    baseline_case.context_prefix_characters_for_full_gold
                ),
                candidate_context_prefix_characters=(
                    context_prefix
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
                raw_rank_outcome=(
                    raw_rank_outcome
                ),
            )
        )

    typed_comparisons = tuple(
        comparisons
    )

    fully_retrievable = all(
        comparison.full_gold_retrievable
        for comparison in typed_comparisons
    )

    fully_filter_eligible = all(
        comparison.full_gold_filter_eligible
        for comparison in typed_comparisons
    )

    max_raw: int | None = None

    if fully_retrievable:
        max_raw = max(
            cast(
                int,
                comparison.candidate_minimum_raw_top_k,
            )
            for comparison in typed_comparisons
        )

    max_eligible: int | None = None
    max_context: int | None = None

    if fully_filter_eligible:
        max_eligible = max(
            cast(
                int,
                comparison.candidate_minimum_eligible_items,
            )
            for comparison in typed_comparisons
        )

        max_context = max(
            cast(
                int,
                comparison.candidate_context_prefix_characters,
            )
            for comparison in typed_comparisons
        )

    return Phase5Bm25CandidateExperimentReport(
        candidate_configuration_id=(
            candidate.configuration_id
        ),
        candidate_config=(
            candidate_config
        ),
        baseline_top_k_curve=(
            baseline.top_k_curve
        ),
        candidate_top_k_curve=(
            _candidate_curve(
                typed_comparisons
            )
        ),
        candidate_maximum_minimum_raw_top_k=(
            max_raw
        ),
        candidate_maximum_minimum_eligible_items=(
            max_eligible
        ),
        candidate_maximum_context_prefix_characters=(
            max_context
        ),
        improved_case_count=sum(
            comparison.raw_rank_outcome
            == "improved"
            for comparison in typed_comparisons
        ),
        unchanged_case_count=sum(
            comparison.raw_rank_outcome
            == "unchanged"
            for comparison in typed_comparisons
        ),
        regressed_case_count=sum(
            comparison.raw_rank_outcome
            == "regressed"
            for comparison in typed_comparisons
        ),
        unretrievable_case_count=sum(
            comparison.raw_rank_outcome
            == "unretrievable"
            for comparison in typed_comparisons
        ),
        case_comparisons=(
            typed_comparisons
        ),
    )


def materialize_phase5_bm25_candidate_experiment(
    repo_root: Path,
) -> tuple[
    Phase5Bm25CandidateExperimentReport,
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
        materialize_phase5_bm25_candidate_experiment(
            repo_root
        )
    )

    print(
        "PHASE5_BM25_CANDIDATE_EXPERIMENT_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_BM25_CANDIDATE_CONFIGURATION_ID="
        f"{report.candidate_configuration_id}"
    )

    for baseline_point, candidate_point in zip(
        report.baseline_top_k_curve,
        report.candidate_top_k_curve,
        strict=True,
    ):
        print(
            "PHASE5_BM25_COMPARISON="
            f"k:{baseline_point.top_k},"
            f"baseline_full:{baseline_point.full_gold_case_count}/"
            f"{baseline_point.applicable_case_count},"
            f"candidate_full:{candidate_point.full_gold_case_count}/"
            f"{candidate_point.applicable_case_count},"
            f"baseline_micro:{baseline_point.micro_gold_recall:.6f},"
            f"candidate_micro:{candidate_point.micro_gold_recall:.6f}"
        )

    print(
        "PHASE5_BM25_CASE_OUTCOMES="
        f"improved:{report.improved_case_count},"
        f"unchanged:{report.unchanged_case_count},"
        f"regressed:{report.regressed_case_count},"
        f"unretrievable:{report.unretrievable_case_count}"
    )
    print(
        "PHASE5_BM25_BASELINE_MAX_MIN_RAW_TOP_K="
        f"{report.baseline_maximum_minimum_raw_top_k}"
    )
    print(
        "PHASE5_BM25_CANDIDATE_MAX_MIN_RAW_TOP_K="
        f"{report.candidate_maximum_minimum_raw_top_k}"
    )
    print(
        "PHASE5_BM25_BASELINE_MAX_MIN_ELIGIBLE_ITEMS="
        f"{report.baseline_maximum_minimum_eligible_items}"
    )
    print(
        "PHASE5_BM25_CANDIDATE_MAX_MIN_ELIGIBLE_ITEMS="
        f"{report.candidate_maximum_minimum_eligible_items}"
    )
    print(
        "PHASE5_BM25_BASELINE_MAX_CONTEXT_PREFIX_CHARACTERS="
        f"{report.baseline_maximum_context_prefix_characters}"
    )
    print(
        "PHASE5_BM25_CANDIDATE_MAX_CONTEXT_PREFIX_CHARACTERS="
        f"{report.candidate_maximum_context_prefix_characters}"
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
