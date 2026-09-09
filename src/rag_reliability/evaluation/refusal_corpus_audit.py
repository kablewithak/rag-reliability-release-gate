"""Phase 4C full-corpus candidate discovery for provisional refusals."""

from __future__ import annotations

import hashlib
import html
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import (
    EvaluationRole,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.authoring_dossier import (
    PHASE4_CONSTITUTION_SHA256,
    Phase4AuthoringDossier,
)
from rag_reliability.evaluation.full_corpus import (
    PHASE3D_CHUNK_COUNT,
    PHASE3D_CHUNK_MANIFEST_SHA256,
    load_phase3d_indexed_documents,
)
from rag_reliability.runtime.models import (
    IndexedDocument,
)

RefusalPattern = Literal[
    "future_version_unknown",
    "silent_mutation_cause",
    "status_cause",
    "pending_state_unknown",
    "user_state_unknown",
]

ReviewVerdict = Literal[
    "review_required"
]

_DETAIL_LIMIT = 25

_DOSSIER_RELATIVE_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_authoring_dossier_v1.json"
)

_AUDIT_JSON_RELATIVE_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_refusal_full_corpus_audit_v1.json"
)

_AUDIT_MARKDOWN_RELATIVE_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_refusal_full_corpus_audit_v1.md"
)


class RefusalAuditIntent(
    ContractModel
):
    """One provisional refusal proposition to challenge."""

    intent_id: NonEmptyStr
    cluster_id: NonEmptyStr
    evaluation_role: EvaluationRole
    pattern_family: RefusalPattern
    refusal_claim: NonEmptyStr

    topic_terms: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=1
    )

    diagnostic_terms: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_terms(
        self,
    ) -> Self:
        all_terms = (
            *self.topic_terms,
            *self.diagnostic_terms,
        )

        normalized = tuple(
            term.casefold()
            for term in all_terms
        )

        if (
            len(normalized)
            != len(set(normalized))
        ):
            raise ValueError(
                "audit terms must be unique "
                "within an intent"
            )

        return self


class RefusalAuditCandidate(
    ContractModel
):
    """One runtime chunk surfaced for human refusal review."""

    evidence_id: NonEmptyStr

    source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=1
    )

    document_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=1
    )

    authority_level: NonEmptyStr
    source_state: NonEmptyStr
    api_version_or_snapshot: NonEmptyStr

    matched_topic_terms: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    matched_diagnostic_terms: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    score: int = Field(
        gt=0
    )

    phase4_gold_evidence: bool

    content_preview: NonEmptyStr

    @model_validator(mode="after")
    def validate_matches(
        self,
    ) -> Self:
        if (
            not self.matched_topic_terms
            and not self.matched_diagnostic_terms
        ):
            raise ValueError(
                "candidate requires at least "
                "one matched audit term"
            )

        return self


class RefusalAuditIntentResult(
    ContractModel
):
    """Candidate-discovery result for one refusal intent."""

    intent: RefusalAuditIntent

    candidate_count: int = Field(
        ge=1
    )

    cross_gold_candidate_count: int = Field(
        ge=0
    )

    candidate_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=1
    )

    detailed_candidates: tuple[
        RefusalAuditCandidate,
        ...,
    ] = Field(
        min_length=1,
        max_length=_DETAIL_LIMIT,
    )

    verdict: ReviewVerdict = (
        "review_required"
    )

    @model_validator(mode="after")
    def validate_result(
        self,
    ) -> Self:
        if (
            self.candidate_count
            != len(
                self.candidate_evidence_ids
            )
        ):
            raise ValueError(
                "candidate count mismatch"
            )

        if (
            len(
                self.candidate_evidence_ids
            )
            != len(
                set(
                    self.candidate_evidence_ids
                )
            )
        ):
            raise ValueError(
                "candidate evidence IDs "
                "must be unique"
            )

        candidate_ids = set(
            self.candidate_evidence_ids
        )

        if any(
            candidate.evidence_id
            not in candidate_ids
            for candidate
            in self.detailed_candidates
        ):
            raise ValueError(
                "detailed candidate missing "
                "from full candidate set"
            )

        scores = tuple(
            candidate.score
            for candidate
            in self.detailed_candidates
        )

        if scores != tuple(
            sorted(
                scores,
                reverse=True,
            )
        ):
            raise ValueError(
                "detailed candidates must "
                "be score ordered"
            )

        return self


