import hashlib
from pathlib import Path

from rag_reliability.evaluation.refusal_corpus_review import (
    AUDIT_MARKDOWN_SHA256,
    Phase4RefusalSemanticReview,
)

ROOT = Path(__file__).resolve().parents[2]

REVIEW_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_refusal_full_corpus_review_v1.json"
)

REVIEW_MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_refusal_full_corpus_review_v1.md"
)


def _review() -> Phase4RefusalSemanticReview:
    return (
        Phase4RefusalSemanticReview
        .model_validate_json(
            REVIEW_PATH.read_text(
                encoding="utf-8"
            )
        )
    )


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def test_refusal_semantic_review_preserves_verdict_counts(
) -> None:
    review = _review()

    assert review.reviewed_intent_count == 10
    assert review.supported_refusal_count == 7
    assert review.answerable_elsewhere_count == 0
    assert review.ambiguous_needs_rewording_count == 3

    assert review.allocation_survives is True
    assert review.allocation_frozen is False
    assert review.canonical_case_authoring_started is False
    assert review.baseline_authorized is False


def test_refusal_semantic_review_has_exact_three_rewrites(
) -> None:
    review = _review()

    rewritten = {
        item.intent_id
        for item in review.items
        if item.rewrite_required
    }

    assert rewritten == {
        "dev-add-assignees-silent-ignore-cause",
        "dev-create-issue-silent-drop-cause",
        "heldout-blocked-by-failure-cause",
    }


def test_refusal_semantic_review_has_no_answerable_elsewhere_case(
) -> None:
    review = _review()

    assert not {
        item.intent_id
        for item in review.items
        if item.verdict == "ANSWERABLE_ELSEWHERE"
    }


def test_refusal_semantic_review_binds_reviewed_audit_bytes(
) -> None:
    review = _review()

    assert (
        review.audit_markdown_sha256
        == AUDIT_MARKDOWN_SHA256
    )


def test_refusal_semantic_review_markdown_is_hash_bound(
) -> None:
    review = _review()

    content = REVIEW_MARKDOWN_PATH.read_bytes()
    digest = _sha256_bytes(content)

    assert digest == review.review_markdown_sha256

    sidecar = REVIEW_MARKDOWN_PATH.with_suffix(
        ".md.sha256"
    )

    assert (
        sidecar.read_text(
            encoding="utf-8"
        ).strip()
        == (
            f"{digest}  "
            f"{REVIEW_MARKDOWN_PATH.name}"
        )
    )


def test_rewritten_refusals_target_unknown_instance_facts(
) -> None:
    review = _review()

    claims = {
        item.intent_id: item.final_claim
        for item in review.items
    }

    assert (
        "which requested login"
        in claims[
            "dev-add-assignees-silent-ignore-cause"
        ]
    )

    assert (
        "which optional requested fields"
        in claims[
            "dev-create-issue-silent-drop-cause"
        ]
    )

    assert (
        "A 404 response"
        in claims[
            "heldout-blocked-by-failure-cause"
        ]
    )
