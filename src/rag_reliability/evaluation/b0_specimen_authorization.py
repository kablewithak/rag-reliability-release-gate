"""Build and freeze the exact G5M B0 specimen and execution authorization."""

from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import subprocess
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from rag_reliability.contracts.base import ContractModel
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.b0_authorization_models import (
    B0AuthorizationError,
    B0FileBinding,
    B0PackageVersion,
    Phase5B0EnvironmentReferenceV1,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ExecutionSlotV1,
    Phase5B0SpecimenV1,
    model_sha256,
    stable_model_bytes,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    B0Role,
    load_phase5_b0_runtime_projection,
)

_SPECIMEN_PATH = Path("artifacts/development/phase5_b0_specimen_v1.json")
_AUTHORIZATION_PATH = Path(
    "artifacts/development/phase5_b0_execution_authorization_v1.json"
)
_RAW_FIXTURE_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_replay_fixture_v1.json"
)
_COVERAGE_PATH = Path(
    "artifacts/development/phase5_b0_replay_fixture_coverage_v1.json"
)

_EXPECTED_FIXTURE_SHA256 = (
    "6755a24c0a859e43b70b4c8b0ec5fbc08540321db14989ab4ba330003d6da69a"
)
_EXPECTED_COVERAGE_SHA256 = (
    "7a1c1de6b848e040cd64d9ffa59aadac6053554514bb97892c7c8aff8328d944"
)
_EXPECTED_RUNTIME_CONFIGURATION_ID = (
    "7399c9ef7cd6612eb8fc363602e9c45c74ca691acde257aa40d07cc4135642a2"
)

_EXPECTED_GOVERNANCE_BINDINGS: tuple[tuple[str, str], ...] = (
    (
        "artifacts/development/phase5_baseline_protocol_v1.json",
        "20637e8eaa598224c33fe83d223fcc5d031d2bfa577299c8cdff4ccfceb6cc19",
    ),
    (
        "artifacts/development/phase5_baseline_protocol_freeze_v1.json",
        "a92845181c9fcd3c69b84a191f1288f4391431cae8f82fe6c520b0b2a07bf434",
    ),
    (
        "artifacts/development/phase5_b0_replay_fixture_protocol_v1.json",
        "c39ddce45a8c1204e596740061943c5f1da370897f8522a0b1f30b75b17a200b",
    ),
    (
        "artifacts/development/phase5_b0_replay_fixture_protocol_freeze_v1.json",
        "91f5bff1a1fe23308c26d00db0ba23d3146d9f1098361f40e688dc707e0008f3",
    ),
    (
        "artifacts/development/phase5_b0_replay_fixture_coverage_v1.json",
        _EXPECTED_COVERAGE_SHA256,
    ),
    (
        "artifacts/development/phase5_g5k_runtime_qualification_v1.json",
        "678dcb0d6453e11cd8e2b9c71153ed8337d5b8a26fcd36d732d6e8eb05dcbe71",
    ),
    (
        "artifacts/development/phase5_baseline_readiness_v1.json",
        "23e8957bb8aad66d6a2bdfcaeac9332ca609c2b293927dbc2fbaddd05bb2d38a",
    ),
    (
        "artifacts/development/phase5_measurement_instrument_freeze_v2.json",
        "6249eb30e9c5986bba55b8d5adba22e62ae4df712c08b4e950b544962a19c932",
    ),
    (
        "datasets/chunk_manifests/phase3d_chunk_manifest_v1.json",
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd",
    ),
    (
        "artifacts/development/phase4c_development_cases_v1.json",
        "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835",
    ),
    (
        "artifacts/development/phase4c_development_case_freeze_v1.json",
        "6deecc31195f3acefb0a6a47a650bf20e4f7606bac9131ff882126504dfbc1bc",
    ),
    (
        "artifacts/development/phase4c_tuning_cases_v1.json",
        "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28",
    ),
    (
        "artifacts/development/phase4c_tuning_case_freeze_v1.json",
        "ef0edfee6a71a7f294c22dcc17d9ecb657b200a100175a7ccd2c709a1e3f97f6",
    ),
)

