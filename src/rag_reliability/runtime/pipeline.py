"""Deterministic orchestration for the Phase 2A RAG mechanics slice."""

from datetime import UTC, datetime
from time import perf_counter

from rag_reliability.config.identity import RuntimeConfiguration
from rag_reliability.contracts.enums import (
    CitationValidationStatus,
    FailureLabel,
    RefusalReason,
    RuntimeErrorCode,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.interfaces import (
    CitationValidator,
    ContextBuilder,
    ProviderAdapter,
    Retriever,
    SourcePolicyFilter,
)
from rag_reliability.contracts.runtime import (
    AnswerOutcome,
    CitationValidationRequest,
    ContextBuildRequest,
    ContextItem,
    ErrorOutcome,
    ProviderRequest,
    RefusalOutcome,
    RetrievalRequest,
    RetrievedEvidence,
    SourceFilterRequest,
)
from rag_reliability.contracts.tracing import TraceEvent, TraceRecord
from rag_reliability.runtime.errors import (
    CitationValidationExecutionError,
    ComponentConfigurationMismatchError,
    ContextBudgetExhaustedError,
    ReplayResponseNotFoundError,
    RetrievalExecutionError,
    SourcePolicyExecutionError,
)
from rag_reliability.runtime.models import PipelineExecution


class DeterministicRagPipeline:
    """Run the non-chaos, non-load development path with exact config custody."""

    def __init__(
        self,
        config: RuntimeConfiguration,
        retriever: Retriever,
        source_filter: SourcePolicyFilter,
        context_builder: ContextBuilder,
        provider: ProviderAdapter,
        citation_validator: CitationValidator,
    ) -> None:
        if config.reranker is not None:
            raise ValueError("Phase 2A pipeline does not execute reranking")

        self._config = config
        self._retriever = retriever
        self._source_filter = source_filter
        self._context_builder = context_builder
        self._provider = provider
        self._citation_validator = citation_validator
        self._validate_component_configuration()

    async def run(self, case: RuntimeCaseInput) -> PipelineExecution:
        started_at = datetime.now(UTC)
        events: list[TraceEvent] = []

        retrieval_start = perf_counter()
        try:
            retrieval = await self._retriever.retrieve(
                RetrievalRequest(
                    query=case.query,
                    top_k=self._config.retrieval.top_k,
                )
            )
        except RetrievalExecutionError:
            events.append(
                self._event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.RETRIEVAL,
                    TraceStatus.ERROR,
                    retrieval_start,
                    error_code=RuntimeErrorCode.RETRIEVAL_ERROR.value,
                )
            )
            error_outcome = ErrorOutcome(
                error_code=RuntimeErrorCode.RETRIEVAL_ERROR,
                message="Retrieval could not complete.",
                retryable=False,
            )
            return self._finish(case, started_at, events, error_outcome, None)

        events.append(
            self._event(
                case.case_id,
                len(events) + 1,
                TraceStage.RETRIEVAL,
                TraceStatus.OK,
                retrieval_start,
                evidence_ids=self._evidence_ids(
                    retrieval.items
                ),
                source_ids=self._source_ids(
                    retrieval.items
                ),
            )
        )

        filtering_start = perf_counter()
        try:
            filtered = await self._source_filter.apply(
                SourceFilterRequest(candidates=retrieval.items)
            )
        except SourcePolicyExecutionError:
            events.append(
                self._event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.FILTERING,
                    TraceStatus.ERROR,
                    filtering_start,
                    error_code=RuntimeErrorCode.SOURCE_POLICY_ERROR.value,
                )
            )
            error_outcome = ErrorOutcome(
                error_code=RuntimeErrorCode.SOURCE_POLICY_ERROR,
                message="Source-policy filtering could not complete.",
                retryable=False,
            )
            return self._finish(case, started_at, events, error_outcome, None)

        events.append(
            self._event(
                case.case_id,
                len(events) + 1,
                TraceStage.FILTERING,
                TraceStatus.OK,
                filtering_start,
                evidence_ids=self._evidence_ids(
                    filtered.eligible
                ),
                source_ids=self._source_ids(
                    filtered.eligible
                ),
            )
        )

        if not filtered.eligible:
            refusal_outcome = RefusalOutcome(
                reason=RefusalReason.INSUFFICIENT_EVIDENCE,
                message="No current authoritative evidence is eligible for answering.",
            )
            events.append(
                self._instant_event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.REFUSAL_FALLBACK,
                    TraceStatus.REFUSED,
                )
            )
            primary = (
                FailureLabel.RETRIEVAL_MISS
                if not retrieval.items
                else None
            )
            return self._finish(case, started_at, events, refusal_outcome, primary)

        context_start = perf_counter()
        try:
            context = await self._context_builder.build(
                ContextBuildRequest(
                    query=case.query,
                    evidence=filtered.eligible,
                )
            )
        except ContextBudgetExhaustedError:
            events.append(
                self._event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.CONTEXT_ASSEMBLY,
                    TraceStatus.ERROR,
                    context_start,
                    error_code=RuntimeErrorCode.CONTEXT_BUILD_ERROR.value,
                )
            )
            error_outcome = ErrorOutcome(
                error_code=RuntimeErrorCode.CONTEXT_BUILD_ERROR,
                message="Eligible evidence did not fit the configured context budget.",
                retryable=False,
            )
            return self._finish(
                case,
                started_at,
                events,
                error_outcome,
                FailureLabel.CONTEXT_EXCLUSION,
            )

        events.append(
            self._event(
                case.case_id,
                len(events) + 1,
                TraceStage.CONTEXT_ASSEMBLY,
                TraceStatus.OK,
                context_start,
                evidence_ids=self._evidence_ids(
                    context.items
                ),
                source_ids=self._source_ids(
                    context.items
                ),
            )
        )

        provider_start = perf_counter()
        try:
            provider_response = await self._provider.generate(
                ProviderRequest(query=case.query, context=context)
            )
        except ReplayResponseNotFoundError:
            events.append(
                self._event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.PROVIDER_GENERATION,
                    TraceStatus.ERROR,
                    provider_start,
                    error_code=RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE.value,
                )
            )
            error_outcome = ErrorOutcome(
                error_code=RuntimeErrorCode.PROVIDER_MALFORMED_RESPONSE,
                message="Replay provider has no configured response for this query.",
                retryable=False,
            )
            return self._finish(
                case,
                started_at,
                events,
                error_outcome,
                FailureLabel.PROVIDER_MALFORMED_RESPONSE,
            )

        events.append(
            self._event(
                case.case_id,
                len(events) + 1,
                TraceStage.PROVIDER_GENERATION,
                TraceStatus.OK,
                provider_start,
                evidence_ids=provider_response.cited_evidence_ids,
                source_ids=self._source_ids_for_citations(
                    context.items,
                    provider_response.cited_evidence_ids,
                ),
            )
        )

        citation_start = perf_counter()
        try:
            validation = await self._citation_validator.validate(
                CitationValidationRequest(
                    provider_response=provider_response,
                    context=context,
                )
            )
        except CitationValidationExecutionError:
            events.append(
                self._event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.CITATION_VALIDATION,
                    TraceStatus.ERROR,
                    citation_start,
                    evidence_ids=provider_response.cited_evidence_ids,
                    source_ids=self._source_ids_for_citations(
                        context.items,
                        provider_response.cited_evidence_ids,
                    ),
                    error_code=RuntimeErrorCode.CITATION_VALIDATION_ERROR.value,
                )
            )
            error_outcome = ErrorOutcome(
                error_code=RuntimeErrorCode.CITATION_VALIDATION_ERROR,
                message="Citation validation could not complete.",
                retryable=False,
            )
            return self._finish(case, started_at, events, error_outcome, None)

        validation_status = (
            TraceStatus.OK
            if validation.all_material_claims_supported
            else TraceStatus.REFUSED
        )
        events.append(
            self._event(
                case.case_id,
                len(events) + 1,
                TraceStage.CITATION_VALIDATION,
                validation_status,
                citation_start,
                evidence_ids=provider_response.cited_evidence_ids,
                source_ids=self._source_ids_for_citations(
                    context.items,
                    provider_response.cited_evidence_ids,
                ),
            )
        )

        if not validation.all_material_claims_supported:
            refusal_outcome = RefusalOutcome(
                reason=RefusalReason.UNSUPPORTED_CITATION,
                message="The generated answer is not fully supported by cited evidence.",
            )
            events.append(
                self._instant_event(
                    case.case_id,
                    len(events) + 1,
                    TraceStage.REFUSAL_FALLBACK,
                    TraceStatus.REFUSED,
                )
            )
            primary = self._citation_failure(validation)
            return self._finish(case, started_at, events, refusal_outcome, primary)

        answer_outcome = AnswerOutcome(
            answer_text=provider_response.answer_text,
            cited_evidence_ids=provider_response.cited_evidence_ids,
            citation_validation=validation,
        )
        return self._finish(case, started_at, events, answer_outcome, None)

    @staticmethod
    def _evidence_ids(
        items: tuple[RetrievedEvidence, ...]
        | tuple[ContextItem, ...],
    ) -> tuple[str, ...]:
        return tuple(
            item.evidence_id
            for item in items
        )

    @staticmethod
    def _source_ids(
        items: tuple[RetrievedEvidence, ...]
        | tuple[ContextItem, ...],
    ) -> tuple[str, ...]:
        observed: set[str] = set()
        ordered: list[str] = []

        for item in items:
            for source_id in item.source_ids:
                if source_id in observed:
                    continue

                observed.add(source_id)
                ordered.append(source_id)

        return tuple(ordered)

    @classmethod
    def _source_ids_for_citations(
        cls,
        context_items: tuple[ContextItem, ...],
        cited_evidence_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        context_by_id = {
            item.evidence_id: item
            for item in context_items
        }

        cited_items = tuple(
            context_by_id[evidence_id]
            for evidence_id in cited_evidence_ids
            if evidence_id in context_by_id
        )

        return cls._source_ids(
            cited_items
        )

    def _validate_component_configuration(self) -> None:
        expected = {
            "retriever": self._config.retrieval.configuration_id,
            "source_filter": self._config.source_policy.configuration_id,
            "context_builder": self._config.context.configuration_id,
            "provider": self._config.provider.configuration_id,
            "citation_validator": self._config.citation.configuration_id,
        }
        actual = {
            "retriever": self._retriever.configuration_id,
            "source_filter": self._source_filter.configuration_id,
            "context_builder": self._context_builder.configuration_id,
            "provider": self._provider.configuration_id,
            "citation_validator": self._citation_validator.configuration_id,
        }

        mismatches = [
            name
            for name, expected_id in expected.items()
            if actual[name] != expected_id
        ]
        if mismatches:
            joined = ", ".join(sorted(mismatches))
            raise ComponentConfigurationMismatchError(
                f"runtime component configuration mismatch: {joined}"
            )

    def _finish(
        self,
        case: RuntimeCaseInput,
        started_at: datetime,
        events: list[TraceEvent],
        outcome: AnswerOutcome | RefusalOutcome | ErrorOutcome,
        primary_failure: FailureLabel | None,
    ) -> PipelineExecution:
        trace = TraceRecord(
            trace_id=f"trace:{case.case_id}:{self._config.configuration_id[:12]}",
            case_id=case.case_id,
            configuration_id=self._config.configuration_id,
            started_at=started_at,
            ended_at=datetime.now(UTC),
            events=tuple(events),
            primary_failure=primary_failure,
        )
        return PipelineExecution(outcome=outcome, trace=trace)

    @staticmethod
    def _event(
        case_id: str,
        sequence: int,
        stage: TraceStage,
        status: TraceStatus,
        started: float,
        evidence_ids: tuple[str, ...] = (),
        source_ids: tuple[str, ...] = (),
        error_code: str | None = None,
    ) -> TraceEvent:
        return TraceEvent(
            event_id=f"{case_id}:{sequence}:{stage.value}",
            stage=stage,
            status=status,
            occurred_at=datetime.now(UTC),
            duration_ms=(perf_counter() - started) * 1000,
            evidence_ids=evidence_ids,
            source_ids=source_ids,
            error_code=error_code,
        )

    @staticmethod
    def _instant_event(
        case_id: str,
        sequence: int,
        stage: TraceStage,
        status: TraceStatus,
    ) -> TraceEvent:
        return TraceEvent(
            event_id=f"{case_id}:{sequence}:{stage.value}",
            stage=stage,
            status=status,
            occurred_at=datetime.now(UTC),
            duration_ms=0.0,
        )

    @staticmethod
    def _citation_failure(validation: object) -> FailureLabel:
        from rag_reliability.contracts.runtime import CitationValidationResult

        if not isinstance(validation, CitationValidationResult):
            raise TypeError("validation must be CitationValidationResult")

        if any(
            check.status is CitationValidationStatus.MISSING
            for check in validation.checks
        ):
            return FailureLabel.CITATION_MISSING
        return FailureLabel.CITATION_NOT_SUPPORTED
