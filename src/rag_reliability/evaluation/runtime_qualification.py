"""Execute the frozen G5K runtime/control-lane qualification."""

from __future__ import annotations

import asyncio
import hashlib
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
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    FailureLabel,
    RefusalReason,
    RuntimeErrorCode,
    SourceState,
)
from rag_reliability.contracts.evaluation import EvaluationCase, RuntimeCaseInput
from rag_reliability.contracts.interfaces import ProviderAdapter
from rag_reliability.contracts.runtime import (
    ContextBuildRequest,
    ErrorOutcome,
    ProviderDecision,
    ProviderRequest,
    RefusalOutcome,
    RetrievalRequest,
    RetrievalResult,
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.bm25_candidate_experiment import (
    Phase5Bm25CandidateConfig,
    _Bm25CandidateRetriever,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
    _load_tuning_cases,
)
from rag_reliability.evaluation.rrf_hybrid_candidate_experiment import (
    Phase5RrfHybridCandidateConfig,
    _fuse_rankings,
)
from rag_reliability.evaluation.runtime_qualification_protocol import (
    Phase5G5kRuntimeQualificationProtocolV1,
)
from rag_reliability.evaluation.runtime_qualification_protocol_freeze import (
    Phase5G5kRuntimeQualificationProtocolFreezeV1,
)
from rag_reliability.evaluation.semantic_runtime_development_confirmation import (
    _load_development_cases,
)
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.errors import (
    ProviderMalformedResponseError,
    ProviderTimeoutError,
)
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import (
    IndexedDocument,
    PipelineExecution,
    ReplayEntry,
)
from rag_reliability.runtime.operation_aware_ranking import (
    stable_partition_by_operation_lineage,
)
from rag_reliability.runtime.operation_aware_rrf_retriever import (
    OperationAwareRrfRetriever,
)
from rag_reliability.runtime.operation_catalog import load_runtime_operation_catalog
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
)
from rag_reliability.runtime.pipeline import DeterministicRagPipeline
from rag_reliability.runtime.provider import ReplayProvider
from rag_reliability.runtime.retrieval import LexicalRetriever

_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_g5k_runtime_qualification_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_g5k_runtime_qualification_protocol_freeze_v1.json"
)
_CHUNK_MANIFEST_PATH = (
    Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_g5k_runtime_qualification_v1.json"
)

_PROTOCOL_SHA256: Sha256 = (
    "8581d5a7382ef41c1dcd3cb9e2ca7b9951b79afa175b83327c7df6b20d762724"
)
_FREEZE_SHA256: Sha256 = (
    "d0d89d485e53e0e115b4254c47b399b81a8c415c44bcd77fb28b0b93b087f185"
)
_CHUNK_MANIFEST_SHA256: Sha256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

_REQUIRED_CONTROL_IDS = (
    "selected_retriever_reference_parity_on_development_and_tuning_queries",
    "supported_answer_full_path",
    "source_policy_refusal_full_path",
    "unsupported_citation_safe_refusal",
    "provider_timeout_terminal_error",
    "provider_malformed_response_terminal_error",
)

_REQUIRED_METRIC_IDS = (
    "strict_answer_success",
    "required_fact_satisfaction",
    "gold_recall_at_k",
    "required_evidence_context_inclusion",
    "claim_support",
    "citation_precision",
    "citation_recall",
    "correct_refusal",
    "over_refusal",
    "critical_failure_count",
    "trace_completeness",
    "latency_ms",
    "provider_attempt_count",
)


class G5kControlCheck(ContractModel):
    control_id: NonEmptyStr
    passed: bool


class G5kScorerApplicability(ContractModel):
    metric_id: NonEmptyStr
    applicable: bool
    interpretation: NonEmptyStr


