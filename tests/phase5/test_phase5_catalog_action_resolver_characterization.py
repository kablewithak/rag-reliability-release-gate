from __future__ import annotations

import hashlib
from functools import cache
from pathlib import Path

from rag_reliability.evaluation.catalog_action_resolver_characterization import (
    Phase5CatalogActionResolverCharacterizationV1,
    materialize_phase5_catalog_action_resolver_characterization,
)
from rag_reliability.runtime.operation_resolution import ResolutionStatus

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT / "artifacts" / "development" / "phase5_catalog_action_resolver_characterization_v1.json"
)


@cache
def _materialized() -> tuple[
    Phase5CatalogActionResolverCharacterizationV1,
    str,
]:
    return materialize_phase5_catalog_action_resolver_characterization(ROOT)


def test_candidate_preserves_fixed_fixture_contract() -> None:
    report, _digest = _materialized()

    assert report.fixed_fixture_count == 10
    assert report.fixed_fixture_expectation_mismatch_count == 0
    assert report.fixed_fixture_false_confident_count == 0
    assert report.fixed_fixture_nondeterministic_count == 0


def test_candidate_rejects_when_only_one_invitation_case_resolves() -> None:
    report, _digest = _materialized()

    assert report.invitation_target_case_count == 2
    assert report.invitation_correct_resolution_count == 1

    targets = {
        item.case_id: item
        for item in report.development_observations
        if item.invitation_target_case
    }

    assert set(targets) == {
        "phase4-dev-repos-accept-invitation-current",
        "phase4-dev-repos-accept-invitation-success",
    }

    current_case = targets["phase4-dev-repos-accept-invitation-current"]
    assert current_case.candidate_status is ResolutionStatus.AMBIGUOUS
    assert current_case.candidate_operation_ids == (
        "repos/accept-invitation-for-authenticated-user",
        "repos/list-attestations",
    )
    assert current_case.candidate_correct_confident_resolution is False
    assert current_case.candidate_false_confident_resolution is False

    success_case = targets["phase4-dev-repos-accept-invitation-success"]
    assert success_case.candidate_status is ResolutionStatus.RESOLVED
    assert success_case.candidate_operation_ids == (
        "repos/accept-invitation-for-authenticated-user",
    )
    assert success_case.candidate_correct_confident_resolution is True
    assert success_case.candidate_false_confident_resolution is False


def test_candidate_rejection_is_safe_and_deterministic() -> None:
    report, _digest = _materialized()

    assert report.development_answerable_case_count == 20
    assert report.development_changed_case_count == 3
    assert report.development_new_correct_resolution_count == 1
    assert report.development_false_confident_count == 0
    assert report.development_nondeterministic_count == 0

    assert report.characterization_passed is False
    assert report.characterization_failures == (
        "invitation_target_cases_not_both_correctly_resolved",
    )


def test_candidate_preserves_nonclaims() -> None:
    report, _digest = _materialized()

    assert report.hard_coded_accept_token_used is False
    assert report.evaluator_fields_passed_to_candidate is False

    assert report.companion_candidate_executed is False
    assert report.composed_candidate_executed is False
    assert report.fresh_confirmation_executed is False

    assert report.held_out_case_content_read is False
    assert report.held_out_outcomes_exposed is False
    assert report.provider_invoked is False

    assert report.runtime_resolver_changed is False
    assert report.runtime_retriever_changed is False
    assert report.retrieval_configuration_selected is False
    assert report.semantic_runtime_configuration_selected is False

    assert report.b0_executed is False
    assert report.release_eligible is False


def test_characterization_materialization_is_deterministic() -> None:
    first_report, first_sha = _materialized()
    second_report, second_sha = materialize_phase5_catalog_action_resolver_characterization(ROOT)

    assert first_report == second_report
    assert first_sha == second_sha
    assert first_sha == hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()
