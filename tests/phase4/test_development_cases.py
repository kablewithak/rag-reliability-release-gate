import hashlib
from collections import Counter
from pathlib import Path

from rag_reliability.contracts.enums import (
    EvaluationRole,
    ResponseMode,
    ScenarioClass,
)
from rag_reliability.evaluation.development_cases import (
    Phase4DevelopmentCaseSuite,
)

ROOT = Path(__file__).resolve().parents[2]

SUITE_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_development_cases_v1.json"
)

MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_development_cases_v1.md"
)


def _suite(
) -> Phase4DevelopmentCaseSuite:
    return (
        Phase4DevelopmentCaseSuite
        .model_validate_json(
            SUITE_PATH.read_text(
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


def test_development_suite_has_exact_case_and_cluster_counts(
) -> None:
    suite = _suite()

    assert len(
        suite.records
    ) == 24

    cluster_counts = Counter(
        record.cluster_id
        for record
        in suite.records
    )

    assert len(
        cluster_counts
    ) == 12

    assert set(
        cluster_counts.values()
    ) == {2}


def test_development_suite_preserves_reviewed_scenario_quota(
) -> None:
    suite = _suite()

    counts = Counter(
        record.case.scenario_class
        for record
        in suite.records
    )

    assert counts == Counter(
        {
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 7,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 5,
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 5,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 3,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 4,
        }
    )


def test_development_suite_is_development_only_and_not_frozen(
) -> None:
    suite = _suite()

    assert all(
        record.case.data_role
        is EvaluationRole.DEVELOPMENT
        for record
        in suite.records
    )

    assert (
        suite.development_case_authoring_complete
        is True
    )

    assert (
        suite.development_suite_frozen
        is False
    )

    assert (
        suite.baseline_authorized
        is False
    )

    assert (
        suite.release_eligible
        is False
    )


def test_multi_evidence_cases_require_multiple_exact_evidence_units(
) -> None:
    suite = _suite()

    multi_cases = [
        record.case
        for record
        in suite.records
        if (
            record.case.scenario_class
            is ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        )
    ]

    assert len(
        multi_cases
    ) == 5

    assert all(
        len(
            case.required_evidence_ids
        )
        >= 2
        for case in multi_cases
    )


def test_freshness_cases_forbid_historical_evidence_when_available(
) -> None:
    suite = _suite()

    by_id = {
        record.case.case_id:
        record.case
        for record
        in suite.records
    }

    for case_id in (
        "phase4-dev-issues-create-current-assignees",
        "phase4-dev-repos-accept-invitation-current",
        "phase4-dev-repos-get-content-current-submodule",
    ):
        case = by_id[
            case_id
        ]

        assert (
            case.scenario_class
            is ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        )

        assert (
            case.forbidden_evidence_ids
        )

        assert (
            case.forbidden_source_ids
        )


def test_refusal_cases_use_insufficient_evidence_and_no_gold_answer(
) -> None:
    suite = _suite()

    refusal_cases = [
        record.case
        for record
        in suite.records
        if (
            record.case.expected_response_mode
            is ResponseMode.REFUSE
        )
    ]

    assert len(
        refusal_cases
    ) == 4

    assert all(
        case.must_refuse_reason
        == "insufficient_evidence"
        for case
        in refusal_cases
    )

    assert all(
        not case.required_fact_ids
        and not case.required_evidence_ids
        and not case.required_source_ids
        and not case.gold_fact_rubric
        for case
        in refusal_cases
    )


def test_runtime_projection_contains_only_case_id_and_query(
) -> None:
    suite = _suite()

    for record in (
        suite.records
    ):
        runtime = (
            record.case
            .to_runtime_input()
            .model_dump()
        )

        assert set(
            runtime
        ) == {
            "case_id",
            "query",
        }


def test_development_review_markdown_is_hash_bound(
) -> None:
    suite = _suite()

    content = (
        MARKDOWN_PATH
        .read_bytes()
    )

    digest = _sha256_bytes(
        content
    )

    assert (
        digest
        == suite.review_markdown_sha256
    )

    sidecar = (
        MARKDOWN_PATH
        .with_suffix(
            ".md.sha256"
        )
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