class Phase4RefusalFullCorpusAudit(
    ContractModel
):
    """Read-only refusal candidate-discovery artifact."""

    audit_version: Literal[
        "phase4c-refusal-full-corpus-audit-v1"
    ] = (
        "phase4c-refusal-full-corpus-audit-v1"
    )

    phase3d_chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = (
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    )

    phase4_constitution_sha256: Literal[
        "e2f1ca0985157ea43e7e648fa431e30c2b139cf9b3ea364d7356e8e11311816d"
    ] = PHASE4_CONSTITUTION_SHA256

    authoring_dossier_sha256: Sha256
    review_markdown_sha256: Sha256

    runtime_corpus_count: Literal[
        1333
    ] = 1333

    refusal_intent_count: Literal[
        10
    ] = 10

    final_verdict_count: Literal[
        0
    ] = 0

    canonical_case_authoring_started: Literal[
        False
    ] = False

    baseline_authorized: Literal[
        False
    ] = False

    release_eligible: Literal[
        False
    ] = False

    results: tuple[
        RefusalAuditIntentResult,
        ...,
    ] = Field(
        min_length=10,
        max_length=10,
    )

    @model_validator(mode="after")
    def validate_audit(
        self,
    ) -> Self:
        intent_ids = tuple(
            result.intent.intent_id
            for result in self.results
        )

        if (
            len(intent_ids)
            != len(set(intent_ids))
        ):
            raise ValueError(
                "refusal intent IDs must be unique"
            )

        role_counts = Counter(
            result.intent.evaluation_role
            for result in self.results
        )

        expected_roles = Counter(
            {
                EvaluationRole.DEVELOPMENT: 4,
                EvaluationRole.TUNING: 3,
                EvaluationRole.HELD_OUT: 3,
            }
        )

        if role_counts != expected_roles:
            raise ValueError(
                "refusal role counts drifted"
            )

        pattern_counts = Counter(
            result.intent.pattern_family
            for result in self.results
        )

        if pattern_counts["status_cause"] != 5:
            raise ValueError(
                "expected five provisional "
                "status-cause refusal patterns"
            )

        if any(
            result.verdict
            != "review_required"
            for result in self.results
        ):
            raise ValueError(
                "automated corpus scan cannot "
                "issue a semantic refusal verdict"
            )

        return self


