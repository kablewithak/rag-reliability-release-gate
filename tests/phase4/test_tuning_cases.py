import hashlib
from collections import Counter
from pathlib import Path

from rag_reliability.contracts.enums import (
    EvaluationRole,
    EvaluationSourceFamily,
    ResponseMode,
    ScenarioClass,
)
from rag_reliability.evaluation.tuning_cases import (
    Phase4TuningCaseSuite,
)

ROOT = Path(__file__).resolve().parents[2]

SUITE_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_cases_v1.json"
)

MARKDOWN_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4c_tuning_cases_v1.md"
)


def _suite() -> Phase4TuningCaseSuite:
    return (
        Phase4TuningCaseSuite
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


def test_tuning_suite_has_exact_case_and_cluster_counts(
) -> None:
    suite = _suite()

    assert len(
        suite.records
    ) == 18

    cluster_counts = Counter(
        record.cluster_id
        for record
        in suite.records
    )

    assert len(
        cluster_counts
    ) == 9

    assert set(
        cluster_counts.values()
    ) == {2}


def test_tuning_suite_preserves_frozen_scenario_quota(
) -> None:
    suite = _suite()

    counts = Counter(
        record.case.scenario_class
        for record
        in suite.records
    )

    assert counts == Counter(
        {
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 6,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 3,
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 3,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 3,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 3,
        }
    )


def test_tuning_suite_preserves_frozen_family_allocation(
) -> None:
    suite = _suite()

    counts = Counter(
        record.case.source_family
        for record
        in suite.records
    )

    assert counts == Counter(
        {
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 6,
            EvaluationSourceFamily.ACTIONS: 4,
            EvaluationSourceFamily.ISSUES: 2,
            EvaluationSourceFamily.PULL_REQUESTS: 4,
            EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 2,
        }
    )


def test_tuning_suite_uses_exact_frozen_clusters(
) -> None:
    suite = _suite()

    cluster_counts = Counter(
        record.cluster_id
        for record
        in suite.records
    )

    assert cluster_counts == Counter(
        {
            "guidance:docs-authentication": 2,
            "guidance:docs-credential-security": 2,
            "guidance:docs-rate-limits": 2,
            "openapi-pair:actions/create-registration-token-for-repo": 2,
            "openapi-pair:actions/create-workflow-dispatch": 2,
            "openapi-pair:issues/add-sub-issue": 2,
            "openapi-pair:pulls/get": 2,
            "openapi-pair:pulls/update": 2,
            "openapi-pair:repos/create-in-org": 2,
        }
    )


def test_tuning_suite_is_tuning_only_and_not_frozen(
) -> None:
    suite = _suite()

    assert all(
        record.case.data_role
        is EvaluationRole.TUNING
        for record
        in suite.records
    )

    assert (
        suite.tuning_case_authoring_complete
        is True
    )

    assert (
        suite.tuning_suite_frozen
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
    ) == 3

    assert all(
        len(
            case.required_evidence_ids
        )
        >= 2
        for case
        in multi_cases
    )


def test_openapi_freshness_cases_forbid_historical_evidence(
) -> None:
    suite = _suite()

    by_id = {
        record.case.case_id:
        record.case
        for record
        in suite.records
    }

    for case_id in (
        "phase4-tuning-workflow-dispatch-current-contract",
        "phase4-tuning-create-in-org-current-451",
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


def test_tuning_refusals_use_exact_semantically_reviewed_clusters(
) -> None:
    suite = _suite()

    refusal_records = [
        record
        for record
        in suite.records
        if (
            record.case.expected_response_mode
            is ResponseMode.REFUSE
        )
    ]

    assert len(
        refusal_records
    ) == 3

    assert {
        record.cluster_id
        for record
        in refusal_records
    } == {
        "openapi-pair:pulls/get",
        "openapi-pair:pulls/update",
        "openapi-pair:repos/create-in-org",
    }

    assert all(
        record.case.must_refuse_reason
        == "insufficient_evidence"
        for record
        in refusal_records
    )

    assert all(
        not record.case.required_fact_ids
        and not record.case.required_evidence_ids
        and not record.case.required_source_ids
        and not record.case.gold_fact_rubric
        for record
        in refusal_records
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


def test_tuning_review_markdown_is_hash_bound(
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
