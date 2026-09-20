"""Characterize Experiment A: catalog-derived resolver action coverage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import ResponseMode
from rag_reliability.contracts.evaluation import EvaluationCase
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.catalog_action_resolver_candidate import (
    CatalogDerivedActionOperationResolver,
)
from rag_reliability.evaluation.operation_resolver_characterization import (
    Phase5OperationResolverCharacterizationReport,
)
from rag_reliability.evaluation.operation_resolver_protocol_v2 import (
    Phase5OperationResolverProtocolV2,
)
from rag_reliability.runtime.operation_catalog import load_runtime_operation_catalog
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    OperationResolution,
    ResolutionStatus,
)

_DESIGN_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_intervention_design_protocol_v1.json"
)
_DESIGN_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_post_reject_intervention_design_protocol_freeze_v1.json"
)
_BASELINE_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_operation_resolver_protocol_v2.json"
)
_BASELINE_CHARACTERIZATION_PATH = (
    Path("artifacts") / "development" / "phase5_operation_resolver_characterization_v2.json"
)
_DEVELOPMENT_PATH = Path("artifacts") / "development" / "phase4c_development_cases_v1.json"
_MANIFEST_PATH = Path("datasets") / "chunk_manifests" / "phase3d_chunk_manifest_v1.json"
_OUTPUT_PATH = (
    Path("artifacts") / "development" / "phase5_catalog_action_resolver_characterization_v1.json"
)

_DESIGN_PROTOCOL_SHA256 = "f5a607f0051fe14b417ce41e6d01359d9c686e3f754711a917293369a22f44b8"
_DESIGN_FREEZE_SHA256 = "5596e5f561f5bf19e2583666e9260feaa3ed00eef4a9ca5b2937042c318c2322"
_BASELINE_PROTOCOL_SHA256 = "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
_BASELINE_CHARACTERIZATION_SHA256 = (
    "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
)
_DEVELOPMENT_SHA256 = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"

_INVITATION_CASE_IDS = frozenset(
    {
        "phase4-dev-repos-accept-invitation-current",
        "phase4-dev-repos-accept-invitation-success",
    }
)
_INVITATION_OPERATION_ID = "repos/accept-invitation-for-authenticated-user"


class ResolverFixtureCandidateObservation(ContractModel):
    fixture_id: NonEmptyStr
    expected_status: NonEmptyStr
    expected_operation_id: NonEmptyStr | None = None
    baseline_status: ResolutionStatus
    baseline_operation_ids: tuple[NonEmptyStr, ...]
    candidate_status: ResolutionStatus
    candidate_operation_ids: tuple[NonEmptyStr, ...]
    expectation_matched: bool
    false_confident_resolution: bool
    deterministic_across_repeats: bool
    changed_vs_baseline: bool


class DevelopmentResolverCandidateObservation(ContractModel):
    case_id: NonEmptyStr
    query: NonEmptyStr
    gold_operation_ids: tuple[NonEmptyStr, ...]
    baseline_status: ResolutionStatus
    baseline_operation_ids: tuple[NonEmptyStr, ...]
    candidate_status: ResolutionStatus
    candidate_operation_ids: tuple[NonEmptyStr, ...]
    candidate_correct_confident_resolution: bool
    candidate_false_confident_resolution: bool
    deterministic_across_repeats: bool
    changed_vs_baseline: bool
    invitation_target_case: bool

    @model_validator(mode="after")
    def validate_observation(self) -> Self:
        if (
            self.candidate_correct_confident_resolution
            and self.candidate_false_confident_resolution
        ):
            raise ValueError("candidate cannot be both correct and false-confident")

        if self.invitation_target_case:
            if self.gold_operation_ids != (_INVITATION_OPERATION_ID,):
                raise ValueError("invitation target gold identity drifted")

        return self


class Phase5CatalogActionResolverCharacterizationV1(ContractModel):
    report_version: Literal["phase5-catalog-action-resolver-characterization-v1"] = (
        "phase5-catalog-action-resolver-characterization-v1"
    )

    evidence_class: Literal["spent_development_diagnostic_and_fixed_fixture_characterization"] = (
        "spent_development_diagnostic_and_fixed_fixture_characterization"
    )

    design_protocol_sha256: Sha256 = _DESIGN_PROTOCOL_SHA256
    design_freeze_sha256: Sha256 = _DESIGN_FREEZE_SHA256
    baseline_resolver_protocol_sha256: Sha256 = _BASELINE_PROTOCOL_SHA256
    baseline_resolver_characterization_sha256: Sha256 = _BASELINE_CHARACTERIZATION_SHA256
    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    chunk_manifest_sha256: Sha256 = _MANIFEST_SHA256

    candidate_id: Literal["phase5-catalog-derived-action-resolver-v3"] = (
        "phase5-catalog-derived-action-resolver-v3"
    )

    candidate_action_source: Literal[
        "first_normalized_operation_token_after_namespace_from_runtime_catalog"
    ] = "first_normalized_operation_token_after_namespace_from_runtime_catalog"

    catalog_operation_count: Literal[20] = 20
    fixed_fixture_count: Literal[10] = 10
    development_answerable_case_count: Literal[20] = 20
    deterministic_repeat_count: Literal[3] = 3

    fixed_fixture_expectation_mismatch_count: int = Field(ge=0, le=10)
    fixed_fixture_false_confident_count: int = Field(ge=0, le=10)
    fixed_fixture_nondeterministic_count: int = Field(ge=0, le=10)

    development_false_confident_count: int = Field(ge=0, le=20)
    development_nondeterministic_count: int = Field(ge=0, le=20)
    development_changed_case_count: int = Field(ge=0, le=20)
    development_new_correct_resolution_count: int = Field(ge=0, le=20)

    invitation_target_case_count: Literal[2] = 2
    invitation_correct_resolution_count: int = Field(ge=0, le=2)

    fixture_observations: tuple[ResolverFixtureCandidateObservation, ...] = Field(
        min_length=10,
        max_length=10,
    )
    development_observations: tuple[
        DevelopmentResolverCandidateObservation,
        ...,
    ] = Field(min_length=20, max_length=20)

    characterization_passed: bool
    characterization_failures: tuple[NonEmptyStr, ...]

    hard_coded_accept_token_used: Literal[False] = False
    evaluator_fields_passed_to_candidate: Literal[False] = False

    development_role: Literal["diagnostic_only_spent_for_future_confirmation"] = (
        "diagnostic_only_spent_for_future_confirmation"
    )

    companion_candidate_executed: Literal[False] = False
    composed_candidate_executed: Literal[False] = False
    fresh_confirmation_executed: Literal[False] = False

    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False

    runtime_resolver_changed: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False

    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if self.characterization_passed != (len(self.characterization_failures) == 0):
            raise ValueError("characterization verdict does not reconcile")

        if tuple(item.fixture_id for item in self.fixture_observations) != tuple(
            sorted(item.fixture_id for item in self.fixture_observations)
        ):
            raise ValueError("fixture observations must be ID sorted")

        if tuple(item.case_id for item in self.development_observations) != tuple(
            sorted(item.case_id for item in self.development_observations)
        ):
            raise ValueError("DEVELOPMENT observations must be case-ID sorted")

        if (
            self.hard_coded_accept_token_used
            or self.evaluator_fields_passed_to_candidate
            or self.companion_candidate_executed
            or self.composed_candidate_executed
            or self.fresh_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.provider_invoked
            or self.runtime_resolver_changed
            or self.runtime_retriever_changed
            or self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.b0_executed
            or self.release_eligible
        ):
            raise ValueError("resolver characterization overclaimed execution state")

        return self


def _verified_bytes(
    repo_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> bytes:
    path = repo_root / relative_path
    content = path.read_bytes()

    if hashlib.sha256(content).hexdigest() != expected_sha256:
        raise ValueError(f"frozen artifact hash mismatch: {relative_path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(f"frozen artifact sidecar mismatch: {relative_path}")

    return content


def _load_development_cases(repo_root: Path) -> tuple[EvaluationCase, ...]:
    payload = json.loads(_verified_bytes(repo_root, _DEVELOPMENT_PATH, _DEVELOPMENT_SHA256))

    if not isinstance(payload, dict):
        raise ValueError("DEVELOPMENT suite must be an object")

    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("DEVELOPMENT suite requires records")

    cases: list[EvaluationCase] = []

    for raw_record in records:
        if not isinstance(raw_record, dict):
            raise ValueError("DEVELOPMENT record must be an object")

        raw_case = raw_record.get("case")
        if not isinstance(raw_case, dict):
            raise ValueError("DEVELOPMENT record requires case")

        case = EvaluationCase.model_validate(raw_case)

        if case.expected_response_mode is not ResponseMode.REFUSE:
            cases.append(case)

    if len(cases) != 20:
        raise ValueError("DEVELOPMENT answerable count drifted")

    return tuple(sorted(cases, key=lambda case: case.case_id))


def _gold_operation_ids(
    case: EvaluationCase,
    lineage: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                operation_id
                for evidence_id in case.required_evidence_ids
                for operation_id in lineage[evidence_id]
            }
        )
    )


def _fixture_matches(
    *,
    result: OperationResolution,
    expected_status: str,
    expected_operation_id: str | None,
) -> bool:
    if result.status.value != expected_status:
        return False

    if expected_status == ResolutionStatus.RESOLVED.value:
        return result.operation_ids == (expected_operation_id,)

    return True


def _false_confident_fixture(
    *,
    result: OperationResolution,
    expected_status: str,
    expected_operation_id: str | None,
) -> bool:
    if result.status is not ResolutionStatus.RESOLVED:
        return False

    return not (
        expected_status == ResolutionStatus.RESOLVED.value
        and result.operation_ids == (expected_operation_id,)
    )


def _correct_confident_development(
    *,
    result: OperationResolution,
    gold_operation_ids: tuple[str, ...],
) -> bool:
    return (
        result.status is ResolutionStatus.RESOLVED
        and len(gold_operation_ids) == 1
        and result.operation_ids == gold_operation_ids
    )


def _false_confident_development(
    *,
    result: OperationResolution,
    gold_operation_ids: tuple[str, ...],
) -> bool:
    if result.status is not ResolutionStatus.RESOLVED:
        return False

    return not (len(gold_operation_ids) == 1 and result.operation_ids == gold_operation_ids)


def build_phase5_catalog_action_resolver_characterization(
    repo_root: Path,
) -> Phase5CatalogActionResolverCharacterizationV1:
    """Execute only Experiment A against frozen fixtures and spent DEV."""

    _verified_bytes(repo_root, _DESIGN_PROTOCOL_PATH, _DESIGN_PROTOCOL_SHA256)
    _verified_bytes(repo_root, _DESIGN_FREEZE_PATH, _DESIGN_FREEZE_SHA256)

    protocol = Phase5OperationResolverProtocolV2.model_validate_json(
        _verified_bytes(
            repo_root,
            _BASELINE_PROTOCOL_PATH,
            _BASELINE_PROTOCOL_SHA256,
        )
    )

    baseline_characterization = Phase5OperationResolverCharacterizationReport.model_validate_json(
        _verified_bytes(
            repo_root,
            _BASELINE_CHARACTERIZATION_PATH,
            _BASELINE_CHARACTERIZATION_SHA256,
        )
    )

    if not baseline_characterization.acceptance_passed:
        raise ValueError("baseline resolver characterization is not accepted")

    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(repo_root, _MANIFEST_PATH, _MANIFEST_SHA256)
    )

    lineage = {chunk.chunk_id: tuple(chunk.linked_operation_ids) for chunk in manifest.chunks}

    catalog = load_runtime_operation_catalog(repo_root)
    baseline = DeterministicOperationResolver(catalog)
    candidate = CatalogDerivedActionOperationResolver(catalog)

    fixture_observations: list[ResolverFixtureCandidateObservation] = []

    for fixture in protocol.fixtures:
        baseline_result = baseline.resolve(fixture.query)
        repeats = tuple(
            candidate.resolve(fixture.query)
            for _ in range(protocol.acceptance.deterministic_repeat_count)
        )
        observed = repeats[0]
        deterministic = all(item == observed for item in repeats[1:])

        fixture_observations.append(
            ResolverFixtureCandidateObservation(
                fixture_id=fixture.fixture_id,
                expected_status=fixture.expected_status,
                expected_operation_id=fixture.expected_operation_id,
                baseline_status=baseline_result.status,
                baseline_operation_ids=baseline_result.operation_ids,
                candidate_status=observed.status,
                candidate_operation_ids=observed.operation_ids,
                expectation_matched=_fixture_matches(
                    result=observed,
                    expected_status=fixture.expected_status,
                    expected_operation_id=fixture.expected_operation_id,
                ),
                false_confident_resolution=_false_confident_fixture(
                    result=observed,
                    expected_status=fixture.expected_status,
                    expected_operation_id=fixture.expected_operation_id,
                ),
                deterministic_across_repeats=deterministic,
                changed_vs_baseline=observed != baseline_result,
            )
        )

    development_observations: list[DevelopmentResolverCandidateObservation] = []

    for case in _load_development_cases(repo_root):
        runtime_input = case.to_runtime_input()
        gold_operation_ids = _gold_operation_ids(case, lineage)

        baseline_result = baseline.resolve(runtime_input.query)
        repeats = tuple(candidate.resolve(runtime_input.query) for _ in range(3))
        observed = repeats[0]
        deterministic = all(item == observed for item in repeats[1:])

        development_observations.append(
            DevelopmentResolverCandidateObservation(
                case_id=case.case_id,
                query=case.query,
                gold_operation_ids=gold_operation_ids,
                baseline_status=baseline_result.status,
                baseline_operation_ids=baseline_result.operation_ids,
                candidate_status=observed.status,
                candidate_operation_ids=observed.operation_ids,
                candidate_correct_confident_resolution=(
                    _correct_confident_development(
                        result=observed,
                        gold_operation_ids=gold_operation_ids,
                    )
                ),
                candidate_false_confident_resolution=(
                    _false_confident_development(
                        result=observed,
                        gold_operation_ids=gold_operation_ids,
                    )
                ),
                deterministic_across_repeats=deterministic,
                changed_vs_baseline=observed != baseline_result,
                invitation_target_case=case.case_id in _INVITATION_CASE_IDS,
            )
        )

    ordered_fixtures = tuple(sorted(fixture_observations, key=lambda item: item.fixture_id))
    ordered_development = tuple(sorted(development_observations, key=lambda item: item.case_id))

    fixture_mismatch_count = sum(not item.expectation_matched for item in ordered_fixtures)
    fixture_false_confident_count = sum(
        item.false_confident_resolution for item in ordered_fixtures
    )
    fixture_nondeterministic_count = sum(
        not item.deterministic_across_repeats for item in ordered_fixtures
    )

    development_false_confident_count = sum(
        item.candidate_false_confident_resolution for item in ordered_development
    )
    development_nondeterministic_count = sum(
        not item.deterministic_across_repeats for item in ordered_development
    )
    development_changed_count = sum(item.changed_vs_baseline for item in ordered_development)
    development_new_correct_count = sum(
        item.changed_vs_baseline and item.candidate_correct_confident_resolution
        for item in ordered_development
    )

    invitation_correct_count = sum(
        item.invitation_target_case and item.candidate_correct_confident_resolution
        for item in ordered_development
    )

    failures: list[str] = []

    if fixture_mismatch_count != 0:
        failures.append("fixed_fixture_expectation_mismatch")

    if fixture_false_confident_count + development_false_confident_count != 0:
        failures.append("false_confident_resolution_present")

    if fixture_nondeterministic_count + development_nondeterministic_count != 0:
        failures.append("nondeterministic_resolution_present")

    if invitation_correct_count != 2:
        failures.append("invitation_target_cases_not_both_correctly_resolved")

    return Phase5CatalogActionResolverCharacterizationV1(
        fixed_fixture_expectation_mismatch_count=fixture_mismatch_count,
        fixed_fixture_false_confident_count=fixture_false_confident_count,
        fixed_fixture_nondeterministic_count=fixture_nondeterministic_count,
        development_false_confident_count=development_false_confident_count,
        development_nondeterministic_count=development_nondeterministic_count,
        development_changed_case_count=development_changed_count,
        development_new_correct_resolution_count=development_new_correct_count,
        invitation_correct_resolution_count=invitation_correct_count,
        fixture_observations=ordered_fixtures,
        development_observations=ordered_development,
        characterization_passed=len(failures) == 0,
        characterization_failures=tuple(failures),
    )


def materialize_phase5_catalog_action_resolver_characterization(
    repo_root: Path,
) -> tuple[Phase5CatalogActionResolverCharacterizationV1, str]:
    report = build_phase5_catalog_action_resolver_characterization(repo_root)
    digest = write_json_with_sha256(repo_root / _OUTPUT_PATH, report)
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_catalog_action_resolver_characterization(repo_root)

    print(f"PHASE5_CATALOG_ACTION_RESOLVER_SHA256={digest}")
    print(
        "PHASE5_CATALOG_ACTION_RESOLVER_FIXTURES="
        f"mismatch:{report.fixed_fixture_expectation_mismatch_count},"
        f"false_confident:{report.fixed_fixture_false_confident_count},"
        f"nondeterministic:{report.fixed_fixture_nondeterministic_count}"
    )
    print(
        "PHASE5_CATALOG_ACTION_RESOLVER_DEVELOPMENT="
        f"changed:{report.development_changed_case_count},"
        f"new_correct:{report.development_new_correct_resolution_count},"
        f"false_confident:{report.development_false_confident_count},"
        f"nondeterministic:{report.development_nondeterministic_count}"
    )
    print(
        f"PHASE5_CATALOG_ACTION_RESOLVER_INVITATION={report.invitation_correct_resolution_count}/2"
    )
    print(f"PHASE5_CATALOG_ACTION_RESOLVER_PASSED={str(report.characterization_passed).lower()}")

    for failure in report.characterization_failures:
        print(f"PHASE5_CATALOG_ACTION_RESOLVER_FAILURE={failure}")

    print("PHASE5_COMPANION_CANDIDATE_EXECUTED=false")
    print("PHASE5_COMPOSED_CANDIDATE_EXECUTED=false")
    print("PHASE5_FRESH_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_RUNTIME_RESOLVER_CHANGED=false")
    print("PHASE5_B0_EXECUTED=false")


if __name__ == "__main__":
    main()