PROVISIONAL_REFUSAL_INTENTS: tuple[
    RefusalAuditIntent,
    ...,
] = (
    RefusalAuditIntent(
        intent_id=(
            "dev-api-version-after-2026-03-10"
        ),
        cluster_id=(
            "guidance:docs-api-versions"
        ),
        evaluation_role=(
            EvaluationRole.DEVELOPMENT
        ),
        pattern_family=(
            "future_version_unknown"
        ),
        refusal_claim=(
            "The frozen corpus does not establish "
            "the identity or release date of an API "
            "version after 2026-03-10."
        ),
        topic_terms=(
            "X-GitHub-Api-Version",
            "API version",
            "2026-03-10",
        ),
        diagnostic_terms=(
            "2022-11-28",
            "closing down",
            "supported",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "dev-add-assignees-silent-ignore-cause"
        ),
        cluster_id=(
            "openapi-pair:issues/add-assignees"
        ),
        evaluation_role=(
            EvaluationRole.DEVELOPMENT
        ),
        pattern_family=(
            "silent_mutation_cause"
        ),
        refusal_claim=(
            "A generic successful add-assignees "
            "outcome does not establish exactly "
            "which requested assignee was ignored "
            "or the concrete reason."
        ),
        topic_terms=(
            "issues/add-assignees",
            "add assignees",
            "assignees",
        ),
        diagnostic_terms=(
            "silently ignored",
            "silently dropped",
            "push access",
            "ignored_reason",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "dev-create-issue-silent-drop-cause"
        ),
        cluster_id=(
            "openapi-pair:issues/create"
        ),
        evaluation_role=(
            EvaluationRole.DEVELOPMENT
        ),
        pattern_family=(
            "silent_mutation_cause"
        ),
        refusal_claim=(
            "Generic success when creating an issue "
            "does not establish the exact actor or "
            "permission deficiency responsible for "
            "silently dropped optional fields."
        ),
        topic_terms=(
            "issues/create",
            "create an issue",
            "/issues",
        ),
        diagnostic_terms=(
            "silently dropped",
            "push access",
            "assignees",
            "labels",
            "milestone",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "dev-remove-reviewers-422-cause"
        ),
        cluster_id=(
            "openapi-pair:"
            "pulls/remove-requested-reviewers"
        ),
        evaluation_role=(
            EvaluationRole.DEVELOPMENT
        ),
        pattern_family=(
            "status_cause"
        ),
        refusal_claim=(
            "A 422 response from removing requested "
            "reviewers does not by itself establish "
            "the exact validation cause."
        ),
        topic_terms=(
            "pulls/remove-requested-reviewers",
            "remove requested reviewers",
            "requested_reviewers",
        ),
        diagnostic_terms=(
            "422",
            "validation failed",
            "invalid request",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "tuning-get-pull-mergeable-null"
        ),
        cluster_id=(
            "openapi-pair:pulls/get"
        ),
        evaluation_role=(
            EvaluationRole.TUNING
        ),
        pattern_family=(
            "pending_state_unknown"
        ),
        refusal_claim=(
            "mergeable=null does not establish "
            "whether the pull request is mergeable "
            "because computation may still be pending."
        ),
        topic_terms=(
            "pulls/get",
            "get a pull request",
            "mergeable",
        ),
        diagnostic_terms=(
            "background job",
            "mergeability",
            "resubmit",
            "null",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "tuning-update-pull-422-cause"
        ),
        cluster_id=(
            "openapi-pair:pulls/update"
        ),
        evaluation_role=(
            EvaluationRole.TUNING
        ),
        pattern_family=(
            "status_cause"
        ),
        refusal_claim=(
            "A 422 response from updating a pull "
            "request does not by itself establish "
            "the exact validation cause."
        ),
        topic_terms=(
            "pulls/update",
            "update a pull request",
        ),
        diagnostic_terms=(
            "422",
            "validation failed",
            "invalid request",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "tuning-create-in-org-451-cause"
        ),
        cluster_id=(
            "openapi-pair:repos/create-in-org"
        ),
        evaluation_role=(
            EvaluationRole.TUNING
        ),
        pattern_family=(
            "status_cause"
        ),
        refusal_claim=(
            "A 451 response from creating an "
            "organization repository does not by "
            "itself establish the exact cause."
        ),
        topic_terms=(
            "repos/create-in-org",
            "create an organization repository",
            "/orgs/{org}/repos",
        ),
        diagnostic_terms=(
            "451",
            "validation failed",
            "error",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "heldout-last-known-timezone"
        ),
        cluster_id=(
            "guidance:docs-timezones"
        ),
        evaluation_role=(
            EvaluationRole.HELD_OUT
        ),
        pattern_family=(
            "user_state_unknown"
        ),
        refusal_claim=(
            "Without observed user state, the "
            "authenticated user's last-known timezone "
            "cannot be inferred."
        ),
        topic_terms=(
            "Time-Zone",
            "last known timezone",
            "timezone",
        ),
        diagnostic_terms=(
            "authenticated user",
            "defaulting to UTC",
            "browse the GitHub website",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "heldout-blocked-by-failure-cause"
        ),
        cluster_id=(
            "openapi-pair:"
            "issues/add-blocked-by-dependency"
        ),
        evaluation_role=(
            EvaluationRole.HELD_OUT
        ),
        pattern_family=(
            "status_cause"
        ),
        refusal_claim=(
            "A generic error response from adding "
            "an issue dependency does not by itself "
            "establish the exact failure cause."
        ),
        topic_terms=(
            "issues/add-blocked-by-dependency",
            "blocked by",
            "issue_id",
        ),
        diagnostic_terms=(
            "422",
            "403",
            "404",
            "410",
            "validation failed",
        ),
    ),
    RefusalAuditIntent(
        intent_id=(
            "heldout-list-pulls-422-cause"
        ),
        cluster_id=(
            "openapi-pair:pulls/list"
        ),
        evaluation_role=(
            EvaluationRole.HELD_OUT
        ),
        pattern_family=(
            "status_cause"
        ),
        refusal_claim=(
            "A 422 response from listing pull "
            "requests does not by itself establish "
            "the exact validation cause."
        ),
        topic_terms=(
            "pulls/list",
            "list pull requests",
            "/pulls",
        ),
        diagnostic_terms=(
            "422",
            "validation failed",
            "sort",
            "direction",
        ),
    ),
)


