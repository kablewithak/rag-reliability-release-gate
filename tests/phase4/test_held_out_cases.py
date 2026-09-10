from collections import Counter

from rag_reliability.contracts.enums import (
    EvaluationRole,
    EvaluationSourceFamily,
    ScenarioClass,
)
from rag_reliability.evaluation.held_out_cases import (
    CASE_SPECS,
    EXPECTED_SCENARIOS_BY_CLUSTER,
)

EXPECTED_CLUSTER_IDS = {
    "guidance:docs-best-practices",
    "guidance:docs-getting-started",
    "guidance:docs-timezones",
    "openapi-pair:actions/create-remove-token-for-org",
    "openapi-pair:issues/add-blocked-by-dependency",
    "openapi-pair:issues/update",
    "openapi-pair:pulls/list",
    "openapi-pair:repos/create-for-authenticated-user",
    "openapi-pair:repos/list-attestations",
}


def test_held_out_case_constitution() -> None:
    assert len(CASE_SPECS) == 18

    cluster_counts = Counter(
        spec.cluster_id
        for spec in CASE_SPECS
    )

    assert set(cluster_counts) == EXPECTED_CLUSTER_IDS
    assert set(cluster_counts.values()) == {2}

    scenarios = Counter(
        spec.scenario_class
        for spec in CASE_SPECS
    )

    assert scenarios == Counter(
        {
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 5,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 4,
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 4,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 2,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 3,
        }
    )


def test_held_out_cluster_scenario_topology() -> None:
    expected = {
        "guidance:docs-best-practices": Counter(
            {
                ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 1,
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 1,
            }
        ),
        "guidance:docs-getting-started": Counter(
            {
                ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 2,
            }
        ),
        "guidance:docs-timezones": Counter(
            {
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 1,
                ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 1,
            }
        ),
        "openapi-pair:actions/create-remove-token-for-org": Counter(
            {
                ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 1,
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 1,
            }
        ),
        "openapi-pair:issues/add-blocked-by-dependency": Counter(
            {
                ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 1,
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 1,
            }
        ),
        "openapi-pair:issues/update": Counter(
            {
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 1,
                ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 1,
            }
        ),
        "openapi-pair:pulls/list": Counter(
            {
                ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 1,
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 1,
            }
        ),
        "openapi-pair:repos/create-for-authenticated-user": Counter(
            {
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 1,
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 1,
            }
        ),
        "openapi-pair:repos/list-attestations": Counter(
            {
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 1,
                ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 1,
            }
        ),
    }

    assert EXPECTED_SCENARIOS_BY_CLUSTER == expected


def test_held_out_role_is_not_runtime_tuning() -> None:
    assert EvaluationRole.HELD_OUT is not EvaluationRole.TUNING


def test_held_out_family_allocation() -> None:
    family_by_cluster = {
        "guidance:docs-best-practices": (
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
        ),
        "guidance:docs-getting-started": (
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
        ),
        "guidance:docs-timezones": (
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
        ),
        "openapi-pair:actions/create-remove-token-for-org": (
            EvaluationSourceFamily.ACTIONS
        ),
        "openapi-pair:issues/add-blocked-by-dependency": (
            EvaluationSourceFamily.ISSUES
        ),
        "openapi-pair:issues/update": (
            EvaluationSourceFamily.ISSUES
        ),
        "openapi-pair:pulls/list": (
            EvaluationSourceFamily.PULL_REQUESTS
        ),
        "openapi-pair:repos/create-for-authenticated-user": (
            EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS
        ),
        "openapi-pair:repos/list-attestations": (
            EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS
        ),
    }

    family_counts = Counter(
        family_by_cluster[
            spec.cluster_id
        ]
        for spec in CASE_SPECS
    )

    assert family_counts == Counter(
        {
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 6,
            EvaluationSourceFamily.ACTIONS: 2,
            EvaluationSourceFamily.ISSUES: 4,
            EvaluationSourceFamily.PULL_REQUESTS: 2,
            EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 4,
        }
    )
