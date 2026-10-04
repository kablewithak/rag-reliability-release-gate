"""Materialize and custody the frozen evaluator-blind Phase 5 B0 replay fixture."""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.config.identity import (
    CitationConfig,
    ContextConfig,
    FallbackConfig,
    ProviderConfig,
    RetrievalConfig,
    RuntimeConfiguration,
    SourcePolicyConfig,
)
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.interfaces import (
    ContextBuilder,
    Retriever,
    SourcePolicyFilter,
)
from rag_reliability.contracts.runtime import (
    ContextBuildRequest,
    RetrievalRequest,
    SourceFilterRequest,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.b0_replay_fixture_protocol import (
    Phase5B0ReplayFixtureProtocolV1,
)
from rag_reliability.evaluation.b0_replay_fixture_protocol_freeze import (
    Phase5B0ReplayFixtureProtocolFreezeV1,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    B0ProjectedSuite,
    B0Role,
    Phase5B0RuntimeProjectionV1,
    load_phase5_b0_runtime_projection,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
)
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import (
    ContextBudgetExhaustedError,
    RetrievalExecutionError,
    SourcePolicyExecutionError,
)
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import ReplayEntry
from rag_reliability.runtime.operation_aware_rrf_retriever import (
    OperationAwareRrfRetriever,
)

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_b0_replay_fixture_protocol_v1.json"
)
_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_b0_replay_fixture_protocol_freeze_v1.json"
)
_BASELINE_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_v1.json"
)
_BASELINE_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_baseline_protocol_freeze_v1.json"
)
_G5K_QUALIFICATION_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_g5k_runtime_qualification_v1.json"
)

_FIXTURE_PATH = (
    Path("evidence_vault")
    / "eval_reports"
    / "phase5_b0_replay_fixture_v1.json"
)
_COVERAGE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_b0_replay_fixture_coverage_v1.json"
)

_PROTOCOL_SHA256: Sha256 = (
    "c39ddce45a8c1204e596740061943c5f1da370897f8522a0b1f30b75b17a200b"
)
_PROTOCOL_FREEZE_SHA256: Sha256 = (
    "91f5bff1a1fe23308c26d00db0ba23d3146d9f1098361f40e688dc707e0008f3"
)
_BASELINE_PROTOCOL_SHA256: Sha256 = (
    "20637e8eaa598224c33fe83d223fcc5d031d2bfa577299c8cdff4ccfceb6cc19"
)
_BASELINE_PROTOCOL_FREEZE_SHA256: Sha256 = (
    "a92845181c9fcd3c69b84a191f1288f4391431cae8f82fe6c520b0b2a07bf434"
)
_G5K_QUALIFICATION_SHA256: Sha256 = (
    "678dcb0d6453e11cd8e2b9c71153ed8337d5b8a26fcd36d732d6e8eb05dcbe71"
)
_G5K_RUNTIME_CONFIGURATION_ID: Sha256 = (
    "7399c9ef7cd6612eb8fc363602e9c45c74ca691acde257aa40d07cc4135642a2"
)
_DEVELOPMENT_SUITE_SHA256: Sha256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_TUNING_SUITE_SHA256: Sha256 = (
    "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
)

PrefixDisposition = Literal[
    "provider_reaching",
    "pre_provider_refusal",
    "prefix_error",
]
MaterializationDecision = Literal["PASS", "REJECT"]


class Phase5B0ReplayFixtureV1(ContractModel):
    """Raw replay dependency kept in the ignored evidence vault."""

    fixture_version: Literal[
        "phase5-b0-replay-fixture-v1"
    ] = "phase5-b0-replay-fixture-v1"

    provider_mode: Literal[
        "query_keyed_scripted_response"
    ] = "query_keyed_scripted_response"

    runtime_configuration_id: Sha256 = _G5K_RUNTIME_CONFIGURATION_ID
    protocol_sha256: Sha256 = _PROTOCOL_SHA256
    entries: tuple[ReplayEntry, ...]

    @model_validator(mode="after")
    def validate_unique_exact_query_keys(self) -> Self:
        queries = tuple(entry.query for entry in self.entries)
        if len(queries) != len(set(queries)):
            raise ValueError("B0 replay fixture exact query keys must be unique")
        if tuple(sorted(queries)) != queries:
            raise ValueError("B0 replay fixture entries must be sorted by exact query")
        return self