class Phase4RefusalAuditError(
    ValueError
):
    """The refusal audit cannot be safely materialized."""


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _enum_string(
    value: object,
) -> str:
    if isinstance(
        value,
        Enum,
    ):
        return str(
            value.value
        )

    return str(value)


def _read_verified_dossier(
    repo_root: Path,
) -> tuple[
    Phase4AuthoringDossier,
    str,
]:
    path = (
        repo_root
        / _DOSSIER_RELATIVE_PATH
    )

    content = path.read_bytes()
    digest = _sha256_bytes(
        content
    )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    expected = (
        f"{digest}  {path.name}"
    )

    observed = (
        sidecar.read_text(
            encoding="utf-8"
        )
        .strip()
    )

    if observed != expected:
        raise Phase4RefusalAuditError(
            "authoring dossier SHA sidecar mismatch"
        )

    dossier = (
        Phase4AuthoringDossier
        .model_validate_json(
            content
        )
    )

    return dossier, digest


def _searchable_text(
    document: IndexedDocument,
) -> str:
    metadata = "\n".join(
        (
            *document.source_ids,
            *document.document_ids,
        )
    )

    return (
        f"{document.content}\n{metadata}"
    ).casefold()


def _matched_terms(
    haystack: str,
    terms: tuple[
        str,
        ...,
    ],
) -> tuple[str, ...]:
    return tuple(
        term
        for term in terms
        if term.casefold()
        in haystack
    )


def _candidate_score(
    topic_matches: tuple[
        str,
        ...,
    ],
    diagnostic_matches: tuple[
        str,
        ...,
    ],
) -> int:
    score = (
        10 * len(topic_matches)
        + 4 * len(
            diagnostic_matches
        )
    )

    if (
        topic_matches
        and diagnostic_matches
    ):
        score += 15

    return score


def _qualifies(
    topic_matches: tuple[
        str,
        ...,
    ],
    diagnostic_matches: tuple[
        str,
        ...,
    ],
) -> bool:
    if topic_matches:
        return True

    return (
        len(diagnostic_matches)
        >= 2
    )


def _preview(
    content: str,
) -> str:
    collapsed = " ".join(
        content.split()
    )

    return collapsed[
        :1200
    ]


def _discover_candidates(
    intent: RefusalAuditIntent,
    documents: tuple[
        IndexedDocument,
        ...,
    ],
    gold_evidence_ids: set[
        str
    ],
) -> RefusalAuditIntentResult:
    candidates: list[
        RefusalAuditCandidate
    ] = []

    for document in documents:
        haystack = _searchable_text(
            document
        )

        topic_matches = (
            _matched_terms(
                haystack,
                intent.topic_terms,
            )
        )

        diagnostic_matches = (
            _matched_terms(
                haystack,
                intent.diagnostic_terms,
            )
        )

        if not _qualifies(
            topic_matches,
            diagnostic_matches,
        ):
            continue

        score = _candidate_score(
            topic_matches,
            diagnostic_matches,
        )

        candidates.append(
            RefusalAuditCandidate(
                evidence_id=(
                    document.evidence_id
                ),
                source_ids=(
                    document.source_ids
                ),
                document_ids=(
                    document.document_ids
                ),
                authority_level=(
                    _enum_string(
                        document.authority_level
                    )
                ),
                source_state=(
                    _enum_string(
                        document.source_state
                    )
                ),
                api_version_or_snapshot=(
                    document
                    .api_version_or_snapshot
                ),
                matched_topic_terms=(
                    topic_matches
                ),
                matched_diagnostic_terms=(
                    diagnostic_matches
                ),
                score=score,
                phase4_gold_evidence=(
                    document.evidence_id
                    in gold_evidence_ids
                ),
                content_preview=(
                    _preview(
                        document.content
                    )
                ),
            )
        )

    ordered = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                -candidate.score,
                candidate.evidence_id,
            ),
        )
    )

    if not ordered:
        raise Phase4RefusalAuditError(
            "refusal candidate discovery "
            f"returned no evidence: "
            f"{intent.intent_id}"
        )

    cross_gold_count = sum(
        not candidate.phase4_gold_evidence
        for candidate in ordered
    )

    return RefusalAuditIntentResult(
        intent=intent,
        candidate_count=len(
            ordered
        ),
        cross_gold_candidate_count=(
            cross_gold_count
        ),
        candidate_evidence_ids=tuple(
            candidate.evidence_id
            for candidate in ordered
        ),
        detailed_candidates=(
            ordered[
                :_DETAIL_LIMIT
            ]
        ),
    )