class Phase5G5kRuntimeQualificationV1(ContractModel):
    """Evidence-backed G5K result without B0 or protected execution."""

    receipt_version: Literal[
        "phase5-g5k-runtime-qualification-v1"
    ] = "phase5-g5k-runtime-qualification-v1"

    protocol_sha256: Sha256 = _PROTOCOL_SHA256
    protocol_freeze_sha256: Sha256 = _FREEZE_SHA256

    selected_retrieval_id: Literal[
        "phase5-operation-aware-rrf-stable-partition-v1"
    ] = "phase5-operation-aware-rrf-stable-partition-v1"

    runtime_configuration_id: Sha256

    development_query_count: Literal[24] = 24
    tuning_query_count: Literal[18] = 18
    retrieval_parity_case_count: Literal[42] = 42
    retrieval_parity_mismatch_count: int = Field(ge=0, le=42)

    control_checks: tuple[
        G5kControlCheck,
        ...,
    ] = Field(min_length=6, max_length=6)

    scorer_applicability: tuple[
        G5kScorerApplicability,
        ...,
    ] = Field(min_length=13, max_length=13)

    lane_a_provider_mode: Literal[
        "query_keyed_scripted_response"
    ] = "query_keyed_scripted_response"
    lane_a_generation_is_context_sensitive: Literal[False] = False
    lane_a_complete_runtime_qualified: bool

    lane_b_model_id: Literal["glm-5.2"] = "glm-5.2"
    lane_b_live_qualification_bound: Literal[True] = True
    lane_b_new_live_calls_executed: Literal[0] = 0

    runtime_evaluator_separation_preserved: Literal[True] = True
    automatic_retries_added: Literal[False] = False

    qualification_decision: Literal["PASS", "REJECT"]
    post_reject_confirmation_deferred: Literal[True] = True
    advance_to_g5m_b0_selection: bool

    protected_confirmation_authorized: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_receipt(self) -> Self:
        observed_controls = tuple(
            item.control_id
            for item in self.control_checks
        )
        if observed_controls != _REQUIRED_CONTROL_IDS:
            raise ValueError("G5K control set drifted")

        observed_metrics = tuple(
            item.metric_id
            for item in self.scorer_applicability
        )
        if observed_metrics != _REQUIRED_METRIC_IDS:
            raise ValueError("G5K scorer-applicability set drifted")

        accepted = (
            self.retrieval_parity_mismatch_count == 0
            and all(item.passed for item in self.control_checks)
            and all(item.applicable for item in self.scorer_applicability)
            and self.runtime_evaluator_separation_preserved
            and not self.automatic_retries_added
            and self.lane_b_new_live_calls_executed == 0
        )

        expected_decision = "PASS" if accepted else "REJECT"

        if self.qualification_decision != expected_decision:
            raise ValueError("G5K qualification decision does not reconcile")

        if self.lane_a_complete_runtime_qualified != accepted:
            raise ValueError("Lane A qualification state does not reconcile")

        if self.advance_to_g5m_b0_selection != accepted:
            raise ValueError("G5M advancement state does not reconcile")

        if not self.post_reject_confirmation_deferred:
            raise ValueError("G5L must remain deferred for the rejected successor")

        if (
            self.protected_confirmation_authorized
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("G5K qualification overclaims downstream state")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(
    path: Path,
    expected_sha256: str,
) -> bytes:
    content = path.read_bytes()

    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(f"frozen artifact sidecar mismatch: {path}")

    return content


def _qualification_runtime_config() -> RuntimeConfiguration:
    return RuntimeConfiguration(
        schema_version="phase5-g5k-runtime-qualification-v1",
        retrieval=RetrievalConfig(
            retriever_id=(
                "phase5-operation-aware-rrf-stable-partition-v1"
            ),
            top_k=20,
        ),
        source_policy=SourcePolicyConfig(
            policy_id="github-rest-current-v1",
        ),
        reranker=None,
        context=ContextConfig(
            builder_id="bounded-context-v1",
            budget_unit_id="characters",
            max_budget=69663,
            max_evidence_items=15,
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


def _load_protocol_controls(
    repo_root: Path,
) -> tuple[
    Phase5G5kRuntimeQualificationProtocolV1,
    Phase5G5kRuntimeQualificationProtocolFreezeV1,
]:
    protocol = Phase5G5kRuntimeQualificationProtocolV1.model_validate_json(
        _verified_bytes(
            repo_root / _PROTOCOL_PATH,
            _PROTOCOL_SHA256,
        )
    )

    freeze = Phase5G5kRuntimeQualificationProtocolFreezeV1.model_validate_json(
        _verified_bytes(
            repo_root / _FREEZE_PATH,
            _FREEZE_SHA256,
        )
    )

    if freeze.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("G5K freeze does not bind expected protocol")

    if not freeze.protocol_frozen:
        raise ValueError("G5K protocol is not frozen")

    return protocol, freeze


def _lineage_map(
    repo_root: Path,
) -> dict[str, tuple[str, ...]]:
    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            repo_root / _CHUNK_MANIFEST_PATH,
            _CHUNK_MANIFEST_SHA256,
        )
    )
    return {
        chunk.chunk_id: tuple(chunk.linked_operation_ids)
        for chunk in manifest.chunks
    }


async def _retriever_parity(
    *,
    repo_root: Path,
    documents: tuple[IndexedDocument, ...],
    cases: tuple[EvaluationCase, ...],
    config: RuntimeConfiguration,
) -> int:
    runtime = OperationAwareRrfRetriever(
        config=config.retrieval,
        documents=documents,
        repo_root=repo_root,
    )

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
    lineage = _lineage_map(repo_root)

    mismatch_count = 0

    for case in cases:
        actual = (
            await runtime.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=20,
                )
            )
        ).items

        lexical_items = (
            await lexical.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=rrf_config.characterization_top_k,
                )
            )
        ).items

        generic = _fuse_rankings(
            lexical_items=lexical_items,
            bm25_items=bm25.retrieve(case.query),
            config=rrf_config,
        )

        expected = stable_partition_by_operation_lineage(
            items=generic,
            resolution=resolver.resolve(case.query),
            linked_operation_ids_by_evidence_id=lineage,
        )[:20]

        if actual != expected:
            mismatch_count += 1

    return mismatch_count