_RUNTIME_SOURCE_PATHS = (
    "pyproject.toml",
    "src/rag_reliability/config/identity.py",
    "src/rag_reliability/contracts/interfaces.py",
    "src/rag_reliability/contracts/runtime.py",
    "src/rag_reliability/contracts/tracing.py",
    "src/rag_reliability/corpus/chunked.py",
    "src/rag_reliability/corpus/chunking.py",
    "src/rag_reliability/corpus/models.py",
    "src/rag_reliability/runtime/citations.py",
    "src/rag_reliability/runtime/context.py",
    "src/rag_reliability/runtime/errors.py",
    "src/rag_reliability/runtime/filtering.py",
    "src/rag_reliability/runtime/models.py",
    "src/rag_reliability/runtime/operation_aware_ranking.py",
    "src/rag_reliability/runtime/operation_aware_rrf_retriever.py",
    "src/rag_reliability/runtime/operation_catalog.py",
    "src/rag_reliability/runtime/operation_resolution.py",
    "src/rag_reliability/runtime/pipeline.py",
    "src/rag_reliability/runtime/provider.py",
    "src/rag_reliability/runtime/retrieval.py",
)

_ORCHESTRATION_SOURCE_PATHS = (
    "src/rag_reliability/evaluation/b0_authorization_models.py",
    "src/rag_reliability/evaluation/b0_execution_preflight.py",
    "src/rag_reliability/evaluation/b0_replay_fixture_materializer.py",
    "src/rag_reliability/evaluation/b0_runtime_projection.py",
    "src/rag_reliability/evaluation/b0_specimen_authorization.py",
)

_EVALUATOR_SOURCE_BINDINGS: tuple[tuple[str, str], ...] = (
    (
        "src/rag_reliability/evaluation/measurement_instrument.py",
        "72a718ef8b282c1c2d3e4e1d143222addcca777bd8ee159f51013a8a231a9a45",
    ),
    (
        "src/rag_reliability/evaluation/measurement_scoring.py",
        "0e0e6a334bf1b904fcf67db0852fd23c3cf57f0fd01f53c3e538763a2f59281d",
    ),
    (
        "src/rag_reliability/evaluation/measurement_aggregation.py",
        "62fce6d52291ec123be9880ae9145b2fff8408ac53c9b912d011b005102a6927",
    ),
)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def verified_sidecar_sha256(
    repo_root: Path,
    relative_path: str | Path,
    *,
    expected_sha256: str | None = None,
) -> str:
    path = repo_root / relative_path
    content = path.read_bytes()
    digest = sha256_bytes(content)

    if expected_sha256 is not None and digest != expected_sha256:
        raise B0AuthorizationError(
            f"frozen artifact hash mismatch: {relative_path}"
        )

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{digest}  {path.name}"

    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise B0AuthorizationError(f"SHA sidecar mismatch: {relative_path}")

    return digest


def file_binding(repo_root: Path, relative_path: str) -> B0FileBinding:
    return B0FileBinding(
        path=relative_path,
        sha256=sha256_bytes((repo_root / relative_path).read_bytes()),
    )


def fixed_file_binding(
    repo_root: Path,
    relative_path: str,
    expected_sha256: str,
) -> B0FileBinding:
    observed = sha256_bytes((repo_root / relative_path).read_bytes())
    if observed != expected_sha256:
        raise B0AuthorizationError(
            f"source binding drifted: {relative_path}"
        )
    return B0FileBinding(path=relative_path, sha256=observed)