def _render_markdown(
    results: tuple[
        RefusalAuditIntentResult,
        ...,
    ],
) -> str:
    lines = [
        "# Phase 4C Refusal Full-Corpus Audit V1",
        "",
        (
            "**Purpose:** deterministically surface "
            "runtime evidence that could invalidate "
            "the ten provisional refusal intents."
        ),
        "",
        (
            "> This artifact is candidate discovery, "
            "not a semantic verdict. A lexical match "
            "cannot prove either answerability or "
            "absence of support."
        ),
        "",
        (
            "> The scan covers the frozen 1,333-chunk "
            "runtime corpus, including background and "
            "shared component evidence."
        ),
        "",
        (
            "**Phase 3D chunk manifest SHA256:** "
            f"`{PHASE3D_CHUNK_MANIFEST_SHA256}`"
        ),
        "",
        (
            "**Phase 4 constitution SHA256:** "
            f"`{PHASE4_CONSTITUTION_SHA256}`"
        ),
        "",
    ]

    for result in results:
        intent = result.intent

        lines.extend(
            [
                (
                    "## "
                    f"`{intent.intent_id}`"
                ),
                "",
                (
                    "- cluster: "
                    f"`{intent.cluster_id}`"
                ),
                (
                    "- role: "
                    f"`{intent.evaluation_role.value}`"
                ),
                (
                    "- pattern: "
                    f"`{intent.pattern_family}`"
                ),
                (
                    "- provisional claim: "
                    f"{intent.refusal_claim}"
                ),
                (
                    "- total discovered candidates: "
                    f"{result.candidate_count}"
                ),
                (
                    "- candidates outside Phase 4 "
                    "gold evidence: "
                    f"{result.cross_gold_candidate_count}"
                ),
                "- automated verdict: `review_required`",
                "",
                "### Search terms",
                "",
                (
                    "- topic: "
                    + ", ".join(
                        f"`{term}`"
                        for term
                        in intent.topic_terms
                    )
                ),
                (
                    "- diagnostic: "
                    + ", ".join(
                        f"`{term}`"
                        for term
                        in intent.diagnostic_terms
                    )
                ),
                "",
                (
                    "### Highest-ranked candidates "
                    f"(max {_DETAIL_LIMIT})"
                ),
                "",
            ]
        )

        for candidate in (
            result.detailed_candidates
        ):
            lines.extend(
                [
                    (
                        "#### "
                        f"`{candidate.evidence_id}`"
                    ),
                    "",
                    (
                        "- score: "
                        f"`{candidate.score}`"
                    ),
                    (
                        "- Phase 4 gold evidence: "
                        f"`{str(candidate.phase4_gold_evidence).lower()}`"
                    ),
                    (
                        "- source state: "
                        f"`{candidate.source_state}`"
                    ),
                    (
                        "- authority: "
                        f"`{candidate.authority_level}`"
                    ),
                    (
                        "- API version/snapshot: "
                        f"`{candidate.api_version_or_snapshot}`"
                    ),
                    (
                        "- source IDs: "
                        + ", ".join(
                            f"`{source_id}`"
                            for source_id
                            in candidate.source_ids
                        )
                    ),
                    (
                        "- topic matches: "
                        + (
                            ", ".join(
                                f"`{term}`"
                                for term
                                in candidate.matched_topic_terms
                            )
                            or "`none`"
                        )
                    ),
                    (
                        "- diagnostic matches: "
                        + (
                            ", ".join(
                                f"`{term}`"
                                for term
                                in candidate.matched_diagnostic_terms
                            )
                            or "`none`"
                        )
                    ),
                    "",
                    "<pre>",
                    html.escape(
                        candidate.content_preview,
                        quote=False,
                    ),
                    "</pre>",
                    "",
                ]
            )

    return (
        "\n".join(lines)
        .rstrip()
        + "\n"
    )


