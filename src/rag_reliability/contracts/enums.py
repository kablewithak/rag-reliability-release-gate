"""Frozen enum values derived from Phase 0 governance."""

from enum import StrEnum


class DataRole(StrEnum):
    UNIT_FIXTURE = "unit_fixture"
    CORPUS_SOURCE = "corpus_source"
    HISTORICAL_SOURCE = "historical_source"
    BACKGROUND_LOAD_SOURCE = "background_load_source"
    CHAOS_OVERLAY = "chaos_overlay"
    EVALUATION_DEVELOPMENT_CASE = "evaluation_development_case"
    INTERVENTION_TUNING_CASE = "intervention_tuning_case"
    HELD_OUT_RELEASE_CASE = "held_out_release_case"
    LOAD_TEST_REPLAY_CASE = "load_test_replay_case"
    PUBLIC_DEMONSTRATION_ARTIFACT = "public_demonstration_artifact"


class CorpusSourceFamily(StrEnum):
    GITHUB_REST_AUTHORED_GUIDANCE = "github_rest_authored_guidance"
    OPENAPI_ENDPOINT_CONTRACT = "openapi_endpoint_contract"


class AuthorityLevel(StrEnum):
    AUTHORITATIVE = "authoritative"
    HISTORICAL = "historical"
    NONE = "none"


class SourceState(StrEnum):
    CURRENT = "current"
    HISTORICAL_COMPARISON = "historical_comparison"


class ChaosPurpose(StrEnum):
    SEMANTIC_DISTRACTOR = "semantic_distractor"
    NEUTRAL_FILLER = "neutral_filler"
    DUPLICATE_EVIDENCE = "duplicate_evidence"
    METADATA_MUTATION = "metadata_mutation"
    CONTROLLED_CONFLICT = "controlled_conflict"
    CONTEXT_ORDER_MUTATION = "context_order_mutation"
    MALFORMED_RECORD_FIXTURE = "malformed_record_fixture"
    DEPENDENCY_FAULT_FIXTURE = "dependency_fault_fixture"


class EvaluationRole(StrEnum):
    DEVELOPMENT = "evaluation_development_case"
    TUNING = "intervention_tuning_case"
    HELD_OUT = "held_out_release_case"


class EvaluationSourceFamily(StrEnum):
    ISSUES = "issues"
    PULL_REQUESTS = "pull_requests"
    REPOSITORIES_AND_REPOSITORY_WEBHOOKS = "repositories_and_repository_webhooks"
    ACTIONS = "actions"
    CROSS_CUTTING_REST_GUIDANCE = "cross_cutting_rest_guidance"


class ScenarioClass(StrEnum):
    CURRENT_SINGLE_SOURCE_ANSWERABLE = "current_single_source_answerable"
    CURRENT_MULTI_EVIDENCE_ANSWERABLE = "current_multi_evidence_answerable"
    VERSION_FRESHNESS_DISAMBIGUATION = "version_freshness_disambiguation"
    AUTHORITY_SCOPE_DISAMBIGUATION = "authority_scope_disambiguation"
    MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE = (
        "must_refuse_insufficient_or_conflicting_evidence"
    )


class Criticality(StrEnum):
    CRITICAL = "critical"
    NONCRITICAL = "noncritical"


class ResponseMode(StrEnum):
    ANSWER = "answer"
    QUALIFIED_ANSWER = "qualified_answer"
    REFUSE = "refuse"


class FailureLabel(StrEnum):
    RETRIEVAL_MISS = "retrieval_miss"
    CONTEXT_EXCLUSION = "context_exclusion"
    CONTEXT_DILUTION = "context_dilution"
    GOLD_EVIDENCE_TRUNCATED = "gold_evidence_truncated"
    STALE_SOURCE_SELECTED = "stale_source_selected"
    SOURCE_CONFLICT_UNRESOLVED = "source_conflict_unresolved"
    METADATA_SCOPE_FAILURE = "metadata_scope_failure"
    CITATION_NOT_SUPPORTED = "citation_not_supported"
    CITATION_MISSING = "citation_missing"
    UNSUPPORTED_ANSWER = "unsupported_answer"
    UNSAFE_ANSWER = "unsafe_answer"
    UNSAFE_REFUSAL = "unsafe_refusal"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_MALFORMED_RESPONSE = "provider_malformed_response"
    RERANKER_UNAVAILABLE = "reranker_unavailable"
    RETRY_EXHAUSTED = "retry_exhausted"
    LOAD_SHEDDING = "load_shedding"
    QUEUE_SATURATION = "queue_saturation"
    TRACE_INCOMPLETE = "trace_incomplete"
    RECOVERY_INCOMPLETE = "recovery_incomplete"
    SEMANTIC_RECOVERY_LAG = "semantic_recovery_lag"
    EVALUATION_INTEGRITY_VIOLATION = "evaluation_integrity_violation"
    CORPUS_MANIFEST_INVALID = "corpus_manifest_invalid"
    AUTHORITATIVE_SOURCE_VIOLATION = "authoritative_source_violation"
    CONFIGURATION_IDENTITY_MISMATCH = "configuration_identity_mismatch"
    RELEASE_EVIDENCE_INCOMPLETE = "release_evidence_incomplete"
    PUBLIC_SANITIZATION_FAILURE = "public_sanitization_failure"


class TraceStage(StrEnum):
    RETRIEVAL = "retrieval"
    FILTERING = "filtering"
    CONTEXT_ASSEMBLY = "context_assembly"
    PROVIDER_GENERATION = "provider_generation"
    CITATION_VALIDATION = "citation_validation"
    REFUSAL_FALLBACK = "refusal_fallback"


class TraceStatus(StrEnum):
    OK = "ok"
    REFUSED = "refused"
    ERROR = "error"
    SKIPPED = "skipped"


class ChaosProfileId(StrEnum):
    CLEAN = "CR-CLEAN"
    LONG_CONTEXT = "CR-LONG-CONTEXT"
    MIDDLE_EVIDENCE = "CR-MIDDLE-EVIDENCE"
    SEMANTIC_DISTRACTOR = "CR-SEMANTIC-DISTRACTOR"
    STALE_CONFLICT = "CR-STALE-CONFLICT"
    WRONG_SCOPE = "CR-WRONG-SCOPE"
    RERANKER_DOWN = "CR-RERANKER-DOWN"
    PROVIDER_DELAY = "CR-PROVIDER-DELAY"
    HIGH_LOAD = "CR-HIGH-LOAD"
    LOAD_STALE_CONFLICT = "CR-LOAD-STALE-CONFLICT"
    LOAD_PROVIDER_FAULT = "CR-LOAD-PROVIDER-FAULT"
    FLAGSHIP_CASCADE = "CR-FLAGSHIP-CASCADE"


class LoadBand(StrEnum):
    CLEAN = "clean"
    MODERATE = "moderate"
    HIGH = "high"


class BlastRadiusTarget(StrEnum):
    LOCAL_RAG_PROCESS = "local_rag_process"
    FAKE_REPLAY_PROVIDER = "fake_replay_provider"
    RETRIEVER_RERANKER = "retriever_reranker"
    LOCAL_EXPERIMENT_STATE = "local_experiment_state"
    SYNTHETIC_OVERLAY = "synthetic_overlay"
    CORPUS_COMPETITION_VIEW = "corpus_competition_view"
    LOCAL_HTTP_SEAM = "local_http_seam"


class ReleaseVerdict(StrEnum):
    PASS = "PASS"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"
    FAIL = "FAIL"