class _StaticRetriever:
    def __init__(
        self,
        config: RetrievalConfig,
        items: tuple[RetrievedEvidence, ...],
    ) -> None:
        self._config = config
        self._items = items

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        return RetrievalResult(
            items=self._items[: request.top_k]
        )


class _TimeoutProvider:
    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderDecision:
        raise ProviderTimeoutError(
            "deterministic G5K timeout control"
        )


class _MalformedProvider:
    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderDecision:
        raise ProviderMalformedResponseError(
            "deterministic G5K malformed control"
        )


def _fixture_document(
    *,
    current: bool = True,
) -> IndexedDocument:
    return IndexedDocument(
        evidence_id=(
            "g5k-current-evidence"
            if current
            else "g5k-historical-evidence"
        ),
        source_ids=("g5k-source",),
        document_ids=("g5k-document",),
        content=(
            "Requests may include the "
            "X-GitHub-Api-Version header."
        ),
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=(
            SourceState.CURRENT
            if current
            else SourceState.HISTORICAL_COMPARISON
        ),
        product_scope="api.github.com",
        api_version_or_snapshot=(
            "2026-03-10"
            if current
            else "2022-11-28"
        ),
        synthetic_overlay=False,
        eligible_as_final_citation=True,
    )


def _as_retrieved(
    document: IndexedDocument,
) -> RetrievedEvidence:
    return RetrievedEvidence(
        evidence_id=document.evidence_id,
        source_ids=document.source_ids,
        document_ids=document.document_ids,
        content=document.content,
        rank=1,
        score=1.0,
        authority_level=document.authority_level,
        source_state=document.source_state,
        product_scope=document.product_scope,
        api_version_or_snapshot=document.api_version_or_snapshot,
        synthetic_overlay=document.synthetic_overlay,
        eligible_as_final_citation=document.eligible_as_final_citation,
    )


