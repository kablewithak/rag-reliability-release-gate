import hashlib
from collections import Counter
from pathlib import Path

from rag_reliability.contracts.enums import (
    EvaluationRole,
)
from rag_reliability.evaluation.authoring_dossier import (
    Phase4AuthoringDossier,
)
from rag_reliability.evaluation.full_corpus import (
    PHASE3D_CHUNK_COUNT,
    load_phase3d_indexed_documents,
)
from rag_reliability.evaluation.refusal_corpus_audit import (
    Phase4RefusalFullCorpusAudit,
)

ROOT = Path(__file__).resolve().parents[2]

AUDIT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_refusal_full_corpus_audit_v1.json"
)

MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_refusal_full_corpus_audit_v1.md"
)

DOSSIER_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_authoring_dossier_v1.json"
)


def _audit(
) -> Phase4RefusalFullCorpusAudit:
    return (
        Phase4RefusalFullCorpusAudit
        .model_validate_json(
            AUDIT_PATH.read_text(
                encoding="utf-8"
            )
        )
    )


def _dossier(
) -> Phase4AuthoringDossier:
    return (
        Phase4AuthoringDossier
        .model_validate_json(
            DOSSIER_PATH.read_text(
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


def test_audit_scans_exact_frozen_runtime_corpus(
) -> None:
    audit = _audit()

    documents = (
        load_phase3d_indexed_documents(
            ROOT
        )
    )

    assert len(
        documents
    ) == PHASE3D_CHUNK_COUNT

    assert (
        audit.runtime_corpus_count
        == PHASE3D_CHUNK_COUNT
    )

    runtime_ids = {
        document.evidence_id
        for document
        in documents
    }

    for result in audit.results:
        assert set(
            result.candidate_evidence_ids
        ) <= runtime_ids


def test_audit_preserves_ten_provisional_refusal_roles(
) -> None:
    audit = _audit()

    assert len(
        audit.results
    ) == 10

    role_counts = Counter(
        result.intent.evaluation_role
        for result
        in audit.results
    )

    assert role_counts == Counter(
        {
            EvaluationRole.DEVELOPMENT: 4,
            EvaluationRole.TUNING: 3,
            EvaluationRole.HELD_OUT: 3,
        }
    )

    assert (
        audit.final_verdict_count
        == 0
    )

    assert all(
        result.verdict
        == "review_required"
        for result
        in audit.results
    )

    assert (
        audit.baseline_authorized
        is False
    )


def test_audit_candidate_details_are_consistent(
) -> None:
    audit = _audit()

    for result in audit.results:
        assert (
            result.candidate_count
            == len(
                result.candidate_evidence_ids
            )
        )

        scores = [
            candidate.score
            for candidate
            in result.detailed_candidates
        ]

        assert scores == sorted(
            scores,
            reverse=True,
        )

        assert all(
            candidate.matched_topic_terms
            or candidate.matched_diagnostic_terms
            for candidate
            in result.detailed_candidates
        )


def test_audit_reaches_beyond_phase4_gold(
) -> None:
    audit = _audit()
    dossier = _dossier()

    gold_ids = {
        evidence_id
        for cluster
        in dossier.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    discovered_ids = {
        evidence_id
        for result
        in audit.results
        for evidence_id
        in result.candidate_evidence_ids
    }

    assert (
        discovered_ids
        - gold_ids
    )

    assert sum(
        result.cross_gold_candidate_count
        for result
        in audit.results
    ) > 0


def test_audit_markdown_is_hash_bound(
) -> None:
    audit = _audit()

    content = MARKDOWN_PATH.read_bytes()

    digest = _sha256_bytes(
        content
    )

    assert (
        digest
        == audit.review_markdown_sha256
    )

    sidecar = MARKDOWN_PATH.with_suffix(
        ".md.sha256"
    )

    assert (
        sidecar.read_text(
            encoding="utf-8"
        ).strip()
        == (
            f"{digest}  "
            f"{MARKDOWN_PATH.name}"
        )
    )