def git_output(repo_root: Path, *args: str) -> str:
    process = subprocess.run(
        ("git", *args),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout.strip()


def require_clean_worktree(repo_root: Path) -> None:
    status = git_output(
        repo_root,
        "status",
        "--porcelain",
        "--untracked-files=normal",
    )
    if status:
        raise B0AuthorizationError(
            "G5M authorization requires a clean worktree; "
            "commit implementation changes before authorizing"
        )


def _total_physical_memory_bytes() -> int | None:
    if os.name == "nt":
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(MemoryStatusEx)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        fn = kernel32.GlobalMemoryStatusEx
        fn.argtypes = [ctypes.POINTER(MemoryStatusEx)]
        fn.restype = ctypes.c_int
        if not fn(ctypes.byref(status)):
            return None
        return int(status.ullTotalPhys)

    sysconf = getattr(os, "sysconf", None)
    if sysconf is None:
        return None

    try:
        page_size = int(sysconf("SC_PAGE_SIZE"))
        page_count = int(sysconf("SC_PHYS_PAGES"))
    except (OSError, ValueError):
        return None

    if page_size <= 0 or page_count <= 0:
        return None
    return page_size * page_count


def _package_version(distribution: str) -> B0PackageVersion:
    try:
        observed = version(distribution)
    except PackageNotFoundError as exc:
        raise B0AuthorizationError(
            f"required runtime package is not installed: {distribution}"
        ) from exc
    return B0PackageVersion(distribution=distribution, version=observed)


def capture_phase5_b0_environment() -> Phase5B0EnvironmentReferenceV1:
    clock = time.get_clock_info("perf_counter")
    logical_cpu_count = os.cpu_count()
    if logical_cpu_count is None or logical_cpu_count < 1:
        raise B0AuthorizationError("logical CPU count is unavailable")

    return Phase5B0EnvironmentReferenceV1(
        os_system=platform.system(),
        os_release=platform.release(),
        os_version=platform.version(),
        machine_architecture=platform.machine(),
        processor_identifier=platform.processor(),
        python_implementation=platform.python_implementation(),
        python_version=platform.python_version(),
        python_build=platform.python_build(),
        logical_cpu_count=logical_cpu_count,
        total_physical_memory_bytes=_total_physical_memory_bytes(),
        perf_counter_implementation=clock.implementation,
        perf_counter_resolution_seconds=clock.resolution,
        perf_counter_monotonic=True,
        runtime_packages=(
            _package_version("pydantic"),
            _package_version("PyYAML"),
        ),
    )


def load_coverage(repo_root: Path) -> Phase5B0ReplayFixtureCoverageV1:
    verified_sidecar_sha256(
        repo_root,
        _COVERAGE_PATH,
        expected_sha256=_EXPECTED_COVERAGE_SHA256,
    )
    coverage = Phase5B0ReplayFixtureCoverageV1.model_validate_json(
        (repo_root / _COVERAGE_PATH).read_bytes()
    )

    expected = (
        coverage.materialization_decision == "PASS",
        coverage.authorized_case_count == 42,
        coverage.provider_reaching_case_count == 42,
        coverage.pre_provider_refusal_case_count == 0,
        coverage.unexpected_prefix_error_count == 0,
        coverage.fixture_entry_count == 42,
        coverage.replay_fixture_sha256 == _EXPECTED_FIXTURE_SHA256,
        coverage.runtime_configuration_id == _EXPECTED_RUNTIME_CONFIGURATION_ID,
        not coverage.baseline_execution_authorized,
        not coverage.b0_executed,
        not coverage.held_out_outcomes_exposed,
    )
    if not all(expected):
        raise B0AuthorizationError("B0 replay coverage is not authorization-ready")
    return coverage


def load_raw_fixture(repo_root: Path) -> Phase5B0ReplayFixtureV1:
    verified_sidecar_sha256(
        repo_root,
        _RAW_FIXTURE_PATH,
        expected_sha256=_EXPECTED_FIXTURE_SHA256,
    )
    fixture = Phase5B0ReplayFixtureV1.model_validate_json(
        (repo_root / _RAW_FIXTURE_PATH).read_bytes()
    )
    if len(fixture.entries) != 42:
        raise B0AuthorizationError("B0 replay fixture must contain 42 entries")
    return fixture


def verify_fixture_coverage_alignment(
    coverage: Phase5B0ReplayFixtureCoverageV1,
    fixture: Phase5B0ReplayFixtureV1,
) -> None:
    coverage_hashes = {
        case.fixture_key_sha256
        for case in coverage.cases
        if case.fixture_key_sha256 is not None
    }
    fixture_hashes = {sha256_text(entry.query) for entry in fixture.entries}
    if coverage_hashes != fixture_hashes:
        raise B0AuthorizationError(
            "raw replay fixture exact query keys do not match coverage receipt"
        )


def _role_by_case(
    repo_root: Path,
) -> tuple[tuple[str, B0Role, str], ...]:
    projection = load_phase5_b0_runtime_projection(repo_root)
    return tuple(
        (case.case_id, projection.development.role, case.query)
        for case in projection.development.cases
    ) + tuple(
        (case.case_id, projection.tuning.role, case.query)
        for case in projection.tuning.cases
    )


def build_execution_slots(
    repo_root: Path,
    coverage: Phase5B0ReplayFixtureCoverageV1,
) -> tuple[Phase5B0ExecutionSlotV1, ...]:
    coverage_by_case = {case.case_id: case for case in coverage.cases}
    ordered = _role_by_case(repo_root)
    slots: list[Phase5B0ExecutionSlotV1] = []

    for arm in ("primary", "replication"):
        for ordinal, (case_id, role, query) in enumerate(ordered, start=1):
            record = coverage_by_case.get(case_id)
            if record is None:
                raise B0AuthorizationError(
                    f"coverage missing authorized case: {case_id}"
                )
            query_sha256 = sha256_text(query)
            if record.query_sha256 != query_sha256:
                raise B0AuthorizationError(
                    f"coverage query digest drifted: {case_id}"
                )
            if record.fixture_key_sha256 != query_sha256:
                raise B0AuthorizationError(
                    f"fixture key digest drifted: {case_id}"
                )
            slots.append(
                Phase5B0ExecutionSlotV1(
                    slot_id=f"{arm}:{case_id}",
                    arm=arm,
                    ordinal=ordinal,
                    case_id=case_id,
                    role=role,
                    query_sha256=query_sha256,
                    fixture_key_sha256=query_sha256,
                )
            )
    return tuple(slots)


def _governance_bindings(repo_root: Path) -> tuple[B0FileBinding, ...]:
    return tuple(
        B0FileBinding(
            path=path,
            sha256=verified_sidecar_sha256(
                repo_root,
                path,
                expected_sha256=expected,
            ),
        )
        for path, expected in _EXPECTED_GOVERNANCE_BINDINGS
    )


def build_phase5_b0_specimen_and_authorization(
    repo_root: Path,
    *,
    require_clean_tracked_worktree: bool,
) -> tuple[Phase5B0SpecimenV1, Phase5B0ExecutionAuthorizationV1]:
    repo_root = repo_root.resolve()
    if require_clean_tracked_worktree:
        require_clean_worktree(repo_root)

    coverage = load_coverage(repo_root)
    fixture = load_raw_fixture(repo_root)
    verify_fixture_coverage_alignment(coverage, fixture)

    evaluator_bindings = tuple(
        fixed_file_binding(repo_root, path, expected)
        for path, expected in _EVALUATOR_SOURCE_BINDINGS
    )
    governance_bindings = _governance_bindings(repo_root)
    environment = capture_phase5_b0_environment()
    ordered = _role_by_case(repo_root)

    specimen = Phase5B0SpecimenV1(
        authorization_source_commit_sha=git_output(repo_root, "rev-parse", "HEAD"),
        authorization_source_branch=git_output(
            repo_root,
            "branch",
            "--show-current",
        ),
        runtime_configuration_id=_EXPECTED_RUNTIME_CONFIGURATION_ID,
        replay_fixture_sha256=_EXPECTED_FIXTURE_SHA256,
        fixture_coverage_sha256=_EXPECTED_COVERAGE_SHA256,
        runtime_source_bindings=tuple(
            file_binding(repo_root, path)
            for path in sorted(_RUNTIME_SOURCE_PATHS)
        ),
        orchestration_source_bindings=tuple(
            file_binding(repo_root, path)
            for path in sorted(_ORCHESTRATION_SOURCE_PATHS)
        ),
        evaluator_source_bindings=evaluator_bindings,
        governance_artifact_bindings=governance_bindings,
        environment=environment,
        environment_sha256=model_sha256(environment),
        case_ids_in_execution_order=tuple(case_id for case_id, _role, _query in ordered),
    )

    authorization = Phase5B0ExecutionAuthorizationV1(
        specimen_sha256=model_sha256(specimen),
        supersedes_baseline_readiness_v1_sha256=(
            "23e8957bb8aad66d6a2bdfcaeac9332ca609c2b293927dbc2fbaddd05bb2d38a"
        ),
        replay_fixture_sha256=_EXPECTED_FIXTURE_SHA256,
        fixture_coverage_sha256=_EXPECTED_COVERAGE_SHA256,
        runtime_configuration_id=_EXPECTED_RUNTIME_CONFIGURATION_ID,
        slots=build_execution_slots(repo_root, coverage),
    )
    return specimen, authorization


def _write_immutable_model(path: Path, value: ContractModel) -> str:
    expected_bytes = stable_model_bytes(value)
    expected_sha256 = sha256_bytes(expected_bytes)

    if path.exists():
        if path.read_bytes() != expected_bytes:
            raise B0AuthorizationError(
                f"refusing to overwrite different immutable artifact: {path}"
            )
        sidecar = path.with_suffix(path.suffix + ".sha256")
        if sidecar.read_text(encoding="utf-8").strip() != (
            f"{expected_sha256}  {path.name}"
        ):
            raise B0AuthorizationError(
                f"immutable artifact sidecar mismatch: {path}"
            )
        return expected_sha256

    return write_json_with_sha256(path, value)


def materialize_phase5_b0_specimen_and_authorization(
    repo_root: Path,
) -> tuple[Phase5B0SpecimenV1, str, Phase5B0ExecutionAuthorizationV1, str]:
    specimen, authorization = build_phase5_b0_specimen_and_authorization(
        repo_root,
        require_clean_tracked_worktree=True,
    )
    specimen_sha256 = _write_immutable_model(repo_root / _SPECIMEN_PATH, specimen)
    if specimen_sha256 != authorization.specimen_sha256:
        raise B0AuthorizationError(
            "written specimen SHA does not match authorization"
        )
    authorization_sha256 = _write_immutable_model(
        repo_root / _AUTHORIZATION_PATH,
        authorization,
    )
    return specimen, specimen_sha256, authorization, authorization_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    specimen, specimen_sha, authorization, authorization_sha = (
        materialize_phase5_b0_specimen_and_authorization(repo_root)
    )

    print(f"PHASE5_B0_SPECIMEN_SHA256={specimen_sha}")
    print(f"PHASE5_B0_EXECUTION_AUTHORIZATION_SHA256={authorization_sha}")
    print(
        "PHASE5_B0_AUTHORIZATION_SOURCE_COMMIT="
        f"{specimen.authorization_source_commit_sha}"
    )
    print(f"PHASE5_B0_ENVIRONMENT_SHA256={specimen.environment_sha256}")
    print(f"PHASE5_B0_REPLAY_FIXTURE_SHA256={specimen.replay_fixture_sha256}")
    print(f"PHASE5_B0_AUTHORIZED_CASES={authorization.authorized_case_count}")
    print(f"PHASE5_B0_PRIMARY_SLOTS={authorization.primary_slot_count}")
    print(f"PHASE5_B0_REPLICATION_SLOTS={authorization.replication_slot_count}")
    print(f"PHASE5_B0_MAXIMUM_CASE_STARTS={authorization.maximum_total_case_starts}")
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(authorization.baseline_execution_authorized).lower()}"
    )
    print(f"PHASE5_B0_EXECUTED={str(authorization.b0_executed).lower()}")
    print(
        "PHASE5_B0_LIVE_PROVIDER_CALLS_AUTHORIZED="
        f"{authorization.live_provider_calls_authorized}"
    )
    print(
        "PHASE5_B0_PROTECTED_EXECUTION_AUTHORIZED="
        f"{str(authorization.protected_case_execution_authorized).lower()}"
    )


if __name__ == "__main__":
    main()