async def _control_supported_answer(
    *,
    repo_root: Path,
    documents: tuple[IndexedDocument, ...],
    cases: tuple[EvaluationCase, ...],
    config: RuntimeConfiguration,
) -> bool:
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

    for case in sorted(
        cases,
        key=lambda item: item.case_id,
    ):
        retrieved = await retriever.retrieve(
            RetrievalRequest(
                query=case.query,
                top_k=20,
            )
        )

        filtered = await source_filter.apply(
            SourceFilterRequest(
                candidates=retrieved.items
            )
        )

        if not filtered.eligible:
            continue

        context = await context_builder.build(
            ContextBuildRequest(
                query=case.query,
                evidence=filtered.eligible,
            )
        )

        if not context.items:
            continue

        cited = context.items[0]

        provider = ReplayProvider(
            config.provider,
            (
                ReplayEntry(
                    query=case.query,
                    answer_text=cited.content,
                    cited_evidence_ids=(
                        cited.evidence_id,
                    ),
                ),
            ),
        )

        pipeline = DeterministicRagPipeline(
            config=config,
            retriever=retriever,
            source_filter=source_filter,
            context_builder=context_builder,
            provider=provider,
            citation_validator=ExactCitationValidator(
                config.citation
            ),
        )

        execution = await pipeline.run(
            RuntimeCaseInput(
                case_id="g5k-supported-answer",
                query=case.query,
            )
        )

        return (
            execution.outcome.status == "answer"
            and execution.trace.primary_failure is None
        )

    return False


async def _fixture_pipeline_execution(
    *,
    config: RuntimeConfiguration,
    document: IndexedDocument,
    provider: ProviderAdapter,
) -> PipelineExecution:
    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=_StaticRetriever(
            config.retrieval,
            (_as_retrieved(document),),
        ),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            config.source_policy
        ),
        context_builder=BoundedContextBuilder(
            config.context
        ),
        provider=provider,
        citation_validator=ExactCitationValidator(
            config.citation
        ),
    )

    return await pipeline.run(
        RuntimeCaseInput(
            case_id="g5k-fixture",
            query="g5k fixture query",
        )
    )


