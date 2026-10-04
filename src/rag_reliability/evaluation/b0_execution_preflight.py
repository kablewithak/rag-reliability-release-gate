"""Fail-closed preflight for the exact authorized Phase 5 B0 execution slots."""

from __future__ import annotations

from pathlib import Path

from rag_reliability.evaluation.b0_authorization_models import (
    Arm,
    B0AuthorizationError,
    B0FileBinding,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ExecutionSlotV1,
    Phase5B0SpecimenV1,
    model_sha256,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
)
from rag_reliability.evaluation.b0_specimen_authorization import (
    _AUTHORIZATION_PATH,
    _SPECIMEN_PATH,
    capture_phase5_b0_environment,
    git_output,
    load_coverage,
    load_raw_fixture,
    require_clean_worktree,
    sha256_bytes,
    sha256_text,
    verified_sidecar_sha256,
    verify_fixture_coverage_alignment,
)


def _verify_file_bindings(
    repo_root: Path,
    bindings: tuple[B0FileBinding, ...],
) -> None:
    for binding in bindings:
        observed = sha256_bytes((repo_root / binding.path).read_bytes())
        if observed != binding.sha256:
            raise B0AuthorizationError(
                f"bound file drifted: {binding.path}"
            )


def load_frozen_specimen_and_authorization(
    repo_root: Path,
) -> tuple[Phase5B0SpecimenV1, Phase5B0ExecutionAuthorizationV1]:
    specimen_sha = verified_sidecar_sha256(repo_root, _SPECIMEN_PATH)
    specimen = Phase5B0SpecimenV1.model_validate_json(
        (repo_root / _SPECIMEN_PATH).read_bytes()
    )
    authorization = Phase5B0ExecutionAuthorizationV1.model_validate_json(
        (repo_root / _AUTHORIZATION_PATH).read_bytes()
    )
    verified_sidecar_sha256(repo_root, _AUTHORIZATION_PATH)

    if model_sha256(specimen) != specimen_sha:
        raise B0AuthorizationError("specimen sidecar does not bind parsed specimen")
    if authorization.specimen_sha256 != specimen_sha:
        raise B0AuthorizationError("authorization does not bind frozen specimen")

    return specimen, authorization


def preflight_specimen(
    repo_root: Path,
    *,
    require_main_clean: bool,
) -> tuple[
    Phase5B0SpecimenV1,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
]:
    repo_root = repo_root.resolve()
    specimen, authorization = load_frozen_specimen_and_authorization(repo_root)

    if require_main_clean:
        branch = git_output(repo_root, "branch", "--show-current")
        if branch != "main":
            raise B0AuthorizationError(
                f"post-merge B0 execution requires main, observed: {branch}"
            )
        require_clean_worktree(repo_root)

    _verify_file_bindings(repo_root, specimen.runtime_source_bindings)
    _verify_file_bindings(repo_root, specimen.orchestration_source_bindings)
    _verify_file_bindings(repo_root, specimen.evaluator_source_bindings)
    _verify_file_bindings(repo_root, specimen.governance_artifact_bindings)

    environment = capture_phase5_b0_environment()
    if environment != specimen.environment:
        raise B0AuthorizationError("B0 execution environment drifted from authorization")

    coverage = load_coverage(repo_root)
    fixture = load_raw_fixture(repo_root)
    verify_fixture_coverage_alignment(coverage, fixture)

    if coverage.replay_fixture_sha256 != specimen.replay_fixture_sha256:
        raise B0AuthorizationError("coverage replay fixture binding drifted")
    if authorization.replay_fixture_sha256 != specimen.replay_fixture_sha256:
        raise B0AuthorizationError("authorization replay fixture binding drifted")
    if authorization.fixture_coverage_sha256 != specimen.fixture_coverage_sha256:
        raise B0AuthorizationError("authorization coverage binding drifted")
    if authorization.runtime_configuration_id != specimen.runtime_configuration_id:
        raise B0AuthorizationError("authorization runtime configuration drifted")

    return specimen, authorization, coverage, fixture


def _slot_for(
    authorization: Phase5B0ExecutionAuthorizationV1,
    *,
    arm: Arm,
    case_id: str,
) -> Phase5B0ExecutionSlotV1:
    matches = tuple(
        slot
        for slot in authorization.slots
        if slot.arm == arm and slot.case_id == case_id
    )
    if len(matches) != 1:
        raise B0AuthorizationError(
            f"exactly one authorized slot required for {arm}:{case_id}"
        )
    return matches[0]


def preflight_execution_slot_with_objects(
    *,
    authorization: Phase5B0ExecutionAuthorizationV1,
    coverage: Phase5B0ReplayFixtureCoverageV1,
    fixture: Phase5B0ReplayFixtureV1,
    arm: Arm,
    case_id: str,
    role: str,
    query: str,
    started_slot_ids: set[str],
    primary_batch_valid_and_custodied: bool,
) -> Phase5B0ExecutionSlotV1:
    if role not in {
        "evaluation_development_case",
        "intervention_tuning_case",
    }:
        raise B0AuthorizationError("protected or unauthorized role rejected")

    if len(started_slot_ids) >= authorization.maximum_total_case_starts:
        raise B0AuthorizationError("B0 execution budget exhausted")

    slot = _slot_for(authorization, arm=arm, case_id=case_id)

    if slot.slot_id in started_slot_ids:
        raise B0AuthorizationError("B0 execution slot already consumed")

    if arm == "replication" and not primary_batch_valid_and_custodied:
        raise B0AuthorizationError(
            "replication requires valid, custodied G5N primary evidence"
        )

    if slot.role != role:
        raise B0AuthorizationError("execution role does not match authorized slot")

    query_sha = sha256_text(query)
    if slot.query_sha256 != query_sha:
        raise B0AuthorizationError("execution query does not match authorized slot")
    if slot.fixture_key_sha256 != query_sha:
        raise B0AuthorizationError("authorized fixture key does not match query")

    coverage_by_case = {case.case_id: case for case in coverage.cases}
    record = coverage_by_case.get(case_id)
    if record is None:
        raise B0AuthorizationError("coverage receipt missing execution case")
    if record.query_sha256 != query_sha:
        raise B0AuthorizationError("coverage query binding drifted")
    if record.fixture_key_sha256 != query_sha:
        raise B0AuthorizationError("coverage fixture-key binding drifted")

    fixture_queries = {entry.query for entry in fixture.entries}
    if query not in fixture_queries:
        raise B0AuthorizationError("authorized query has no replay fixture entry")

    return slot


def preflight_execution_slot(
    repo_root: Path,
    *,
    arm: Arm,
    case_id: str,
    role: str,
    query: str,
    started_slot_ids: set[str],
    primary_batch_valid_and_custodied: bool,
) -> Phase5B0ExecutionSlotV1:
    _specimen, authorization, coverage, fixture = preflight_specimen(
        repo_root,
        require_main_clean=True,
    )
    return preflight_execution_slot_with_objects(
        authorization=authorization,
        coverage=coverage,
        fixture=fixture,
        arm=arm,
        case_id=case_id,
        role=role,
        query=query,
        started_slot_ids=started_slot_ids,
        primary_batch_valid_and_custodied=primary_batch_valid_and_custodied,
    )