class Phase5B0ReplayCoverageCase(ContractModel):
    """Public-safe per-case construction evidence without raw query/source text."""

    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256
    disposition: PrefixDisposition

    selected_context_evidence_id: NonEmptyStr | None = None
    selected_context_content_sha256: Sha256 | None = None
    response_sha256: Sha256 | None = None
    fixture_key_sha256: Sha256 | None = None
    prefix_error_code: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_disposition_fields(self) -> Self:
        provider_fields = (
            self.selected_context_evidence_id,
            self.selected_context_content_sha256,
            self.response_sha256,
            self.fixture_key_sha256,
        )

        if self.disposition == "provider_reaching":
            if any(value is None for value in provider_fields):
                raise ValueError(
                    "provider-reaching coverage requires context/response/key evidence"
                )
            if self.prefix_error_code is not None:
                raise ValueError(
                    "provider-reaching coverage cannot carry prefix_error_code"
                )
            return self

        if any(value is not None for value in provider_fields):
            raise ValueError(
                "non-provider coverage cannot carry provider fixture evidence"
            )

        if self.disposition == "prefix_error":
            if self.prefix_error_code is None:
                raise ValueError("prefix error requires prefix_error_code")
        elif self.prefix_error_code is not None:
            raise ValueError(
                "pre-provider refusal cannot carry prefix_error_code"
            )

        return self