async def _run_controls(
    *,
    repo_root: Path,
    documents: tuple[IndexedDocument, ...],
    cases: tuple[EvaluationCase, ...],
    config: RuntimeConfiguration,
    mismatch_count: int,
) -> tuple[G5kControlCheck, ...]:
    supported_answer = await _control_supported_answer(
        repo_root=repo_root,
        documents=documents,
        cases=cases,
        config=config,
    )

    source_refusal = await _fixture_pipeline_execution(
        config=config,
        document=_fixture_document(
            current=False
        ),
        provider=ReplayProvider(
            config.provider,
            (),
        ),
    )

    current = _fixture_document(
        current=True
    )

    unsupported = await _fixture_pipeline_execution(
        config=config,
        document=current,
        provider=ReplayProvider(
            config.provider,
            (
                ReplayEntry(
                    query="g5k fixture query",
                    answer_text=(
                        "This sentence is not present "
                        "in the cited evidence."
                    ),
                    cited_evidence_ids=(
                        current.evidence_id,
                    ),
                ),
            ),
        ),
    )

    timed_out = await _fixture_pipeline_execution(
        config=config,
        document=current,
        provider=_TimeoutProvider(
            config.provider
        ),
    )

    malformed = await _fixture_pipeline_execution(
        config=config,
        document=current,
        provider=_MalformedProvider(
            config.provider
        ),
    )

    source_refusal_passed = (
        isinstance(
            source_refusal.outcome,
            RefusalOutcome,
        )
        and source_refusal.outcome.reason
        is RefusalReason.INSUFFICIENT_EVIDENCE
    )

    unsupported_passed = (
        isinstance(
            unsupported.outcome,
            RefusalOutcome,
        )
        and unsupported.outcome.reason
        is RefusalReason.UNSUPPORTED_CITATION
        and unsupported.trace.primary_failure
        is FailureLabel.CITATION_NOT_SUPPORTED
    )

    timeout_passed = (
        isinstance(
            timed_out.outcome,
            ErrorOutcome,
        )
        and timed_out.outcome.error_code
        is RuntimeErrorCode.PROVIDER_TIMEOUT
        and timed_out.trace.primary_failure
        is FailureLabel.PROVIDER_TIMEOUT
        and timed_out.outcome.retryable is False
    )

    malformed_passed = (
        isinstance(
            malformed.outcome,
            ErrorOutcome,
        )
        and malformed.outcome.error_code
        is RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE
        and malformed.trace.primary_failure
        is FailureLabel.PROVIDER_MALFORMED_RESPONSE
        and malformed.outcome.retryable is False
    )

    return (
        G5kControlCheck(
            control_id=_REQUIRED_CONTROL_IDS[0],
            passed=(mismatch_count == 0),
        ),
        G5kControlCheck(
            control_id=_REQUIRED_CONTROL_IDS[1],
            passed=supported_answer,
        ),
        G5kControlCheck(
            control_id=_REQUIRED_CONTROL_IDS[2],
            passed=source_refusal_passed,
        ),
        G5kControlCheck(
            control_id=_REQUIRED_CONTROL_IDS[3],
            passed=unsupported_passed,
        ),
        G5kControlCheck(
            control_id=_REQUIRED_CONTROL_IDS[4],
            passed=timeout_passed,
        ),
        G5kControlCheck(
            control_id=_REQUIRED_CONTROL_IDS[5],
            passed=malformed_passed,
        ),
    )


def _scorer_applicability(
) -> tuple[G5kScorerApplicability, ...]:
    interpretations = {
        "strict_answer_success": (
            "Applicable to Lane A outputs with evaluator-owned correctness "
            "checks; not evidence of learned-model reasoning."
        ),
        "required_fact_satisfaction": (
            "Applicable only through evaluator-owned post-run fact verdicts; "
            "the replay table is not an independent correctness scorer."
        ),
        "gold_recall_at_k": (
            "Applicable post-run to retrieval output; gold evidence never "
            "enters runtime routing."
        ),
        "required_evidence_context_inclusion": (
            "Applicable post-run to assembled context; evaluator truth remains "
            "outside runtime."
        ),
        "claim_support": (
            "Applicable to the declared exact-support citation validator and "
            "must not be generalized to semantic entailment."
        ),
        "citation_precision": (
            "Applicable post-run against evaluator-owned required evidence."
        ),
        "citation_recall": (
            "Applicable post-run against evaluator-owned required evidence."
        ),
        "correct_refusal": (
            "Applicable to deterministic refusal control flow."
        ),
        "over_refusal": (
            "Applicable descriptively to Lane A answerable cases."
        ),
        "critical_failure_count": (
            "Applicable using the frozen failure taxonomy and "
            "earliest-supported failure rule."
        ),
        "trace_completeness": (
            "Applicable to the complete deterministic pipeline trace."
        ),
        "latency_ms": (
            "Applicable only to Lane A local runtime timing; it is not "
            "GLM-5.2 provider latency evidence."
        ),
        "provider_attempt_count": (
            "Applicable to Lane A replay-provider invocation accounting."
        ),
    }

    return tuple(
        G5kScorerApplicability(
            metric_id=metric_id,
            applicable=True,
            interpretation=interpretations[
                metric_id
            ],
        )
        for metric_id in _REQUIRED_METRIC_IDS
    )


