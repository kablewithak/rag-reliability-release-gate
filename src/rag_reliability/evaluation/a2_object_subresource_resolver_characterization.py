"""Execute the single bounded Phase 5 A2 resolver characterization."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.chunked import Phase3dChunkManifest
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.a2_object_subresource_resolver_candidate import (
    A2ObjectSubresourceOperationResolver,
)
from rag_reliability.evaluation.a2_successor_resolver_protocol import (
    Phase5A2SuccessorResolverProtocolV1,
)
from rag_reliability.evaluation.a2_successor_resolver_protocol_freeze import (
    Phase5A2SuccessorResolverProtocolFreezeV1,
)
from rag_reliability.evaluation.catalog_action_resolver_characterization import (
    DevelopmentResolverCandidateObservation,
    Phase5CatalogActionResolverCharacterizationV1,
    ResolverFixtureCandidateObservation,
    _correct_confident_development,
    _false_confident_development,
    _false_confident_fixture,
    _fixture_matches,
    _gold_operation_ids,
    _load_development_cases,
)
from rag_reliability.evaluation.operation_resolver_characterization import (
    Phase5OperationResolverCharacterizationReport,
)
from rag_reliability.evaluation.operation_resolver_protocol_v2 import (
    Phase5OperationResolverProtocolV2,
)
from rag_reliability.runtime.operation_catalog import (
    load_runtime_operation_catalog,
)
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
)

_A2_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_a2_successor_resolver_protocol_v1.json"
)
_A2_PROTOCOL_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_a2_successor_resolver_protocol_freeze_v1.json"
)
_A1_CHARACTERIZATION_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_catalog_action_resolver_characterization_v1.json"
)
_BASELINE_PROTOCOL_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_protocol_v2.json"
)
_BASELINE_CHARACTERIZATION_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_characterization_v2.json"
)
_MANIFEST_PATH = (
    Path("datasets")
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_a2_object_subresource_resolver_characterization_v1.json"
)

_A2_PROTOCOL_SHA256 = (
    "37af55f372cf3bc34c10c63ef1d215265f077fea0114b61059a508e0c99ad293"
)
_A2_PROTOCOL_FREEZE_SHA256 = (
    "ac4a3fc834c4d9318fab92ce8e20692c9b0f330cef087b74346daf3dd19a3112"
)
_A1_CHARACTERIZATION_SHA256 = (
    "2ad66ffeb2b86c2348789cdf8c19d55492bd8a0001871e0a2566d5829e92de88"
)
_BASELINE_PROTOCOL_SHA256 = (
    "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
)
_BASELINE_CHARACTERIZATION_SHA256 = (
    "8b342a210bf535bb0284e3611935d6e4b6e907e6000329c2c47021791648d7cc"
)
_DEVELOPMENT_SHA256 = (
    "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
)
_MANIFEST_SHA256 = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)

_INVITATION_CASE_IDS = frozenset(
    {
        "phase4-dev-repos-accept-invitation-current",
        "phase4-dev-repos-accept-invitation-success",
    }
)


class Phase5A2ObjectSubresourceResolverCharacterizationV1(ContractModel):
    """Machine-readable A2 bounded characterization result."""

    report_version: Literal[
        "phase5-a2-object-subresource-resolver-characterization-v1"
    ] = "phase5-a2-object-subresource-resolver-characterization-v1"

    experiment_id: Literal[
        "phase5-a2-object-subresource-resolver-v1"
    ] = "phase5-a2-object-subresource-resolver-v1"

    evidence_class: Literal[
        "spent_development_diagnostic_and_fixed_fixture_characterization"
    ] = "spent_development_diagnostic_and_fixed_fixture_characterization"

    a2_protocol_sha256: Sha256 = _A2_PROTOCOL_SHA256
    a2_protocol_freeze_sha256: Sha256 = _A2_PROTOCOL_FREEZE_SHA256
    parent_a1_characterization_sha256: Sha256 = _A1_CHARACTERIZATION_SHA256
    baseline_resolver_protocol_sha256: Sha256 = _BASELINE_PROTOCOL_SHA256
    baseline_resolver_characterization_sha256: Sha256 = (
        _BASELINE_CHARACTERIZATION_SHA256
    )
    development_suite_sha256: Sha256 = _DEVELOPMENT_SHA256
    chunk_manifest_sha256: Sha256 = _MANIFEST_SHA256

    candidate_id: Literal[
        "phase5-a2-namespace-action-object-subresource-resolver-v1"
    ] = "phase5-a2-namespace-action-object-subresource-resolver-v1"

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

    fixture_observations: tuple[
        ResolverFixtureCandidateObservation,
        ...,
    ] = Field(min_length=10, max_length=10)

    development_observations: tuple[
        DevelopmentResolverCandidateObservation,
        ...,
    ] = Field(min_length=20, max_length=20)

    run_validity: Literal["VALID"] = "VALID"
    scientific_disposition: Literal[
        "PASS",
        "REJECT",
        "INCONCLUSIVE",
    ]

    characterization_passed: bool
    characterization_failures: tuple[NonEmptyStr, ...]

    candidate_implemented: Literal[True] = True
    candidate_executed: Literal[True] = True

    hard_coded_invitation_target_used: Literal[False] = False
    evaluator_fields_passed_to_candidate: Literal[False] = False
    parameter_sweep_executed: Literal[False] = False
    provider_invoked: Literal[False] = False

    post_reject_confirmation_inspected: Literal[False] = False
    post_reject_confirmation_executed: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    runtime_resolver_changed: Literal[False] = False
    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_selected: Literal[False] = False

    baseline_readiness_review_required: Literal[True] = True
    automatic_a3_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    chaos_executed: Literal[False] = False
    load_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        expected_pass = len(self.characterization_failures) == 0

        if self.characterization_passed != expected_pass:
            raise ValueError("A2 characterization verdict does not reconcile")

        expected_disposition = "PASS" if expected_pass else "REJECT"
        if self.scientific_disposition != expected_disposition:
            raise ValueError("A2 scientific disposition does not reconcile")

        fixture_ids = tuple(
            item.fixture_id
            for item in self.fixture_observations
        )
        if fixture_ids != tuple(sorted(fixture_ids)):
            raise ValueError("A2 fixture observations must be ID sorted")

        case_ids = tuple(
            item.case_id
            for item in self.development_observations
        )
        if case_ids != tuple(sorted(case_ids)):
            raise ValueError(
                "A2 DEVELOPMENT observations must be case-ID sorted"
            )

        if (
            self.hard_coded_invitation_target_used
            or self.evaluator_fields_passed_to_candidate
            or self.parameter_sweep_executed
            or self.provider_invoked
            or self.post_reject_confirmation_inspected
            or self.post_reject_confirmation_executed
            or self.held_out_case_content_read
            or self.held_out_outcomes_exposed
            or self.runtime_resolver_changed
            or self.runtime_retriever_changed
            or self.retrieval_configuration_selected
            or self.semantic_runtime_configuration_selected
            or self.automatic_a3_authorized
            or self.b0_executed
            or self.chaos_executed
            or self.load_executed
            or self.release_eligible
        ):
            raise ValueError("A2 characterization overclaimed execution state")

        return self


def _verified_bytes(
    repo_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> bytes:
    path = repo_root / relative_path
    content = path.read_bytes()

    if hashlib.sha256(content).hexdigest() != expected_sha256:
        raise ValueError(
            f"frozen artifact hash mismatch: {relative_path}"
        )

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise ValueError(
            f"frozen artifact sidecar mismatch: {relative_path}"
        )

    return content


def build_phase5_a2_object_subresource_resolver_characterization(
    repo_root: Path,
) -> Phase5A2ObjectSubresourceResolverCharacterizationV1:
    """Execute exactly one A2 candidate against fixed fixtures and spent DEV."""

    a2_protocol = Phase5A2SuccessorResolverProtocolV1.model_validate_json(
        _verified_bytes(
            repo_root,
            _A2_PROTOCOL_PATH,
            _A2_PROTOCOL_SHA256,
        )
    )

    a2_freeze = Phase5A2SuccessorResolverProtocolFreezeV1.model_validate_json(
        _verified_bytes(
            repo_root,
            _A2_PROTOCOL_FREEZE_PATH,
            _A2_PROTOCOL_FREEZE_SHA256,
        )
    )

    if a2_freeze.protocol_sha256 != _A2_PROTOCOL_SHA256:
        raise ValueError("A2 freeze does not bind the expected protocol")

    if not a2_freeze.protocol_frozen:
        raise ValueError("A2 protocol is not frozen")

    a1 = Phase5CatalogActionResolverCharacterizationV1.model_validate_json(
        _verified_bytes(
            repo_root,
            _A1_CHARACTERIZATION_PATH,
            _A1_CHARACTERIZATION_SHA256,
        )
    )

    if a1.characterization_passed:
        raise ValueError("A2 requires the recorded A1 rejection")

    baseline_protocol = Phase5OperationResolverProtocolV2.model_validate_json(
        _verified_bytes(
            repo_root,
            _BASELINE_PROTOCOL_PATH,
            _BASELINE_PROTOCOL_SHA256,
        )
    )

    baseline_characterization = (
        Phase5OperationResolverCharacterizationReport.model_validate_json(
            _verified_bytes(
                repo_root,
                _BASELINE_CHARACTERIZATION_PATH,
                _BASELINE_CHARACTERIZATION_SHA256,
            )
        )
    )

    if not baseline_characterization.acceptance_passed:
        raise ValueError(
            "baseline resolver characterization is not accepted"
        )

    manifest = Phase3dChunkManifest.model_validate_json(
        _verified_bytes(
            repo_root,
            _MANIFEST_PATH,
            _MANIFEST_SHA256,
        )
    )

    if a2_protocol.gate.parameter_sweep_allowed:
        raise ValueError("A2 protocol unexpectedly allows parameter sweep")

    if a2_protocol.gate.provider_calls_allowed != 0:
        raise ValueError("A2 protocol unexpectedly allows provider calls")

    catalog = load_runtime_operation_catalog(repo_root)

    if len(catalog) != 20:
        raise ValueError("A2 runtime catalog operation count drifted")

    baseline = DeterministicOperationResolver(catalog)
    candidate = A2ObjectSubresourceOperationResolver(catalog)

    fixture_observations: list[
        ResolverFixtureCandidateObservation
    ] = []

    for fixture in baseline_protocol.fixtures:
        baseline_result = baseline.resolve(fixture.query)
        repeats = tuple(
            candidate.resolve(fixture.query)
            for _ in range(
                baseline_protocol.acceptance.deterministic_repeat_count
            )
        )
        observed = repeats[0]
        deterministic = all(
            item == observed
            for item in repeats[1:]
        )

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

    lineage = {
        chunk.chunk_id: tuple(chunk.linked_operation_ids)
        for chunk in manifest.chunks
    }

    development_observations: list[
        DevelopmentResolverCandidateObservation
    ] = []

    for case in _load_development_cases(repo_root):
        runtime_input = case.to_runtime_input()
        gold_operation_ids = _gold_operation_ids(
            case,
            lineage,
        )

        baseline_result = baseline.resolve(runtime_input.query)
        repeats = tuple(
            candidate.resolve(runtime_input.query)
            for _ in range(
                baseline_protocol.acceptance.deterministic_repeat_count
            )
        )
        observed = repeats[0]
        deterministic = all(
            item == observed
            for item in repeats[1:]
        )

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
                invitation_target_case=(
                    case.case_id in _INVITATION_CASE_IDS
                ),
            )
        )

    ordered_fixtures = tuple(
        sorted(
            fixture_observations,
            key=lambda item: item.fixture_id,
        )
    )
    ordered_development = tuple(
        sorted(
            development_observations,
            key=lambda item: item.case_id,
        )
    )

    fixture_mismatch_count = sum(
        not item.expectation_matched
        for item in ordered_fixtures
    )
    fixture_false_confident_count = sum(
        item.false_confident_resolution
        for item in ordered_fixtures
    )
    fixture_nondeterministic_count = sum(
        not item.deterministic_across_repeats
        for item in ordered_fixtures
    )

    development_false_confident_count = sum(
        item.candidate_false_confident_resolution
        for item in ordered_development
    )
    development_nondeterministic_count = sum(
        not item.deterministic_across_repeats
        for item in ordered_development
    )
    development_changed_count = sum(
        item.changed_vs_baseline
        for item in ordered_development
    )
    development_new_correct_count = sum(
        item.changed_vs_baseline
        and item.candidate_correct_confident_resolution
        for item in ordered_development
    )

    invitation_correct_count = sum(
        item.invitation_target_case
        and item.candidate_correct_confident_resolution
        for item in ordered_development
    )

    failures: list[str] = []

    if fixture_mismatch_count != 0:
        failures.append(
            "fixed_fixture_expectation_mismatch"
        )

    if fixture_false_confident_count != 0:
        failures.append(
            "fixed_fixture_false_confident_resolution_present"
        )

    if fixture_nondeterministic_count != 0:
        failures.append(
            "fixed_fixture_nondeterministic_resolution_present"
        )

    if invitation_correct_count != 2:
        failures.append(
            "invitation_target_cases_not_both_correctly_resolved"
        )

    if development_false_confident_count != 0:
        failures.append(
            "development_false_confident_resolution_present"
        )

    if development_nondeterministic_count != 0:
        failures.append(
            "development_nondeterministic_resolution_present"
        )

    disposition: Literal[
        "PASS",
        "REJECT",
        "INCONCLUSIVE",
    ] = "PASS" if not failures else "REJECT"

    return Phase5A2ObjectSubresourceResolverCharacterizationV1(
        fixed_fixture_expectation_mismatch_count=(
            fixture_mismatch_count
        ),
        fixed_fixture_false_confident_count=(
            fixture_false_confident_count
        ),
        fixed_fixture_nondeterministic_count=(
            fixture_nondeterministic_count
        ),
        development_false_confident_count=(
            development_false_confident_count
        ),
        development_nondeterministic_count=(
            development_nondeterministic_count
        ),
        development_changed_case_count=(
            development_changed_count
        ),
        development_new_correct_resolution_count=(
            development_new_correct_count
        ),
        invitation_correct_resolution_count=(
            invitation_correct_count
        ),
        fixture_observations=ordered_fixtures,
        development_observations=ordered_development,
        scientific_disposition=disposition,
        characterization_passed=not failures,
        characterization_failures=tuple(failures),
    )


def materialize_phase5_a2_object_subresource_resolver_characterization(
    repo_root: Path,
) -> tuple[
    Phase5A2ObjectSubresourceResolverCharacterizationV1,
    str,
]:
    report = (
        build_phase5_a2_object_subresource_resolver_characterization(
            repo_root
        )
    )
    digest = write_json_with_sha256(
        repo_root / _OUTPUT_PATH,
        report,
    )
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = (
        materialize_phase5_a2_object_subresource_resolver_characterization(
            repo_root
        )
    )

    print(
        "PHASE5_A2_CHARACTERIZATION_SHA256="
        f"{digest}"
    )
    print(
        "PHASE5_A2_RUN_VALIDITY="
        f"{report.run_validity}"
    )
    print(
        "PHASE5_A2_SCIENTIFIC_DISPOSITION="
        f"{report.scientific_disposition}"
    )
    print(
        "PHASE5_A2_FIXTURES="
        f"mismatch:{report.fixed_fixture_expectation_mismatch_count},"
        f"false_confident:{report.fixed_fixture_false_confident_count},"
        f"nondeterministic:{report.fixed_fixture_nondeterministic_count}"
    )
    print(
        "PHASE5_A2_DEVELOPMENT="
        f"changed:{report.development_changed_case_count},"
        f"new_correct:{report.development_new_correct_resolution_count},"
        f"false_confident:{report.development_false_confident_count},"
        f"nondeterministic:{report.development_nondeterministic_count}"
    )
    print(
        "PHASE5_A2_INVITATION="
        f"{report.invitation_correct_resolution_count}/2"
    )

    for failure in report.characterization_failures:
        print(
            "PHASE5_A2_FAILURE="
            f"{failure}"
        )

    print("PHASE5_POST_REJECT_CONFIRMATION_INSPECTED=false")
    print("PHASE5_POST_REJECT_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_RUNTIME_RESOLVER_CHANGED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_BASELINE_READINESS_REVIEW_REQUIRED=true")
    print("PHASE5_AUTOMATIC_A3_AUTHORIZED=false")


if __name__ == "__main__":
    main()