class Phase5B0ReplayFixtureCoverageV1(ContractModel):
    """Coverage and construction receipt for the frozen 42-case materialization."""

    receipt_version: Literal[
        "phase5-b0-replay-fixture-coverage-v1"
    ] = "phase5-b0-replay-fixture-coverage-v1"

    protocol_sha256: Sha256 = _PROTOCOL_SHA256
    protocol_freeze_sha256: Sha256 = _PROTOCOL_FREEZE_SHA256
    baseline_protocol_sha256: Sha256 = _BASELINE_PROTOCOL_SHA256
    baseline_protocol_freeze_sha256: Sha256 = _BASELINE_PROTOCOL_FREEZE_SHA256
    g5k_runtime_qualification_sha256: Sha256 = _G5K_QUALIFICATION_SHA256
    runtime_configuration_id: Sha256 = _G5K_RUNTIME_CONFIGURATION_ID
    development_suite_sha256: Sha256 = _DEVELOPMENT_SUITE_SHA256
    tuning_suite_sha256: Sha256 = _TUNING_SUITE_SHA256

    raw_fixture_relative_path: Literal[
        "evidence_vault/eval_reports/phase5_b0_replay_fixture_v1.json"
    ] = "evidence_vault/eval_reports/phase5_b0_replay_fixture_v1.json"
    replay_fixture_sha256: Sha256 | None

    authorized_case_count: Literal[42] = 42
    development_case_count: Literal[24] = 24
    tuning_case_count: Literal[18] = 18

    provider_reaching_case_count: int = Field(ge=0, le=42)
    pre_provider_refusal_case_count: int = Field(ge=0, le=42)
    unexpected_prefix_error_count: int = Field(ge=0, le=42)

    distinct_provider_query_count: int = Field(ge=0, le=42)
    duplicate_provider_case_count: int = Field(ge=0, le=42)
    fixture_entry_count: int = Field(ge=0, le=42)

    query_disposition_conflict_count: int = Field(ge=0, le=42)
    duplicate_response_conflict_count: int = Field(ge=0, le=42)

    cases: tuple[
        Phase5B0ReplayCoverageCase,
        ...,
    ] = Field(min_length=42, max_length=42)

    materialization_decision: MaterializationDecision
    replay_fixture_materialized: bool

    runtime_projection_fields: tuple[str, str] = ("case_id", "query")

    evaluator_fields_used_for_fixture_authoring: Literal[False] = False
    protected_roles_accessed: Literal[False] = False
    live_provider_call_count: Literal[0] = 0
    response_edit_count: Literal[0] = 0

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_coverage_math(self) -> Self:
        if self.runtime_projection_fields != ("case_id", "query"):
            raise ValueError("coverage runtime projection boundary drifted")

        if len({case.case_id for case in self.cases}) != 42:
            raise ValueError("coverage case IDs must be unique")

        observed_development = sum(
            case.role == "evaluation_development_case"
            for case in self.cases
        )
        observed_tuning = sum(
            case.role == "intervention_tuning_case"
            for case in self.cases
        )

        if observed_development != self.development_case_count:
            raise ValueError("DEVELOPMENT coverage count drifted")
        if observed_tuning != self.tuning_case_count:
            raise ValueError("TUNING coverage count drifted")

        if (
            self.provider_reaching_case_count
            + self.pre_provider_refusal_case_count
            + self.unexpected_prefix_error_count
            != self.authorized_case_count
        ):
            raise ValueError("coverage partition does not close to 42")

        observed_provider = sum(
            case.disposition == "provider_reaching"
            for case in self.cases
        )
        observed_refusal = sum(
            case.disposition == "pre_provider_refusal"
            for case in self.cases
        )
        observed_errors = sum(
            case.disposition == "prefix_error"
            for case in self.cases
        )

        if observed_provider != self.provider_reaching_case_count:
            raise ValueError("provider-reaching count does not reconcile")
        if observed_refusal != self.pre_provider_refusal_case_count:
            raise ValueError("pre-provider refusal count does not reconcile")
        if observed_errors != self.unexpected_prefix_error_count:
            raise ValueError("prefix error count does not reconcile")

        expected_duplicate_cases = (
            self.provider_reaching_case_count
            - self.distinct_provider_query_count
        )
        if self.duplicate_provider_case_count != expected_duplicate_cases:
            raise ValueError("duplicate provider case count does not reconcile")

        accepted = (
            self.unexpected_prefix_error_count == 0
            and self.query_disposition_conflict_count == 0
            and self.duplicate_response_conflict_count == 0
            and self.fixture_entry_count == self.distinct_provider_query_count
            and self.replay_fixture_sha256 is not None
            and self.replay_fixture_materialized
            and not self.evaluator_fields_used_for_fixture_authoring
            and not self.protected_roles_accessed
            and self.live_provider_call_count == 0
            and self.response_edit_count == 0
        )

        expected_decision = "PASS" if accepted else "REJECT"
        if self.materialization_decision != expected_decision:
            raise ValueError("materialization decision does not reconcile")

        if self.materialization_decision == "REJECT":
            if self.replay_fixture_materialized:
                raise ValueError("rejected materialization cannot freeze a replay fixture")
            if self.replay_fixture_sha256 is not None:
                raise ValueError("rejected materialization cannot carry fixture SHA")

        return self


@dataclass(frozen=True)
class _ProviderCandidate:
    case_id: str
    query: str
    entry: ReplayEntry


@dataclass(frozen=True)
class _CaseObservation:
    case_id: str
    role: B0Role
    query: str
    coverage: Phase5B0ReplayCoverageCase
    provider_candidate: _ProviderCandidate | None