async def _build_receipt(
    repo_root: Path,
) -> Phase5G5kRuntimeQualificationV1:
    protocol, _freeze = _load_protocol_controls(
        repo_root
    )

    if protocol.lane_b_new_live_calls_authorized != 0:
        raise ValueError(
            "frozen protocol unexpectedly authorizes live calls"
        )

    documents, _evidence_ids = _load_indexed_documents(
        repo_root
    )
    development = _load_development_cases(
        repo_root
    )
    tuning = _load_tuning_cases(
        repo_root
    )
    cases = (
        *development,
        *tuning,
    )

    if len(cases) != 42:
        raise ValueError(
            "G5K parity projection must contain 42 exposed cases"
        )

    config = _qualification_runtime_config()

    mismatch_count = await _retriever_parity(
        repo_root=repo_root,
        documents=documents,
        cases=cases,
        config=config,
    )

    controls = await _run_controls(
        repo_root=repo_root,
        documents=documents,
        cases=cases,
        config=config,
        mismatch_count=mismatch_count,
    )

    scorers = _scorer_applicability()

    accepted = (
        mismatch_count == 0
        and all(item.passed for item in controls)
        and all(item.applicable for item in scorers)
    )

    return Phase5G5kRuntimeQualificationV1(
        runtime_configuration_id=config.configuration_id,
        retrieval_parity_mismatch_count=mismatch_count,
        control_checks=controls,
        scorer_applicability=scorers,
        lane_a_complete_runtime_qualified=accepted,
        qualification_decision=(
            "PASS"
            if accepted
            else "REJECT"
        ),
        advance_to_g5m_b0_selection=accepted,
    )


def materialize_phase5_g5k_runtime_qualification(
    repo_root: Path,
) -> tuple[
    Phase5G5kRuntimeQualificationV1,
    str,
]:
    receipt = asyncio.run(
        _build_receipt(
            repo_root
        )
    )

    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        receipt,
    )

    return receipt, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    receipt, digest = (
        materialize_phase5_g5k_runtime_qualification(
            repo_root
        )
    )

    print(
        "PHASE5_G5K_RUNTIME_QUALIFICATION_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_G5K_RUNTIME_CONFIGURATION_ID="
        f"{receipt.runtime_configuration_id}"
    )
    print(
        "PHASE5_G5K_RETRIEVAL_PARITY="
        f"{receipt.retrieval_parity_case_count - receipt.retrieval_parity_mismatch_count}/"
        f"{receipt.retrieval_parity_case_count}"
    )
    print(
        "PHASE5_G5K_CONTROL_CHECKS="
        f"{sum(item.passed for item in receipt.control_checks)}/"
        f"{len(receipt.control_checks)}"
    )
    print(
        "PHASE5_G5K_SCORER_APPLICABILITY="
        f"{sum(item.applicable for item in receipt.scorer_applicability)}/"
        f"{len(receipt.scorer_applicability)}"
    )
    print(
        "PHASE5_G5K_QUALIFICATION_DECISION="
        f"{receipt.qualification_decision}"
    )

    for control in receipt.control_checks:
        if not control.passed:
            print(
                "PHASE5_G5K_FAILED_CONTROL="
                f"{control.control_id}"
            )

    print(
        "PHASE5_G5K_LANE_A_COMPLETE_RUNTIME_QUALIFIED="
        f"{str(receipt.lane_a_complete_runtime_qualified).lower()}"
    )
    print(
        "PHASE5_G5K_LANE_B_NEW_LIVE_CALLS_EXECUTED="
        f"{receipt.lane_b_new_live_calls_executed}"
    )
    print(
        "PHASE5_POST_REJECT_CONFIRMATION_DEFERRED="
        f"{str(receipt.post_reject_confirmation_deferred).lower()}"
    )
    print(
        "PHASE5_ADVANCE_TO_G5M_B0_SELECTION="
        f"{str(receipt.advance_to_g5m_b0_selection).lower()}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(receipt.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_B0_EXECUTED="
        f"{str(receipt.b0_executed).lower()}"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED="
        f"{str(receipt.held_out_outcomes_exposed).lower()}"
    )


if __name__ == "__main__":
    main()