def _write_bytes_with_sha256(
    path: Path,
    content: bytes,
) -> str:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(
        content
    )

    digest = _sha256_bytes(
        content
    )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    sidecar.write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    return digest


def materialize_phase4_refusal_audit(
    repo_root: Path,
) -> tuple[
    Phase4RefusalFullCorpusAudit,
    str,
    str,
]:
    dossier, dossier_sha256 = (
        _read_verified_dossier(
            repo_root
        )
    )

    documents = (
        load_phase3d_indexed_documents(
            repo_root
        )
    )

    if (
        len(documents)
        != PHASE3D_CHUNK_COUNT
    ):
        raise Phase4RefusalAuditError(
            "runtime corpus count mismatch"
        )

    cluster_role_by_id = {
        cluster.cluster_id:
        cluster.evaluation_role
        for cluster
        in dossier.clusters
    }

    gold_evidence_ids = {
        evidence_id
        for cluster
        in dossier.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    for intent in (
        PROVISIONAL_REFUSAL_INTENTS
    ):
        observed_role = (
            cluster_role_by_id.get(
                intent.cluster_id
            )
        )

        if (
            observed_role
            is not intent.evaluation_role
        ):
            raise Phase4RefusalAuditError(
                "refusal intent role does "
                "not match frozen cluster: "
                f"{intent.intent_id}"
            )

    results = tuple(
        _discover_candidates(
            intent,
            documents,
            gold_evidence_ids,
        )
        for intent
        in PROVISIONAL_REFUSAL_INTENTS
    )

    markdown = _render_markdown(
        results
    )

    markdown_path = (
        repo_root
        / _AUDIT_MARKDOWN_RELATIVE_PATH
    )

    markdown_sha256 = (
        _write_bytes_with_sha256(
            markdown_path,
            markdown.encode(
                "utf-8"
            ),
        )
    )

    audit = (
        Phase4RefusalFullCorpusAudit(
            authoring_dossier_sha256=(
                dossier_sha256
            ),
            review_markdown_sha256=(
                markdown_sha256
            ),
            results=results,
        )
    )

    audit_path = (
        repo_root
        / _AUDIT_JSON_RELATIVE_PATH
    )

    audit_sha256 = (
        write_json_with_sha256(
            audit_path,
            audit,
        )
    )

    return (
        audit,
        audit_sha256,
        markdown_sha256,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    (
        audit,
        audit_sha256,
        markdown_sha256,
    ) = materialize_phase4_refusal_audit(
        repo_root
    )

    pattern_counts = Counter(
        result.intent.pattern_family
        for result
        in audit.results
    )

    total_candidates = sum(
        result.candidate_count
        for result
        in audit.results
    )

    cross_gold_candidates = sum(
        result.cross_gold_candidate_count
        for result
        in audit.results
    )

    print(
        "PHASE4C_REFUSAL_RUNTIME_CORPUS_COUNT="
        f"{audit.runtime_corpus_count}"
    )

    print(
        "PHASE4C_REFUSAL_INTENT_COUNT="
        f"{audit.refusal_intent_count}"
    )

    print(
        "PHASE4C_REFUSAL_TOTAL_CANDIDATE_MATCHES="
        f"{total_candidates}"
    )

    print(
        "PHASE4C_REFUSAL_CROSS_GOLD_CANDIDATE_MATCHES="
        f"{cross_gold_candidates}"
    )

    print(
        "PHASE4C_REFUSAL_STATUS_CAUSE_PATTERN_COUNT="
        f"{pattern_counts['status_cause']}"
    )

    print(
        "PHASE4C_REFUSAL_FINAL_VERDICT_COUNT=0"
    )

    print(
        "PHASE4C_REFUSAL_REVIEW_REQUIRED_COUNT=10"
    )

    print(
        "PHASE4C_REFUSAL_AUDIT_JSON_SHA256="
        f"{audit_sha256}"
    )

    print(
        "PHASE4C_REFUSAL_AUDIT_MARKDOWN_SHA256="
        f"{markdown_sha256}"
    )

    print(
        "PHASE4C_REFUSAL_AUDIT_READY=true"
    )

    print(
        "PHASE4C_ALLOCATION_FROZEN=false"
    )

    print(
        "PHASE4_BASELINE_AUTHORIZED=false"
    )


if __name__ == "__main__":
    main()