@dataclass(frozen=True)
class _DeduplicationResult:
    entries: tuple[ReplayEntry, ...]
    distinct_provider_query_count: int
    duplicate_provider_case_count: int
    duplicate_response_conflict_count: int


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _stable_model_bytes(value: ContractModel) -> bytes:
    return (
        json.dumps(
            value.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _model_sha256(value: ContractModel) -> str:
    return _sha256_bytes(_stable_model_bytes(value))


def _verified_bytes(
    path: Path,
    expected_sha256: str,
) -> bytes:
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise ValueError(f"frozen artifact sidecar mismatch: {path}")

    return content


def _load_frozen_controls(
    repo_root: Path,
) -> Phase5B0ReplayFixtureProtocolV1:
    protocol = Phase5B0ReplayFixtureProtocolV1.model_validate_json(
        _verified_bytes(
            repo_root / _PROTOCOL_PATH,
            _PROTOCOL_SHA256,
        )
    )

    freeze = Phase5B0ReplayFixtureProtocolFreezeV1.model_validate_json(
        _verified_bytes(
            repo_root / _PROTOCOL_FREEZE_PATH,
            _PROTOCOL_FREEZE_SHA256,
        )
    )

    _verified_bytes(
        repo_root / _BASELINE_PROTOCOL_PATH,
        _BASELINE_PROTOCOL_SHA256,
    )
    _verified_bytes(
        repo_root / _BASELINE_PROTOCOL_FREEZE_PATH,
        _BASELINE_PROTOCOL_FREEZE_SHA256,
    )

    g5k_payload = json.loads(
        _verified_bytes(
            repo_root / _G5K_QUALIFICATION_PATH,
            _G5K_QUALIFICATION_SHA256,
        )
    )

    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("fixture protocol freeze does not bind expected protocol")

    if not freeze.protocol_frozen:
        raise ValueError("fixture authoring protocol is not frozen")

    if not isinstance(g5k_payload, dict):
        raise ValueError("G5K qualification artifact must be a JSON object")

    if g5k_payload.get("qualification_decision") != "PASS":
        raise ValueError("G5K qualification is not PASS")

    if g5k_payload.get("runtime_configuration_id") != _G5K_RUNTIME_CONFIGURATION_ID:
        raise ValueError("G5K runtime configuration identity drifted")

    if g5k_payload.get("baseline_execution_authorized") is not False:
        raise ValueError("G5K artifact unexpectedly authorizes baseline execution")

    return protocol


def _b0_runtime_config(
    protocol: Phase5B0ReplayFixtureProtocolV1,
) -> RuntimeConfiguration:
    config = RuntimeConfiguration(
        schema_version="phase5-g5k-runtime-qualification-v1",
        retrieval=RetrievalConfig(
            retriever_id=protocol.selected_retrieval_id,
            top_k=protocol.retrieval_top_k,
        ),
        source_policy=SourcePolicyConfig(
            policy_id=protocol.source_policy_id,
        ),
        reranker=None,
        context=ContextConfig(
            builder_id=protocol.context_builder_id,
            budget_unit_id=protocol.context_budget_unit_id,
            max_budget=protocol.context_max_budget,
            max_evidence_items=protocol.context_max_evidence_items,
        ),
        provider=ProviderConfig(
            adapter_id="replay-provider-v1",
            model_id="replay-model-v1",
            timeout_ms=1000,
            max_retries=0,
        ),
        citation=CitationConfig(
            validator_id="exact-citation-v1",
            require_citations=True,
        ),
        fallback=FallbackConfig(
            policy_id="safe-refusal-v1",
            allow_qualified_answer=False,
        ),
    )

    if config.configuration_id != _G5K_RUNTIME_CONFIGURATION_ID:
        raise ValueError("materializer runtime configuration does not match G5K")

    return config


def _deduplicate_provider_candidates(
    candidates: tuple[_ProviderCandidate, ...],
) -> _DeduplicationResult:
    by_query: dict[str, ReplayEntry] = {}
    conflict_queries: set[str] = set()

    for candidate in candidates:
        existing = by_query.get(candidate.query)

        if existing is None:
            by_query[candidate.query] = candidate.entry
            continue

        if existing != candidate.entry:
            conflict_queries.add(candidate.query)

    distinct_query_count = len(by_query)
    duplicate_case_count = len(candidates) - distinct_query_count

    if conflict_queries:
        return _DeduplicationResult(
            entries=(),
            distinct_provider_query_count=distinct_query_count,
            duplicate_provider_case_count=duplicate_case_count,
            duplicate_response_conflict_count=len(conflict_queries),
        )

    entries = tuple(by_query[query] for query in sorted(by_query))

    return _DeduplicationResult(
        entries=entries,
        distinct_provider_query_count=distinct_query_count,
        duplicate_provider_case_count=duplicate_case_count,
        duplicate_response_conflict_count=0,
    )


class B0ReplayFixtureMaterializer:
    """Run only the frozen retrieval/filter/context prefix; never invoke a provider."""

    def __init__(
        self,
        *,
        retriever: Retriever,
        source_filter: SourcePolicyFilter,
        context_builder: ContextBuilder,
    ) -> None:
        self._retriever = retriever
        self._source_filter = source_filter
        self._context_builder = context_builder

    async def _observe_case(
        self,
        *,
        case_id: str,
        query: str,
        role: B0Role,
        top_k: int,
    ) -> _CaseObservation:
        query_sha256 = _sha256_text(query)

        try:
            retrieval = await self._retriever.retrieve(
                RetrievalRequest(
                    query=query,
                    top_k=top_k,
                )
            )
        except RetrievalExecutionError:
            return _CaseObservation(
                case_id=case_id,
                role=role,
                query=query,
                coverage=Phase5B0ReplayCoverageCase(
                    case_id=case_id,
                    role=role,
                    query_sha256=query_sha256,
                    disposition="prefix_error",
                    prefix_error_code="retrieval_execution_error",
                ),
                provider_candidate=None,
            )

        try:
            filtered = await self._source_filter.apply(
                SourceFilterRequest(
                    candidates=retrieval.items,
                )
            )
        except SourcePolicyExecutionError:
            return _CaseObservation(
                case_id=case_id,
                role=role,
                query=query,
                coverage=Phase5B0ReplayCoverageCase(
                    case_id=case_id,
                    role=role,
                    query_sha256=query_sha256,
                    disposition="prefix_error",
                    prefix_error_code="source_policy_execution_error",
                ),
                provider_candidate=None,
            )

        if not filtered.eligible:
            return _CaseObservation(
                case_id=case_id,
                role=role,
                query=query,
                coverage=Phase5B0ReplayCoverageCase(
                    case_id=case_id,
                    role=role,
                    query_sha256=query_sha256,
                    disposition="pre_provider_refusal",
                ),
                provider_candidate=None,
            )

        try:
            context = await self._context_builder.build(
                ContextBuildRequest(
                    query=query,
                    evidence=filtered.eligible,
                )
            )
        except ContextBudgetExhaustedError:
            return _CaseObservation(
                case_id=case_id,
                role=role,
                query=query,
                coverage=Phase5B0ReplayCoverageCase(
                    case_id=case_id,
                    role=role,
                    query_sha256=query_sha256,
                    disposition="prefix_error",
                    prefix_error_code="context_budget_exhausted",
                ),
                provider_candidate=None,
            )

        first = context.items[0]
        response_sha256 = _sha256_text(first.content)

        entry = ReplayEntry(
            query=query,
            answer_text=first.content,
            cited_evidence_ids=(first.evidence_id,),
        )

        return _CaseObservation(
            case_id=case_id,
            role=role,
            query=query,
            coverage=Phase5B0ReplayCoverageCase(
                case_id=case_id,
                role=role,
                query_sha256=query_sha256,
                disposition="provider_reaching",
                selected_context_evidence_id=first.evidence_id,
                selected_context_content_sha256=response_sha256,
                response_sha256=response_sha256,
                fixture_key_sha256=query_sha256,
            ),
            provider_candidate=_ProviderCandidate(
                case_id=case_id,
                query=query,
                entry=entry,
            ),
        )

    async def _observe_suite(
        self,
        *,
        suite: B0ProjectedSuite,
        top_k: int,
    ) -> tuple[_CaseObservation, ...]:
        observed: list[_CaseObservation] = []

        for case in suite.cases:
            observed.append(
                await self._observe_case(
                    case_id=case.case_id,
                    query=case.query,
                    role=suite.role,
                    top_k=top_k,
                )
            )

        return tuple(observed)

    async def materialize(
        self,
        *,
        projection: Phase5B0RuntimeProjectionV1,
        protocol: Phase5B0ReplayFixtureProtocolV1,
    ) -> tuple[
        Phase5B0ReplayFixtureV1 | None,
        Phase5B0ReplayFixtureCoverageV1,
    ]:
        observations = (
            *(
                await self._observe_suite(
                    suite=projection.development,
                    top_k=protocol.retrieval_top_k,
                )
            ),
            *(
                await self._observe_suite(
                    suite=projection.tuning,
                    top_k=protocol.retrieval_top_k,
                )
            ),
        )

        provider_candidates: list[_ProviderCandidate] = []
        for observation in observations:
            if observation.provider_candidate is not None:
                provider_candidates.append(observation.provider_candidate)

        dedup = _deduplicate_provider_candidates(
            tuple(provider_candidates)
        )

        dispositions_by_query: dict[str, set[str]] = {}
        for observation in observations:
            dispositions_by_query.setdefault(
                observation.query,
                set(),
            ).add(
                observation.coverage.disposition
            )

        disposition_conflicts = sum(
            len(dispositions) > 1
            for dispositions in dispositions_by_query.values()
        )

        provider_count = sum(
            observation.coverage.disposition == "provider_reaching"
            for observation in observations
        )
        refusal_count = sum(
            observation.coverage.disposition == "pre_provider_refusal"
            for observation in observations
        )
        error_count = sum(
            observation.coverage.disposition == "prefix_error"
            for observation in observations
        )

        accepted = (
            len(observations) == 42
            and error_count == 0
            and disposition_conflicts == 0
            and dedup.duplicate_response_conflict_count == 0
            and len(dedup.entries) == dedup.distinct_provider_query_count
        )

        fixture: Phase5B0ReplayFixtureV1 | None = None
        fixture_sha256: str | None = None

        if accepted:
            fixture = Phase5B0ReplayFixtureV1(
                entries=dedup.entries,
            )
            fixture_sha256 = _model_sha256(fixture)

        coverage = Phase5B0ReplayFixtureCoverageV1(
            replay_fixture_sha256=fixture_sha256,
            provider_reaching_case_count=provider_count,
            pre_provider_refusal_case_count=refusal_count,
            unexpected_prefix_error_count=error_count,
            distinct_provider_query_count=dedup.distinct_provider_query_count,
            duplicate_provider_case_count=dedup.duplicate_provider_case_count,
            fixture_entry_count=(
                len(dedup.entries)
                if fixture is not None
                else 0
            ),
            query_disposition_conflict_count=disposition_conflicts,
            duplicate_response_conflict_count=(
                dedup.duplicate_response_conflict_count
            ),
            cases=tuple(
                sorted(
                    (
                        observation.coverage
                        for observation in observations
                    ),
                    key=lambda case: case.case_id,
                )
            ),
            materialization_decision=(
                "PASS"
                if accepted
                else "REJECT"
            ),
            replay_fixture_materialized=accepted,
        )

        return fixture, coverage


def _write_immutable_model(
    path: Path,
    value: ContractModel,
) -> str:
    expected_bytes = _stable_model_bytes(value)
    expected_sha256 = _sha256_bytes(expected_bytes)

    if path.exists():
        observed = path.read_bytes()
        if observed != expected_bytes:
            raise ValueError(
                f"refusing to overwrite different immutable artifact: {path}"
            )

        sidecar = path.with_suffix(path.suffix + ".sha256")
        expected_sidecar = f"{expected_sha256}  {path.name}"

        if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
            raise ValueError(f"immutable artifact sidecar mismatch: {path}")

        return expected_sha256

    return write_json_with_sha256(
        path,
        value,
    )


async def _build_materialization(
    repo_root: Path,
) -> tuple[
    Phase5B0ReplayFixtureV1 | None,
    Phase5B0ReplayFixtureCoverageV1,
]:
    protocol = _load_frozen_controls(
        repo_root
    )
    projection = load_phase5_b0_runtime_projection(
        repo_root
    )
    config = _b0_runtime_config(
        protocol
    )

    documents, _evidence_ids = _load_indexed_documents(
        repo_root
    )

    retriever = OperationAwareRrfRetriever(
        config=config.retrieval,
        documents=documents,
        repo_root=repo_root,
    )
    source_filter = CurrentGithubRestSourcePolicyFilter(
        config.source_policy
    )
    context_builder = BoundedContextBuilder(
        config.context
    )

    if retriever.configuration_id != config.retrieval.configuration_id:
        raise ValueError("retriever configuration identity drifted")

    if source_filter.configuration_id != config.source_policy.configuration_id:
        raise ValueError("source filter configuration identity drifted")

    if context_builder.configuration_id != config.context.configuration_id:
        raise ValueError("context builder configuration identity drifted")

    materializer = B0ReplayFixtureMaterializer(
        retriever=retriever,
        source_filter=source_filter,
        context_builder=context_builder,
    )

    first_fixture, first_coverage = await materializer.materialize(
        projection=projection,
        protocol=protocol,
    )
    second_fixture, second_coverage = await materializer.materialize(
        projection=projection,
        protocol=protocol,
    )

    if first_fixture != second_fixture:
        raise ValueError("B0 replay fixture is not deterministic across repeats")

    if first_coverage != second_coverage:
        raise ValueError("B0 replay coverage is not deterministic across repeats")

    return first_fixture, first_coverage


def materialize_phase5_b0_replay_fixture(
    repo_root: Path,
) -> tuple[
    Phase5B0ReplayFixtureCoverageV1,
    str,
    str | None,
]:
    fixture, coverage = asyncio.run(
        _build_materialization(
            repo_root
        )
    )

    fixture_sha256: str | None = None

    if fixture is not None:
        fixture_sha256 = _write_immutable_model(
            repo_root / _FIXTURE_PATH,
            fixture,
        )

        if fixture_sha256 != coverage.replay_fixture_sha256:
            raise ValueError("written replay fixture SHA does not match coverage")

    coverage_sha256 = _write_immutable_model(
        repo_root / _COVERAGE_PATH,
        coverage,
    )

    return coverage, coverage_sha256, fixture_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    coverage, coverage_sha256, fixture_sha256 = (
        materialize_phase5_b0_replay_fixture(
            repo_root
        )
    )

    print(
        "PHASE5_B0_REPLAY_MATERIALIZATION_DECISION="
        f"{coverage.materialization_decision}"
    )
    print(
        "PHASE5_B0_REPLAY_COVERAGE_SHA256="
        f"{coverage_sha256}"
    )
    print(
        "PHASE5_B0_REPLAY_FIXTURE_SHA256="
        f"{fixture_sha256 or 'NOT_MATERIALIZED'}"
    )
    print(
        "PHASE5_B0_AUTHORIZED_CASES="
        f"{coverage.authorized_case_count}"
    )
    print(
        "PHASE5_B0_PROVIDER_REACHING_CASES="
        f"{coverage.provider_reaching_case_count}"
    )
    print(
        "PHASE5_B0_PRE_PROVIDER_REFUSALS="
        f"{coverage.pre_provider_refusal_case_count}"
    )
    print(
        "PHASE5_B0_UNEXPECTED_PREFIX_ERRORS="
        f"{coverage.unexpected_prefix_error_count}"
    )
    print(
        "PHASE5_B0_DISTINCT_PROVIDER_QUERY_KEYS="
        f"{coverage.distinct_provider_query_count}"
    )
    print(
        "PHASE5_B0_DUPLICATE_PROVIDER_CASES="
        f"{coverage.duplicate_provider_case_count}"
    )
    print(
        "PHASE5_B0_QUERY_DISPOSITION_CONFLICTS="
        f"{coverage.query_disposition_conflict_count}"
    )
    print(
        "PHASE5_B0_DUPLICATE_RESPONSE_CONFLICTS="
        f"{coverage.duplicate_response_conflict_count}"
    )
    print(
        "PHASE5_B0_REPLAY_FIXTURE_MATERIALIZED="
        f"{str(coverage.replay_fixture_materialized).lower()}"
    )
    print(
        "PHASE5_B0_REPLAY_LIVE_PROVIDER_CALLS="
        f"{coverage.live_provider_call_count}"
    )
    print(
        "PHASE5_B0_REPLAY_EVALUATOR_FIELDS_USED="
        f"{str(coverage.evaluator_fields_used_for_fixture_authoring).lower()}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(coverage.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_B0_EXECUTED="
        f"{str(coverage.b0_executed).lower()}"
    )


if __name__ == "__main__":
    main()
