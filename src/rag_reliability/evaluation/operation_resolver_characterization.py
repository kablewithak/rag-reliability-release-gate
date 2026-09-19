"""Characterize the deterministic Phase 5 operation resolver against frozen intent."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.operation_resolver_protocol_freeze_v2 import (
    Phase5OperationResolverProtocolFreezeReceiptV2,
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

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_operation_resolver_protocol_v2.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_protocol_freeze_v2.json"
)
_OUTPUT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_operation_resolver_characterization_v2.json"
)

_PROTOCOL_SHA256: Literal[
    "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
] = "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"

_FREEZE_SHA256: Literal[
    "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"
] = "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"


class ResolverFixtureObservation(ContractModel):
    """Observed deterministic resolver behavior for one frozen fixture."""

    fixture_id: NonEmptyStr
    expected_status: NonEmptyStr
    expected_operation_id: NonEmptyStr | None = None
    observed_status: ResolutionStatus
    observed_operation_ids: tuple[NonEmptyStr, ...]
    expectation_matched: bool
    false_confident_resolution: bool
    deterministic_across_repeats: bool


class Phase5OperationResolverCharacterizationReport(ContractModel):
    """Offline characterization only; no retrieval configuration is promoted."""

    report_version: Literal[
        "phase5-operation-resolver-characterization-v2"
    ] = "phase5-operation-resolver-characterization-v2"

    evidence_class: Literal[
        "runtime_boundary_characterization"
    ] = "runtime_boundary_characterization"

    protocol_sha256: Literal[
        "38b23aafe7a505480de774d70e4da9c5e6e3c34c9be2dddff2eb3a137dc2cb0f"
    ] = _PROTOCOL_SHA256

    protocol_freeze_receipt_sha256: Literal[
        "1f5b8e7d1cc4f2d577dbb7c580e6992a66be459be988be3b5ac90f25012a5df1"
    ] = _FREEZE_SHA256

    catalog_source: Literal[
        "frozen_phase3d_current_authoritative_operation_core_chunks"
    ] = "frozen_phase3d_current_authoritative_operation_core_chunks"

    catalog_operation_count: int = Field(ge=1)
    fixture_count: Literal[10] = 10
    deterministic_repeat_count: Literal[3] = 3

    resolved_fixture_count: int = Field(ge=0, le=10)
    ambiguous_fixture_count: int = Field(ge=0, le=10)
    unresolved_fixture_count: int = Field(ge=0, le=10)
    expectation_mismatch_count: int = Field(ge=0, le=10)
    false_confident_resolution_count: int = Field(ge=0, le=10)
    nondeterministic_fixture_count: int = Field(ge=0, le=10)
    resolution_coverage: float = Field(ge=0.0, le=1.0)

    observations: tuple[ResolverFixtureObservation, ...] = Field(
        min_length=10,
        max_length=10,
    )

    acceptance_passed: bool
    acceptance_failures: tuple[NonEmptyStr, ...]

    evaluator_fields_passed_to_resolver: Literal[False] = False
    provider_invoked: Literal[False] = False
    development_gold_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False

    runtime_retriever_changed: Literal[False] = False
    retrieval_configuration_selected: Literal[False] = False
    semantic_runtime_configuration_frozen: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if (
            self.resolved_fixture_count
            + self.ambiguous_fixture_count
            + self.unresolved_fixture_count
            != self.fixture_count
        ):
            raise ValueError("resolver status counts do not reconcile")

        expected_coverage = self.resolved_fixture_count / self.fixture_count
        if abs(self.resolution_coverage - expected_coverage) > 1e-12:
            raise ValueError("resolver coverage does not reconcile")

        if self.acceptance_passed != (len(self.acceptance_failures) == 0):
            raise ValueError("resolver acceptance result does not reconcile")

        if tuple(item.fixture_id for item in self.observations) != tuple(
            sorted(item.fixture_id for item in self.observations)
        ):
            raise ValueError("resolver observations must be fixture-ID sorted")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_bytes(path: Path, expected_sha256: str) -> bytes:
    content = path.read_bytes()
    if _sha256_bytes(content) != expected_sha256:
        raise ValueError(f"frozen resolver artifact hash mismatch: {path}")

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{expected_sha256}  {path.name}"
    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise ValueError(f"frozen resolver artifact sidecar mismatch: {path}")

    return content


def _load_protocol(
    repo_root: Path,
) -> Phase5OperationResolverProtocolV2:
    protocol = Phase5OperationResolverProtocolV2.model_validate_json(
        _verified_bytes(repo_root / _PROTOCOL_PATH, _PROTOCOL_SHA256)
    )

    receipt = Phase5OperationResolverProtocolFreezeReceiptV2.model_validate_json(
        _verified_bytes(repo_root / _FREEZE_PATH, _FREEZE_SHA256)
    )

    if receipt.protocol_sha256 != _PROTOCOL_SHA256:
        raise ValueError("resolver freeze receipt does not bind the expected protocol")

    if not receipt.protocol_frozen:
        raise ValueError("resolver protocol is not frozen")

    return protocol


def _matches_expectation(
    result: OperationResolution,
    expected_status: str,
    expected_operation_id: str | None,
) -> bool:
    if result.status.value != expected_status:
        return False

    if expected_status == ResolutionStatus.RESOLVED.value:
        return result.operation_ids == (expected_operation_id,)

    return True


def _is_false_confident_resolution(
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


def _acceptance_failures(
    *,
    protocol: Phase5OperationResolverProtocolV2,
    mismatch_count: int,
    false_confident_count: int,
    nondeterministic_count: int,
    resolved_count: int,
) -> tuple[str, ...]:
    failures: list[str] = []
    acceptance = protocol.acceptance

    if mismatch_count != 0:
        failures.append("frozen_fixture_expectation_mismatch")

    if false_confident_count > acceptance.false_confident_resolution_tolerance:
        failures.append("false_confident_resolution_tolerance_exceeded")

    if nondeterministic_count > acceptance.nondeterministic_fixture_tolerance:
        failures.append("nondeterministic_fixture_tolerance_exceeded")

    if resolved_count < acceptance.minimum_resolved_fixture_count:
        failures.append("minimum_resolved_fixture_count_not_met")

    return tuple(failures)


def build_phase5_operation_resolver_characterization(
    repo_root: Path,
) -> Phase5OperationResolverCharacterizationReport:
    """Execute only the fixed offline resolver characterization."""

    protocol = _load_protocol(repo_root)
    catalog = load_runtime_operation_catalog(repo_root)
    resolver = DeterministicOperationResolver(catalog)

    observations: list[ResolverFixtureObservation] = []

    for fixture in protocol.fixtures:
        repeats = tuple(
            resolver.resolve(fixture.query)
            for _ in range(protocol.acceptance.deterministic_repeat_count)
        )

        deterministic = all(result == repeats[0] for result in repeats[1:])
        observed = repeats[0]
        matched = _matches_expectation(
            observed,
            fixture.expected_status,
            fixture.expected_operation_id,
        )
        false_confident = _is_false_confident_resolution(
            observed,
            fixture.expected_status,
            fixture.expected_operation_id,
        )

        observations.append(
            ResolverFixtureObservation(
                fixture_id=fixture.fixture_id,
                expected_status=fixture.expected_status,
                expected_operation_id=fixture.expected_operation_id,
                observed_status=observed.status,
                observed_operation_ids=observed.operation_ids,
                expectation_matched=matched,
                false_confident_resolution=false_confident,
                deterministic_across_repeats=deterministic,
            )
        )

    ordered = tuple(sorted(observations, key=lambda item: item.fixture_id))
    resolved_count = sum(
        item.observed_status is ResolutionStatus.RESOLVED for item in ordered
    )
    ambiguous_count = sum(
        item.observed_status is ResolutionStatus.AMBIGUOUS for item in ordered
    )
    unresolved_count = sum(
        item.observed_status is ResolutionStatus.UNRESOLVED for item in ordered
    )
    mismatch_count = sum(not item.expectation_matched for item in ordered)
    false_confident_count = sum(
        item.false_confident_resolution for item in ordered
    )
    nondeterministic_count = sum(
        not item.deterministic_across_repeats for item in ordered
    )

    failures = _acceptance_failures(
        protocol=protocol,
        mismatch_count=mismatch_count,
        false_confident_count=false_confident_count,
        nondeterministic_count=nondeterministic_count,
        resolved_count=resolved_count,
    )

    return Phase5OperationResolverCharacterizationReport(
        catalog_operation_count=resolver.operation_count,
        resolved_fixture_count=resolved_count,
        ambiguous_fixture_count=ambiguous_count,
        unresolved_fixture_count=unresolved_count,
        expectation_mismatch_count=mismatch_count,
        false_confident_resolution_count=false_confident_count,
        nondeterministic_fixture_count=nondeterministic_count,
        resolution_coverage=resolved_count / len(protocol.fixtures),
        observations=ordered,
        acceptance_passed=len(failures) == 0,
        acceptance_failures=failures,
    )


def materialize_phase5_operation_resolver_characterization(
    repo_root: Path,
) -> tuple[Phase5OperationResolverCharacterizationReport, str]:
    report = build_phase5_operation_resolver_characterization(repo_root)
    digest = write_json_with_sha256(repo_root / _OUTPUT_PATH, report)
    return report, digest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report, digest = materialize_phase5_operation_resolver_characterization(repo_root)

    print(f"PHASE5_OPERATION_RESOLVER_CHARACTERIZATION_SHA256={digest}")
    print(f"PHASE5_OPERATION_RESOLVER_CATALOG_COUNT={report.catalog_operation_count}")
    print(f"PHASE5_OPERATION_RESOLVER_RESOLVED={report.resolved_fixture_count}/10")
    print(f"PHASE5_OPERATION_RESOLVER_AMBIGUOUS={report.ambiguous_fixture_count}/10")
    print(f"PHASE5_OPERATION_RESOLVER_UNRESOLVED={report.unresolved_fixture_count}/10")
    print(
        "PHASE5_OPERATION_RESOLVER_FALSE_CONFIDENT="
        f"{report.false_confident_resolution_count}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_NONDETERMINISTIC="
        f"{report.nondeterministic_fixture_count}"
    )
    print(
        "PHASE5_OPERATION_RESOLVER_ACCEPTANCE_PASSED="
        f"{str(report.acceptance_passed).lower()}"
    )

    for failure in report.acceptance_failures:
        print(f"PHASE5_OPERATION_RESOLVER_ACCEPTANCE_FAILURE={failure}")

    print("PHASE5_RETRIEVAL_CONFIGURATION_SELECTED=false")
    print("PHASE5_RUNTIME_RETRIEVER_CHANGED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")

    if not report.acceptance_passed:
        raise SystemExit("Phase 5 operation resolver acceptance failed")


if __name__ == "__main__":
    main()
