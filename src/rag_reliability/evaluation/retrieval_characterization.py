"""TUNING-only lexical retrieval characterization for Phase 5.

This module measures the existing deterministic LexicalRetriever against the
frozen TUNING suite and frozen Phase 3D chunk corpus. It does not select or
freeze a runtime configuration, execute a provider, run B0, inspect DEVELOPMENT
gold for tuning, or expose HELD_OUT outcomes.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from rag_reliability.config.identity import RetrievalConfig, SourcePolicyConfig
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import EvaluationRole, ResponseMode
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.contracts.runtime import RetrievalRequest, SourceFilterRequest
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.runtime.filtering import (
    CurrentGithubRestSourcePolicyFilter,
)
from rag_reliability.runtime.models import IndexedDocument
from rag_reliability.runtime.retrieval import LexicalRetriever

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
    / "phase5_tuning_retrieval_characterization_v1.json"
)

_TUNING_SHA256: Literal[
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
] = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"

_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

_CHARACTERIZATION_TOP_K: Literal[1333] = 1333

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


class Phase5RequiredEvidenceRank(ContractModel):
    """Observed position of one evaluator-owned required evidence ID."""

    evidence_id: NonEmptyStr
    raw_rank: int | None = Field(default=None, ge=1)
    eligible_rank: int | None = Field(default=None, ge=1)
    survived_source_filter: bool

    @model_validator(mode="after")
    def validate_rank_boundary(self) -> Self:
        if self.eligible_rank is not None and self.raw_rank is None:
            raise ValueError(
                "eligible evidence cannot exist without a raw retrieval rank"
            )

        if self.survived_source_filter != (self.eligible_rank is not None):
            raise ValueError(
                "source-filter survival does not reconcile with eligible rank"
            )

        return self


class Phase5TuningRetrievalCaseResult(ContractModel):
    """Characterization result for one frozen TUNING query."""

    case_id: NonEmptyStr
    expected_response_mode: ResponseMode

    raw_candidate_count: int = Field(ge=0)
    eligible_candidate_count: int = Field(ge=0)

    required_evidence_count: int = Field(ge=0)
    required_evidence_ranks: tuple[Phase5RequiredEvidenceRank, ...]

    full_gold_retrievable: bool | None = None
    full_gold_filter_eligible: bool | None = None

    minimum_raw_top_k_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )
    minimum_eligible_items_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )
    context_prefix_characters_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )

    @model_validator(mode="after")
    def validate_case_semantics(self) -> Self:
        if len(self.required_evidence_ranks) != self.required_evidence_count:
            raise ValueError(
                "required evidence rank count does not reconcile"
            )

        if self.expected_response_mode is ResponseMode.REFUSE:
            if self.required_evidence_count != 0:
                raise ValueError(
                    "refusal characterization cannot carry required evidence"
                )

            if any(
                value is not None
                for value in (
                    self.full_gold_retrievable,
                    self.full_gold_filter_eligible,
                    self.minimum_raw_top_k_for_full_gold,
                    self.minimum_eligible_items_for_full_gold,
                    self.context_prefix_characters_for_full_gold,
                )
            ):
                raise ValueError(
                    "refusal characterization cannot carry gold-rank metrics"
                )

            return self

        if self.required_evidence_count < 1:
            raise ValueError(
                "answerable characterization requires required evidence"
            )

        if self.full_gold_retrievable is None:
            raise ValueError(
                "answerable characterization requires retrievability verdict"
            )

        if self.full_gold_filter_eligible is None:
            raise ValueError(
                "answerable characterization requires filter verdict"
            )

        if self.full_gold_retrievable:
            if self.minimum_raw_top_k_for_full_gold is None:
                raise ValueError(
                    "retrievable gold requires a raw top-k floor"
                )
        elif self.minimum_raw_top_k_for_full_gold is not None:
            raise ValueError(
                "unretrievable gold cannot carry a raw top-k floor"
            )

        if self.full_gold_filter_eligible:
            if self.minimum_eligible_items_for_full_gold is None:
                raise ValueError(
                    "filter-eligible gold requires an eligible-item floor"
                )

            if self.context_prefix_characters_for_full_gold is None:
                raise ValueError(
                    "filter-eligible gold requires a context-prefix size"
                )
        elif any(
            value is not None
            for value in (
                self.minimum_eligible_items_for_full_gold,
                self.context_prefix_characters_for_full_gold,
            )
        ):
            raise ValueError(
                "filter-ineligible gold cannot carry context floors"
            )

        return self


class Phase5TopKCurvePoint(ContractModel):
    """Exact TUNING retrieval recall at one raw top-k cutoff."""

    top_k: int = Field(ge=1)

    applicable_case_count: int = Field(ge=1)
    full_gold_case_count: int = Field(ge=0)
    full_gold_case_rate: float = Field(ge=0.0, le=1.0)

    required_evidence_reference_count: int = Field(ge=1)
    retrieved_required_evidence_count: int = Field(ge=0)
    micro_gold_recall: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_curve_math(self) -> Self:
        if self.full_gold_case_count > self.applicable_case_count:
            raise ValueError(
                "full-gold case count cannot exceed applicable cases"
            )

        expected_case_rate = (
            self.full_gold_case_count
            / self.applicable_case_count
        )

        if abs(self.full_gold_case_rate - expected_case_rate) > 1e-12:
            raise ValueError(
                "full-gold case rate does not reconcile"
            )

        if (
            self.retrieved_required_evidence_count
            > self.required_evidence_reference_count
        ):
            raise ValueError(
                "retrieved required evidence cannot exceed denominator"
            )

        expected_micro = (
            self.retrieved_required_evidence_count
            / self.required_evidence_reference_count
        )

        if abs(self.micro_gold_recall - expected_micro) > 1e-12:
            raise ValueError(
                "micro gold recall does not reconcile"
            )

        return self


class Phase5TuningRetrievalCharacterizationReport(ContractModel):
    """TUNING-only characterization; explicitly not a configuration decision."""

    report_version: Literal[
        "phase5-tuning-retrieval-characterization-v1"
    ] = "phase5-tuning-retrieval-characterization-v1"

    evidence_class: Literal[
        "intervention_tuning_only"
    ] = "intervention_tuning_only"

    tuning_suite_sha256: Literal[
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
    ] = _TUNING_SHA256

    chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = _CHUNK_MANIFEST_SHA256

    retriever_id: Literal["lexical-v1"] = "lexical-v1"
    characterization_top_k: Literal[1333] = _CHARACTERIZATION_TOP_K
    retriever_configuration_id: Sha256

    source_policy_id: Literal[
        "github-rest-current-v1"
    ] = "github-rest-current-v1"
    source_policy_configuration_id: Sha256

    corpus_chunk_count: Literal[1333] = 1333
    tuning_case_count: Literal[18] = 18
    answerable_case_count: Literal[15] = 15
    refusal_case_count: Literal[3] = 3

    required_evidence_reference_count: int = Field(ge=1)
    unique_required_evidence_count: int = Field(ge=1)

    all_chunk_content_hashes_verified: Literal[True] = True
    all_required_evidence_present_in_corpus: Literal[True] = True

    all_answerable_full_gold_retrievable: bool
    all_answerable_full_gold_filter_eligible: bool

    maximum_minimum_raw_top_k_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )
    maximum_minimum_eligible_items_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )
    maximum_context_prefix_characters_for_full_gold: int | None = Field(
        default=None,
        ge=1,
    )

    top_k_curve: tuple[Phase5TopKCurvePoint, ...] = Field(
        min_length=10,
        max_length=10,
    )
    case_results: tuple[Phase5TuningRetrievalCaseResult, ...] = Field(
        min_length=18,
        max_length=18,
    )

    development_gold_used_for_characterization: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False

    provider_invoked: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if (
            self.answerable_case_count
            + self.refusal_case_count
            != self.tuning_case_count
        ):
            raise ValueError(
                "TUNING answerable/refusal counts do not reconcile"
            )

        case_ids = tuple(
            result.case_id
            for result in self.case_results
        )

        if len(case_ids) != len(set(case_ids)):
            raise ValueError(
                "TUNING characterization case IDs must be unique"
            )

        if tuple(
            point.top_k
            for point in self.top_k_curve
        ) != _TOP_K_CURVE:
            raise ValueError(
                "top-k characterization curve drifted"
            )

        if self.development_gold_used_for_characterization:
            raise ValueError(
                "DEVELOPMENT gold cannot tune retrieval configuration"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "HELD_OUT outcomes cannot enter retrieval characterization"
            )

        if self.retrieval_configuration_selected:
            raise ValueError(
                "characterization cannot select retrieval configuration"
            )

        if self.semantic_runtime_configuration_selected:
            raise ValueError(
                "characterization cannot select semantic runtime configuration"
            )

        if self.semantic_runtime_configuration_frozen:
            raise ValueError(
                "characterization cannot freeze semantic runtime configuration"
            )

        if self.provider_invoked:
            raise ValueError(
                "retrieval characterization cannot invoke a provider"
            )

        if self.baseline_execution_authorized or self.b0_executed:
            raise ValueError(
                "retrieval characterization cannot authorize or execute B0"
            )

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(
    path: Path,
    expected_sha256: str,
) -> bytes:
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(
            f"frozen artifact hash mismatch: {path}"
        )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    expected_sidecar = (
        f"{expected_sha256}  {path.name}"
    )

    observed_sidecar = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    if observed_sidecar != expected_sidecar:
        raise ValueError(
            f"SHA sidecar mismatch: {path}"
        )

    return content


def _load_tuning_cases(
    repo_root: Path,
) -> tuple[EvaluationCase, ...]:
    content = _verified_bytes(
        repo_root / _TUNING_PATH,
        _TUNING_SHA256,
    )

    payload = json.loads(content)

    if not isinstance(payload, dict):
        raise ValueError(
            "TUNING suite must be a JSON object"
        )

    if payload.get("case_count") != 18:
        raise ValueError(
            "TUNING case count drifted"
        )

    raw_records = payload.get("records")

    if not isinstance(raw_records, list):
        raise ValueError(
            "TUNING records must be a JSON array"
        )

    cases: list[EvaluationCase] = []

    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            raise ValueError(
                "TUNING record must be a JSON object"
            )

        raw_case = raw_record.get("case")

        if not isinstance(raw_case, dict):
            raise ValueError(
                "TUNING record requires case object"
            )

        case = EvaluationCase.model_validate(
            raw_case
        )

        if case.data_role is not EvaluationRole.TUNING:
            raise ValueError(
                "retrieval characterization must remain TUNING-only"
            )

        cases.append(case)

    if len(cases) != 18:
        raise ValueError(
            "TUNING suite record count drifted"
        )

    if len(
        {
            case.case_id
            for case in cases
        }
    ) != 18:
        raise ValueError(
            "TUNING case IDs must be unique"
        )

    return tuple(cases)


def _load_indexed_documents(
    repo_root: Path,
) -> tuple[
    tuple[IndexedDocument, ...],
    set[str],
]:
    manifest_content = _verified_bytes(
        repo_root / _CHUNK_MANIFEST_PATH,
        _CHUNK_MANIFEST_SHA256,
    )

    manifest = (
        Phase3dChunkManifest.model_validate_json(
            manifest_content
        )
    )

    documents: list[IndexedDocument] = []

    for chunk in manifest.chunks:
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
                f"chunk content hash mismatch: {chunk.chunk_id}"
            )

        content = content_bytes.decode(
            "utf-8"
        )

        source_ids = tuple(
            sorted(
                {
                    parent.source_id
                    for parent in chunk.parents
                }
            )
        )

        document_ids = tuple(
            sorted(
                {
                    parent.document_id
                    for parent in chunk.parents
                }
            )
        )

        documents.append(
            IndexedDocument(
                evidence_id=chunk.chunk_id,
                source_ids=source_ids,
                document_ids=document_ids,
                content=content,
                authority_level=(
                    chunk.evidence_scope.authority_level
                ),
                source_state=(
                    chunk.evidence_scope.source_state
                ),
                product_scope=(
                    chunk.evidence_scope.product_scope
                ),
                api_version_or_snapshot=(
                    chunk.evidence_scope.api_version_or_snapshot
                ),
                synthetic_overlay=False,
                eligible_as_final_citation=True,
            )
        )

    if len(documents) != 1333:
        raise ValueError(
            "indexed chunk count drifted"
        )

    evidence_ids = {
        document.evidence_id
        for document in documents
    }

    if len(evidence_ids) != 1333:
        raise ValueError(
            "indexed evidence IDs must be unique"
        )

    return (
        tuple(documents),
        evidence_ids,
    )


def _context_prefix_characters(
    eligible_items: tuple[object, ...],
    prefix_count: int,
) -> int:
    from rag_reliability.contracts.runtime import RetrievedEvidence

    typed_items: list[RetrievedEvidence] = []

    for item in eligible_items[:prefix_count]:
        if not isinstance(
            item,
            RetrievedEvidence,
        ):
            raise TypeError(
                "eligible context item must be RetrievedEvidence"
            )
        typed_items.append(item)

    blocks = tuple(
        (
            f"EVIDENCE: {item.evidence_id}\n"
            f"{item.content}"
        )
        for item in typed_items
    )

    return len(
        "\n\n".join(blocks)
    )


def _curve(
    case_results: tuple[
        Phase5TuningRetrievalCaseResult,
        ...,
    ],
) -> tuple[Phase5TopKCurvePoint, ...]:
    answerable = tuple(
        result
        for result in case_results
        if result.expected_response_mode
        is not ResponseMode.REFUSE
    )

    reference_count = sum(
        result.required_evidence_count
        for result in answerable
    )

    points: list[Phase5TopKCurvePoint] = []

    for top_k in _TOP_K_CURVE:
        full_gold_case_count = 0
        retrieved_reference_count = 0

        for result in answerable:
            ranks = tuple(
                item.raw_rank
                for item in result.required_evidence_ranks
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
                full_gold_case_count += 1

        points.append(
            Phase5TopKCurvePoint(
                top_k=top_k,
                applicable_case_count=len(
                    answerable
                ),
                full_gold_case_count=(
                    full_gold_case_count
                ),
                full_gold_case_rate=(
                    full_gold_case_count
                    / len(answerable)
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
) -> Phase5TuningRetrievalCharacterizationReport:
    cases = _load_tuning_cases(
        repo_root
    )

    (
        documents,
        corpus_evidence_ids,
    ) = _load_indexed_documents(
        repo_root
    )

    answerable_cases = tuple(
        case
        for case in cases
        if case.expected_response_mode
        is not ResponseMode.REFUSE
    )

    refusal_cases = tuple(
        case
        for case in cases
        if case.expected_response_mode
        is ResponseMode.REFUSE
    )

    if len(answerable_cases) != 15:
        raise ValueError(
            "expected 15 answerable TUNING cases"
        )

    if len(refusal_cases) != 3:
        raise ValueError(
            "expected 3 refusal TUNING cases"
        )

    required_evidence_ids = {
        evidence_id
        for case in answerable_cases
        for evidence_id in case.required_evidence_ids
    }

    if not required_evidence_ids <= corpus_evidence_ids:
        raise ValueError(
            "TUNING required evidence is missing from frozen corpus"
        )

    retrieval_config = RetrievalConfig(
        retriever_id="lexical-v1",
        top_k=_CHARACTERIZATION_TOP_K,
    )

    source_policy_config = SourcePolicyConfig(
        policy_id="github-rest-current-v1"
    )

    retriever = LexicalRetriever(
        config=retrieval_config,
        documents=documents,
    )

    source_filter = (
        CurrentGithubRestSourcePolicyFilter(
            config=source_policy_config
        )
    )

    case_results: list[
        Phase5TuningRetrievalCaseResult
    ] = []

    for case in cases:
        retrieval = await retriever.retrieve(
            RetrievalRequest(
                query=case.query,
                top_k=_CHARACTERIZATION_TOP_K,
            )
        )

        filtered = await source_filter.apply(
            SourceFilterRequest(
                candidates=retrieval.items
            )
        )

        if case.expected_response_mode is ResponseMode.REFUSE:
            case_results.append(
                Phase5TuningRetrievalCaseResult(
                    case_id=case.case_id,
                    expected_response_mode=(
                        case.expected_response_mode
                    ),
                    raw_candidate_count=len(
                        retrieval.items
                    ),
                    eligible_candidate_count=len(
                        filtered.eligible
                    ),
                    required_evidence_count=0,
                    required_evidence_ranks=(),
                )
            )
            continue

        raw_rank_by_id = {
            item.evidence_id: item.rank
            for item in retrieval.items
        }

        eligible_rank_by_id = {
            item.evidence_id: index
            for index, item in enumerate(
                filtered.eligible,
                start=1,
            )
        }

        rank_records = tuple(
            Phase5RequiredEvidenceRank(
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

        full_gold_retrievable = all(
            item.raw_rank is not None
            for item in rank_records
        )

        full_gold_filter_eligible = all(
            item.eligible_rank is not None
            for item in rank_records
        )

        minimum_raw_top_k: int | None = None

        if full_gold_retrievable:
            raw_ranks = tuple(
                cast(int, item.raw_rank)
                for item in rank_records
            )
            minimum_raw_top_k = max(
                raw_ranks
            )

        minimum_eligible_items: int | None = None
        context_prefix_characters: int | None = None

        if full_gold_filter_eligible:
            eligible_ranks = tuple(
                cast(int, item.eligible_rank)
                for item in rank_records
            )

            minimum_eligible_items = max(
                eligible_ranks
            )

            context_prefix_characters = (
                _context_prefix_characters(
                    cast(
                        tuple[object, ...],
                        filtered.eligible,
                    ),
                    minimum_eligible_items,
                )
            )

        case_results.append(
            Phase5TuningRetrievalCaseResult(
                case_id=case.case_id,
                expected_response_mode=(
                    case.expected_response_mode
                ),
                raw_candidate_count=len(
                    retrieval.items
                ),
                eligible_candidate_count=len(
                    filtered.eligible
                ),
                required_evidence_count=len(
                    case.required_evidence_ids
                ),
                required_evidence_ranks=(
                    rank_records
                ),
                full_gold_retrievable=(
                    full_gold_retrievable
                ),
                full_gold_filter_eligible=(
                    full_gold_filter_eligible
                ),
                minimum_raw_top_k_for_full_gold=(
                    minimum_raw_top_k
                ),
                minimum_eligible_items_for_full_gold=(
                    minimum_eligible_items
                ),
                context_prefix_characters_for_full_gold=(
                    context_prefix_characters
                ),
            )
        )

    typed_results = tuple(
        case_results
    )

    answer_results = tuple(
        result
        for result in typed_results
        if result.expected_response_mode
        is not ResponseMode.REFUSE
    )

    all_retrievable = all(
        result.full_gold_retrievable is True
        for result in answer_results
    )

    all_filter_eligible = all(
        result.full_gold_filter_eligible is True
        for result in answer_results
    )

    maximum_raw_top_k: int | None = None

    if all_retrievable:
        maximum_raw_top_k = max(
            cast(
                int,
                result.minimum_raw_top_k_for_full_gold,
            )
            for result in answer_results
        )

    maximum_eligible_items: int | None = None
    maximum_context_chars: int | None = None

    if all_filter_eligible:
        maximum_eligible_items = max(
            cast(
                int,
                result.minimum_eligible_items_for_full_gold,
            )
            for result in answer_results
        )

        maximum_context_chars = max(
            cast(
                int,
                result.context_prefix_characters_for_full_gold,
            )
            for result in answer_results
        )

    return Phase5TuningRetrievalCharacterizationReport(
        retriever_configuration_id=(
            retrieval_config.configuration_id
        ),
        source_policy_configuration_id=(
            source_policy_config.configuration_id
        ),
        required_evidence_reference_count=sum(
            len(case.required_evidence_ids)
            for case in answerable_cases
        ),
        unique_required_evidence_count=len(
            required_evidence_ids
        ),
        all_answerable_full_gold_retrievable=(
            all_retrievable
        ),
        all_answerable_full_gold_filter_eligible=(
            all_filter_eligible
        ),
        maximum_minimum_raw_top_k_for_full_gold=(
            maximum_raw_top_k
        ),
        maximum_minimum_eligible_items_for_full_gold=(
            maximum_eligible_items
        ),
        maximum_context_prefix_characters_for_full_gold=(
            maximum_context_chars
        ),
        top_k_curve=_curve(
            typed_results
        ),
        case_results=typed_results,
    )


def materialize_phase5_tuning_retrieval_characterization(
    repo_root: Path,
) -> tuple[
    Phase5TuningRetrievalCharacterizationReport,
    str,
]:
    """Materialize deterministic TUNING-only lexical characterization."""

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
        materialize_phase5_tuning_retrieval_characterization(
            repo_root
        )
    )

    print(
        "PHASE5_TUNING_RETRIEVAL_CHARACTERIZATION_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_TUNING_ANSWERABLE_CASE_COUNT="
        f"{report.answerable_case_count}"
    )
    print(
        "PHASE5_TUNING_REQUIRED_EVIDENCE_REFERENCE_COUNT="
        f"{report.required_evidence_reference_count}"
    )
    print(
        "PHASE5_TUNING_UNIQUE_REQUIRED_EVIDENCE_COUNT="
        f"{report.unique_required_evidence_count}"
    )
    print(
        "PHASE5_TUNING_ALL_GOLD_RETRIEVABLE="
        f"{str(report.all_answerable_full_gold_retrievable).lower()}"
    )
    print(
        "PHASE5_TUNING_ALL_GOLD_FILTER_ELIGIBLE="
        f"{str(report.all_answerable_full_gold_filter_eligible).lower()}"
    )
    print(
        "PHASE5_TUNING_MAX_MIN_RAW_TOP_K="
        f"{report.maximum_minimum_raw_top_k_for_full_gold}"
    )
    print(
        "PHASE5_TUNING_MAX_MIN_ELIGIBLE_ITEMS="
        f"{report.maximum_minimum_eligible_items_for_full_gold}"
    )
    print(
        "PHASE5_TUNING_MAX_CONTEXT_PREFIX_CHARACTERS="
        f"{report.maximum_context_prefix_characters_for_full_gold}"
    )

    for point in report.top_k_curve:
        print(
            "PHASE5_TUNING_RECALL_CURVE="
            f"k:{point.top_k},"
            f"full_cases:{point.full_gold_case_count}/"
            f"{point.applicable_case_count},"
            f"micro:{point.micro_gold_recall:.6f}"
        )

    print(
        "PHASE5_RETRIEVAL_CONFIGURATION_SELECTED=false"
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
