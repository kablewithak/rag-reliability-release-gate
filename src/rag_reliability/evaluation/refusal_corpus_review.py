"""Semantic review of the Phase 4C full-corpus refusal audit."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import EvaluationRole
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.refusal_corpus_audit import (
    Phase4RefusalFullCorpusAudit,
)

ReviewVerdict = Literal[
    "SUPPORTED_REFUSAL",
    "ANSWERABLE_ELSEWHERE",
    "AMBIGUOUS_NEEDS_REWORDING",
]

AUDIT_MARKDOWN_SHA256 = (
    "0429b8842a29e62312b59b85c353a8071acc2f8fbde094da3b543cd8ba591693"
)

_AUDIT_JSON_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_refusal_full_corpus_audit_v1.json"
)

_AUDIT_MARKDOWN_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_refusal_full_corpus_audit_v1.md"
)

_REVIEW_JSON_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_refusal_full_corpus_review_v1.json"
)

_REVIEW_MARKDOWN_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_refusal_full_corpus_review_v1.md"
)


class RefusalReviewDecision(ContractModel):
    intent_id: NonEmptyStr
    verdict: ReviewVerdict
    final_claim: NonEmptyStr
    rationale: NonEmptyStr


class RefusalSemanticReviewItem(ContractModel):
    intent_id: NonEmptyStr
    cluster_id: NonEmptyStr
    evaluation_role: EvaluationRole
    original_claim: NonEmptyStr
    final_claim: NonEmptyStr
    verdict: ReviewVerdict
    rationale: NonEmptyStr
    candidate_count: int = Field(ge=1)
    cross_gold_candidate_count: int = Field(ge=0)
    rewrite_required: bool

    @model_validator(mode="after")
    def validate_rewrite_state(self) -> Self:
        if (
            self.verdict
            == "AMBIGUOUS_NEEDS_REWORDING"
            and not self.rewrite_required
        ):
            raise ValueError(
                "ambiguous review must require rewrite"
            )

        if (
            self.verdict == "SUPPORTED_REFUSAL"
            and self.rewrite_required
        ):
            raise ValueError(
                "supported refusal must not require rewrite"
            )

        if (
            self.rewrite_required
            and self.final_claim == self.original_claim
        ):
            raise ValueError(
                "rewrite must change the claim"
            )

        return self


class Phase4RefusalSemanticReview(ContractModel):
    review_version: Literal[
        "phase4c-refusal-full-corpus-review-v1"
    ] = "phase4c-refusal-full-corpus-review-v1"

    audit_markdown_sha256: Literal[
        "0429b8842a29e62312b59b85c353a8071acc2f8fbde094da3b543cd8ba591693"
    ] = (
        "0429b8842a29e62312b59b85c353a8071acc2f8fbde094da3b543cd8ba591693"
    )

    audit_json_sha256: Sha256
    review_markdown_sha256: Sha256

    reviewed_intent_count: Literal[10] = 10
    supported_refusal_count: Literal[7] = 7
    answerable_elsewhere_count: Literal[0] = 0
    ambiguous_needs_rewording_count: Literal[3] = 3

    allocation_survives: Literal[True] = True
    allocation_frozen: Literal[False] = False
    canonical_case_authoring_started: Literal[False] = False
    baseline_authorized: Literal[False] = False

    items: tuple[
        RefusalSemanticReviewItem,
        ...,
    ] = Field(
        min_length=10,
        max_length=10,
    )

    @model_validator(mode="after")
    def validate_review(self) -> Self:
        verdict_counts = Counter(
            item.verdict
            for item in self.items
        )

        expected = Counter(
            {
                "SUPPORTED_REFUSAL": 7,
                "ANSWERABLE_ELSEWHERE": 0,
                "AMBIGUOUS_NEEDS_REWORDING": 3,
            }
        )

        if verdict_counts != expected:
            raise ValueError(
                "semantic review verdict counts drifted"
            )

        intent_ids = tuple(
            item.intent_id
            for item in self.items
        )

        if len(intent_ids) != len(set(intent_ids)):
            raise ValueError(
                "semantic review intent IDs are not unique"
            )

        return self


DECISIONS: tuple[
    RefusalReviewDecision,
    ...,
] = (
    RefusalReviewDecision(
        intent_id="dev-api-version-after-2026-03-10",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "The frozen corpus does not establish the identity or "
            "release date of an API version after 2026-03-10."
        ),
        rationale=(
            "The surfaced evidence establishes current and historical "
            "version material but does not establish a later version "
            "identity or release date."
        ),
    ),
    RefusalReviewDecision(
        intent_id="dev-add-assignees-silent-ignore-cause",
        verdict="AMBIGUOUS_NEEDS_REWORDING",
        final_claim=(
            "Given only a successful add-assignees outcome and no "
            "request or response detail, the frozen evidence cannot "
            "establish which requested login, if any, was ignored."
        ),
        rationale=(
            "The operation itself documents the push-access condition, "
            "so the refusal must target the unknown instance-specific "
            "login rather than treat the documented condition as unknown."
        ),
    ),
    RefusalReviewDecision(
        intent_id="dev-create-issue-silent-drop-cause",
        verdict="AMBIGUOUS_NEEDS_REWORDING",
        final_claim=(
            "Given only a successful create-issue outcome and no "
            "response details or caller identity, the frozen evidence "
            "cannot establish which optional requested fields were "
            "silently dropped or identify the caller."
        ),
        rationale=(
            "The operation documents that lack of push access can "
            "silently drop optional assignments, labels, or milestone "
            "changes, so permission deficiency must not be treated as "
            "universally unknown."
        ),
    ),
    RefusalReviewDecision(
        intent_id="dev-remove-reviewers-422-cause",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "A 422 response from removing requested reviewers does not "
            "by itself establish the exact validation cause."
        ),
        rationale=(
            "The operation and shared validation contract establish "
            "validation failure but do not identify the concrete cause "
            "from status alone."
        ),
    ),
    RefusalReviewDecision(
        intent_id="tuning-get-pull-mergeable-null",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "mergeable=null does not establish whether the pull request "
            "is mergeable because computation may still be pending."
        ),
        rationale=(
            "The operation explicitly states that null can mean the "
            "background mergeability computation has not completed."
        ),
    ),
    RefusalReviewDecision(
        intent_id="tuning-update-pull-422-cause",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "A 422 response from updating a pull request does not by "
            "itself establish the exact validation cause."
        ),
        rationale=(
            "The status and generic validation schema do not identify "
            "the exact failed field or condition without response detail."
        ),
    ),
    RefusalReviewDecision(
        intent_id="tuning-create-in-org-451-cause",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "A 451 response from creating an organization repository "
            "does not by itself establish the exact triggering cause."
        ),
        rationale=(
            "The current operation exposes the response but the surfaced "
            "frozen evidence does not establish its exact triggering "
            "condition."
        ),
    ),
    RefusalReviewDecision(
        intent_id="heldout-last-known-timezone",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "Without observed user state, the authenticated user's "
            "last-known timezone cannot be inferred."
        ),
        rationale=(
            "The documentation defines timezone precedence, but the "
            "actual last-known timezone is user state rather than a "
            "fact contained in the corpus."
        ),
    ),
    RefusalReviewDecision(
        intent_id="heldout-blocked-by-failure-cause",
        verdict="AMBIGUOUS_NEEDS_REWORDING",
        final_claim=(
            "A 404 response from adding a blocked-by dependency does "
            "not by itself identify which relevant resource or access "
            "condition caused the request to fail."
        ),
        rationale=(
            "The original generic-error wording was too weak to be "
            "diagnostic. A specific 404 preserves the insufficiency "
            "test without pretending the exact cause is known."
        ),
    ),
    RefusalReviewDecision(
        intent_id="heldout-list-pulls-422-cause",
        verdict="SUPPORTED_REFUSAL",
        final_claim=(
            "A 422 response from listing pull requests does not by "
            "itself establish the exact validation cause."
        ),
        rationale=(
            "The operation exposes several query dimensions and a "
            "generic validation failure; status alone does not identify "
            "the exact failed condition."
        ),
    ),
)


class Phase4RefusalSemanticReviewError(ValueError):
    """The semantic refusal review cannot be safely materialized."""


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_verified(
    path: Path,
) -> tuple[bytes, str]:
    content = path.read_bytes()
    digest = _sha256_bytes(content)

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    observed = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    expected = f"{digest}  {path.name}"

    if observed != expected:
        raise Phase4RefusalSemanticReviewError(
            f"SHA sidecar mismatch: {path}"
        )

    return content, digest


def _write_markdown(
    path: Path,
    content: str,
) -> str:
    encoded = content.encode("utf-8")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(encoded)

    digest = _sha256_bytes(encoded)

    path.with_suffix(
        path.suffix + ".sha256"
    ).write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    return digest


def _render_markdown(
    items: tuple[
        RefusalSemanticReviewItem,
        ...,
    ],
) -> str:
    lines = [
        "# Phase 4C Refusal Full-Corpus Semantic Review V1",
        "",
        f"Audit Markdown SHA256: `{AUDIT_MARKDOWN_SHA256}`",
        "",
        "## Verdict summary",
        "",
        "- `SUPPORTED_REFUSAL=7`",
        "- `ANSWERABLE_ELSEWHERE=0`",
        "- `AMBIGUOUS_NEEDS_REWORDING=3`",
        "- `ALLOCATION_SURVIVES=true`",
        "- `ALLOCATION_FROZEN=false`",
        "",
    ]

    for item in items:
        lines.extend(
            [
                f"## `{item.intent_id}`",
                "",
                f"- verdict: `{item.verdict}`",
                f"- cluster: `{item.cluster_id}`",
                f"- role: `{item.evaluation_role.value}`",
                (
                    "- candidate count: "
                    f"`{item.candidate_count}`"
                ),
                (
                    "- cross-gold candidate count: "
                    f"`{item.cross_gold_candidate_count}`"
                ),
                (
                    "- rewrite required: "
                    f"`{str(item.rewrite_required).lower()}`"
                ),
                "",
                "**Final claim**",
                "",
                item.final_claim,
                "",
                "**Rationale**",
                "",
                item.rationale,
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def materialize_phase4_refusal_semantic_review(
    repo_root: Path,
) -> tuple[
    Phase4RefusalSemanticReview,
    str,
    str,
]:
    audit_markdown_path = (
        repo_root
        / _AUDIT_MARKDOWN_PATH
    )

    _, audit_markdown_sha = _read_verified(
        audit_markdown_path
    )

    if audit_markdown_sha != AUDIT_MARKDOWN_SHA256:
        raise Phase4RefusalSemanticReviewError(
            "reviewed audit Markdown SHA mismatch"
        )

    audit_json_path = (
        repo_root
        / _AUDIT_JSON_PATH
    )

    audit_json_bytes, audit_json_sha = (
        _read_verified(
            audit_json_path
        )
    )

    audit = (
        Phase4RefusalFullCorpusAudit
        .model_validate_json(
            audit_json_bytes
        )
    )

    audit_results = {
        result.intent.intent_id: result
        for result in audit.results
    }

    decisions = {
        decision.intent_id: decision
        for decision in DECISIONS
    }

    if set(audit_results) != set(decisions):
        raise Phase4RefusalSemanticReviewError(
            "semantic decisions do not cover exact audit intents"
        )

    items = tuple(
        RefusalSemanticReviewItem(
            intent_id=result.intent.intent_id,
            cluster_id=result.intent.cluster_id,
            evaluation_role=(
                result.intent.evaluation_role
            ),
            original_claim=(
                result.intent.refusal_claim
            ),
            final_claim=(
                decisions[
                    result.intent.intent_id
                ].final_claim
            ),
            verdict=(
                decisions[
                    result.intent.intent_id
                ].verdict
            ),
            rationale=(
                decisions[
                    result.intent.intent_id
                ].rationale
            ),
            candidate_count=(
                result.candidate_count
            ),
            cross_gold_candidate_count=(
                result.cross_gold_candidate_count
            ),
            rewrite_required=(
                decisions[
                    result.intent.intent_id
                ].verdict
                == "AMBIGUOUS_NEEDS_REWORDING"
            ),
        )
        for result in audit.results
    )

    markdown = _render_markdown(items)

    markdown_sha = _write_markdown(
        repo_root
        / _REVIEW_MARKDOWN_PATH,
        markdown,
    )

    review = Phase4RefusalSemanticReview(
        audit_json_sha256=audit_json_sha,
        review_markdown_sha256=markdown_sha,
        items=items,
    )

    json_sha = write_json_with_sha256(
        repo_root
        / _REVIEW_JSON_PATH,
        review,
    )

    return review, json_sha, markdown_sha


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    review, json_sha, markdown_sha = (
        materialize_phase4_refusal_semantic_review(
            repo_root
        )
    )

    print(
        "PHASE4C_REFUSAL_SUPPORTED_COUNT="
        f"{review.supported_refusal_count}"
    )
    print(
        "PHASE4C_REFUSAL_ANSWERABLE_ELSEWHERE_COUNT="
        f"{review.answerable_elsewhere_count}"
    )
    print(
        "PHASE4C_REFUSAL_REWRITE_COUNT="
        f"{review.ambiguous_needs_rewording_count}"
    )
    print(
        "PHASE4C_REFUSAL_ALLOCATION_SURVIVES=true"
    )
    print(
        "PHASE4C_REFUSAL_ALLOCATION_FROZEN=false"
    )
    print(
        "PHASE4C_CASE_AUTHORING_STARTED=false"
    )
    print(
        "PHASE4_BASELINE_AUTHORIZED=false"
    )
    print(
        "PHASE4C_REFUSAL_REVIEW_JSON_SHA256="
        f"{json_sha}"
    )
    print(
        "PHASE4C_REFUSAL_REVIEW_MARKDOWN_SHA256="
        f"{markdown_sha}"
    )


if __name__ == "__main__":
    main()
