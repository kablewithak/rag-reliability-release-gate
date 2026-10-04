"""Execute and reconcile exactly one authorized Phase 5 G5N B0 primary batch.

The execution boundary accepts only runtime `(case_id, query)` projections and the
frozen deterministic replay fixture. Evaluator-owned fields are not loaded by the
runner. A primary slot is permanently consumed when its start record is durably
appended. Existing execution evidence always switches the top-level entry point
into reconciliation-only mode; it never resumes or replaces consumed evidence.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Literal, Protocol, Self

from pydantic import Field, model_validator

from rag_reliability.config.identity import RuntimeConfiguration
from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import RuntimeErrorCode, TraceStage
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import ErrorOutcome
from rag_reliability.evaluation.b0_authorization_models import (
    B0AuthorizationError,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ExecutionSlotV1,
    Phase5B0SpecimenV1,
    stable_model_bytes,
)
from rag_reliability.evaluation.b0_execution_preflight import (
    load_frozen_specimen_and_authorization,
    preflight_execution_slot_with_objects,
    preflight_specimen,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
    _b0_runtime_config,
    _load_frozen_controls,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    B0Role,
    Phase5B0RuntimeProjectionV1,
    load_phase5_b0_runtime_projection,
)
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
)
from rag_reliability.runtime.citations import ExactCitationValidator
from rag_reliability.runtime.context import BoundedContextBuilder
from rag_reliability.runtime.filtering import CurrentGithubRestSourcePolicyFilter
from rag_reliability.runtime.models import PipelineExecution
from rag_reliability.runtime.operation_aware_rrf_retriever import (
    OperationAwareRrfRetriever,
)
from rag_reliability.runtime.pipeline import DeterministicRagPipeline
from rag_reliability.runtime.provider import ReplayProvider

_SPECIMEN_SHA256: Sha256 = (
    "5ce922230e8a09041c7ea6248ee0f4acf412182ee062c6a16a15b65668485986"
)
_AUTHORIZATION_SHA256: Sha256 = (
    "825d305fcceb92e93911f9278fceef0d0eb251d4309c3b701d9af167c42fc1b8"
)
_RUNTIME_CONFIGURATION_ID: Sha256 = (
    "7399c9ef7cd6612eb8fc363602e9c45c74ca691acde257aa40d07cc4135642a2"
)
_REPLAY_FIXTURE_SHA256: Sha256 = (
    "6755a24c0a859e43b70b4c8b0ec5fbc08540321db14989ab4ba330003d6da69a"
)
_ENVIRONMENT_SHA256: Sha256 = (
    "ef296bb60d581b5e71b5ba8b0ae26539d98c6dd86be03ce1a17e1130bec4e78d"
)

_SPECIMEN_PATH = Path("artifacts/development/phase5_b0_specimen_v1.json")
_AUTHORIZATION_PATH = Path(
    "artifacts/development/phase5_b0_execution_authorization_v1.json"
)

_START_JOURNAL_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_primary_start_journal_v1.jsonl"
)
_TERMINAL_JOURNAL_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_primary_terminal_journal_v1.jsonl"
)
_RAW_BATCH_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_primary_execution_v1.json"
)
_PUBLIC_RECEIPT_PATH = Path(
    "artifacts/development/phase5_b0_primary_execution_receipt_v1.json"
)

_RUNNER_RELATIVE_PATH = (
    "src/rag_reliability/evaluation/b0_primary_execution.py"
)
_INDEX_LOADER_RELATIVE_PATH = (
    "src/rag_reliability/evaluation/retrieval_characterization.py"
)

PrimaryBatchDecision = Literal["COMPLETE", "STOPPED", "INTERRUPTED"]


class PrimaryPipeline(Protocol):
    """Minimal runtime-only execution seam used by the G5N runner."""

    async def run(self, case: RuntimeCaseInput) -> PipelineExecution:
        """Execute one runtime-projected case."""


class Phase5B0PrimaryStartRecordV1(ContractModel):
    """Durable evidence that an authorized primary slot was consumed."""

    record_version: Literal[
        "phase5-b0-primary-start-record-v1"
    ] = "phase5-b0-primary-start-record-v1"

    slot_id: NonEmptyStr
    ordinal: int = Field(ge=1, le=42)
    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256

    execution_commit_sha: NonEmptyStr
    runner_source_sha256: Sha256
    index_loader_source_sha256: Sha256


class Phase5B0PrimaryExecutionRecordV1(ContractModel):
    """One terminal raw execution record retained only in the evidence vault."""

    record_version: Literal[
        "phase5-b0-primary-execution-record-v1"
    ] = "phase5-b0-primary-execution-record-v1"

    slot_id: NonEmptyStr
    ordinal: int = Field(ge=1, le=42)
    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256
    execution: PipelineExecution

    @model_validator(mode="after")
    def validate_execution_binding(self) -> Self:
        if self.execution.trace.case_id != self.case_id:
            raise ValueError("execution trace case_id does not match slot case_id")
        return self


class Phase5B0PrimaryUnreconciledStartV1(ContractModel):
    """Metadata-safe record of a consumed start with no terminal execution."""

    slot_id: NonEmptyStr
    ordinal: int = Field(ge=1, le=42)
    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256


class Phase5B0PrimaryPublicCaseReceiptV1(ContractModel):
    """Metadata-safe terminal case custody without query/answer/context text."""

    case_id: NonEmptyStr
    slot_id: NonEmptyStr
    ordinal: int = Field(ge=1, le=42)
    role: B0Role
    query_sha256: Sha256

    outcome_status: Literal["answer", "refusal", "error"]
    runtime_error_code: RuntimeErrorCode | None = None
    terminal_trace_stage: TraceStage
    trace_event_count: int = Field(ge=1)

    execution_sha256: Sha256
    trace_sha256: Sha256

    @model_validator(mode="after")
    def validate_error_code(self) -> Self:
        if self.outcome_status == "error":
            if self.runtime_error_code is None:
                raise ValueError("error receipt requires runtime_error_code")
        elif self.runtime_error_code is not None:
            raise ValueError("non-error receipt cannot carry runtime_error_code")
        return self


class Phase5B0PrimaryRawBatchV1(ContractModel):
    """Internal raw G5N custody; may represent interrupted consumed evidence."""

    batch_version: Literal[
        "phase5-b0-primary-execution-v1"
    ] = "phase5-b0-primary-execution-v1"

    specimen_sha256: Sha256 = _SPECIMEN_SHA256
    authorization_sha256: Sha256 = _AUTHORIZATION_SHA256
    runtime_configuration_id: Sha256 = _RUNTIME_CONFIGURATION_ID
    replay_fixture_sha256: Sha256 = _REPLAY_FIXTURE_SHA256
    environment_sha256: Sha256 = _ENVIRONMENT_SHA256

    execution_commit_sha: NonEmptyStr
    runner_source_sha256: Sha256
    index_loader_source_sha256: Sha256

    arm: Literal["primary"] = "primary"
    authorized_case_count: Literal[42] = 42
    authorized_primary_slot_count: Literal[42] = 42

    started_slot_count: int = Field(ge=1, le=42)
    terminal_record_count: int = Field(ge=0, le=42)
    unreconciled_started_slot_count: int = Field(ge=0, le=42)

    records: tuple[Phase5B0PrimaryExecutionRecordV1, ...] = Field(
        default=(),
        max_length=42,
    )
    unreconciled_starts: tuple[
        Phase5B0PrimaryUnreconciledStartV1,
        ...,
    ] = Field(default=(), max_length=42)

    same_stage_failure_stop_count: Literal[2] = 2
    stop_triggered: bool
    stop_stage: TraceStage | None = None
    batch_decision: PrimaryBatchDecision
    batch_complete: bool

    evaluator_fields_used_by_runtime: Literal[False] = False
    live_provider_call_count: Literal[0] = 0
    protected_roles_accessed: Literal[False] = False
    selective_rerun_used: Literal[False] = False
    replacement_start_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_batch(self) -> Self:
        if self.terminal_record_count != len(self.records):
            raise ValueError("terminal record count does not reconcile")

        if self.unreconciled_started_slot_count != len(
            self.unreconciled_starts
        ):
            raise ValueError("unreconciled start count does not reconcile")

        if self.started_slot_count != (
            self.terminal_record_count
            + self.unreconciled_started_slot_count
        ):
            raise ValueError("started slot count does not reconcile")

        terminal_slots = tuple(record.slot_id for record in self.records)
        unreconciled_slots = tuple(
            record.slot_id for record in self.unreconciled_starts
        )
        all_slots = terminal_slots + unreconciled_slots

        if len(all_slots) != len(set(all_slots)):
            raise ValueError("primary raw batch contains duplicate slots")

        expected_complete = (
            self.started_slot_count == 42
            and self.terminal_record_count == 42
            and self.unreconciled_started_slot_count == 0
            and not self.stop_triggered
        )
        if self.batch_complete != expected_complete:
            raise ValueError("batch_complete does not reconcile")

        if self.batch_decision == "COMPLETE":
            if not expected_complete:
                raise ValueError("COMPLETE requires 42 reconciled terminal records")
        elif self.batch_decision == "STOPPED":
            if not self.stop_triggered:
                raise ValueError("STOPPED requires the typed stop rule")
            if self.unreconciled_started_slot_count != 0:
                raise ValueError("STOPPED cannot contain unreconciled starts")
        else:
            if self.stop_triggered or expected_complete:
                raise ValueError("INTERRUPTED decision does not reconcile")

        if self.stop_triggered != (self.stop_stage is not None):
            raise ValueError("stop stage must reconcile with stop_triggered")

        return self


class Phase5B0PrimaryExecutionReceiptV1(ContractModel):
    """Tracked public-safe custody receipt for the G5N primary batch."""

    receipt_version: Literal[
        "phase5-b0-primary-execution-receipt-v1"
    ] = "phase5-b0-primary-execution-receipt-v1"

    specimen_sha256: Sha256 = _SPECIMEN_SHA256
    authorization_sha256: Sha256 = _AUTHORIZATION_SHA256
    runtime_configuration_id: Sha256 = _RUNTIME_CONFIGURATION_ID
    replay_fixture_sha256: Sha256 = _REPLAY_FIXTURE_SHA256
    environment_sha256: Sha256 = _ENVIRONMENT_SHA256

    execution_commit_sha: NonEmptyStr
    runner_source_sha256: Sha256
    index_loader_source_sha256: Sha256

    raw_batch_relative_path: Literal[
        "evidence_vault/eval_reports/phase5_b0_primary_execution_v1.json"
    ] = "evidence_vault/eval_reports/phase5_b0_primary_execution_v1.json"

    raw_batch_sha256: Sha256
    start_journal_sha256: Sha256
    terminal_journal_present: bool
    terminal_journal_sha256: Sha256 | None = None

    authorized_case_count: Literal[42] = 42
    started_slot_count: int = Field(ge=1, le=42)
    terminal_record_count: int = Field(ge=0, le=42)
    unreconciled_started_slot_count: int = Field(ge=0, le=42)

    answer_count: int = Field(ge=0, le=42)
    refusal_count: int = Field(ge=0, le=42)
    error_count: int = Field(ge=0, le=42)

    cases: tuple[Phase5B0PrimaryPublicCaseReceiptV1, ...] = Field(
        default=(),
        max_length=42,
    )
    unreconciled_starts: tuple[
        Phase5B0PrimaryUnreconciledStartV1,
        ...,
    ] = Field(default=(), max_length=42)

    same_stage_failure_stop_count: Literal[2] = 2
    stop_triggered: bool
    stop_stage: TraceStage | None = None
    batch_decision: PrimaryBatchDecision
    primary_execution_complete: bool

    scoring_performed: Literal[False] = False
    evaluator_fields_used_by_runtime: Literal[False] = False
    live_provider_call_count: Literal[0] = 0
    protected_roles_accessed: Literal[False] = False
    selective_rerun_used: Literal[False] = False
    replacement_start_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    replication_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_receipt(self) -> Self:
        if self.terminal_record_count != len(self.cases):
            raise ValueError("receipt terminal count does not reconcile")

        if self.unreconciled_started_slot_count != len(
            self.unreconciled_starts
        ):
            raise ValueError("receipt unreconciled count does not reconcile")

        if self.started_slot_count != (
            self.terminal_record_count
            + self.unreconciled_started_slot_count
        ):
            raise ValueError("receipt started count does not reconcile")

        outcome_total = self.answer_count + self.refusal_count + self.error_count
        if outcome_total != self.terminal_record_count:
            raise ValueError("receipt outcome counts do not reconcile")

        case_ids = tuple(case.case_id for case in self.cases)
        slot_ids = tuple(case.slot_id for case in self.cases)
        unresolved_slot_ids = tuple(
            item.slot_id for item in self.unreconciled_starts
        )

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("receipt terminal case IDs must be unique")
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("receipt terminal slot IDs must be unique")
        if set(slot_ids) & set(unresolved_slot_ids):
            raise ValueError("terminal and unreconciled slots overlap")

        if self.terminal_journal_present != (
            self.terminal_journal_sha256 is not None
        ):
            raise ValueError("terminal journal presence does not reconcile")

        expected_complete = (
            self.started_slot_count == 42
            and self.terminal_record_count == 42
            and self.unreconciled_started_slot_count == 0
            and not self.stop_triggered
        )
        if self.primary_execution_complete != expected_complete:
            raise ValueError("primary execution completeness does not reconcile")

        if self.batch_decision == "COMPLETE":
            if not expected_complete:
                raise ValueError("COMPLETE receipt requires full reconciliation")
        elif self.batch_decision == "STOPPED":
            if not self.stop_triggered:
                raise ValueError("STOPPED receipt requires typed stop")
            if self.unreconciled_started_slot_count != 0:
                raise ValueError("STOPPED receipt cannot carry orphan starts")
        else:
            if self.stop_triggered or expected_complete:
                raise ValueError("INTERRUPTED receipt does not reconcile")

        if self.stop_triggered != (self.stop_stage is not None):
            raise ValueError("receipt stop stage does not reconcile")

        return self


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_model(value: ContractModel) -> str:
    return _sha256_bytes(stable_model_bytes(value))


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _stable_json_line(value: ContractModel) -> bytes:
    return (
        json.dumps(
            value.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _append_durable(
    path: Path,
    value: ContractModel,
    *,
    first: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if first else "ab"

    with path.open(mode) as handle:
        handle.write(_stable_json_line(value))
        handle.flush()
        os.fsync(handle.fileno())


def _execution_evidence_paths() -> tuple[Path, ...]:
    return (
        _START_JOURNAL_PATH,
        _TERMINAL_JOURNAL_PATH,
        _RAW_BATCH_PATH,
        _PUBLIC_RECEIPT_PATH,
        _RAW_BATCH_PATH.with_suffix(".json.sha256"),
        _PUBLIC_RECEIPT_PATH.with_suffix(".json.sha256"),
    )


def _existing_execution_evidence(repo_root: Path) -> tuple[str, ...]:
    return tuple(
        str(relative)
        for relative in _execution_evidence_paths()
        if (repo_root / relative).exists()
    )


def _require_fresh_execution_paths(repo_root: Path) -> None:
    existing = _existing_execution_evidence(repo_root)
    if existing:
        joined = ", ".join(existing)
        raise B0AuthorizationError(
            "G5N primary evidence path already exists; "
            f"execution cannot continue or rerun: {joined}"
        )


def _verified_fixed_artifact(
    repo_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> None:
    path = repo_root / relative_path
    if _sha256_file(path) != expected_sha256:
        raise B0AuthorizationError(
            f"frozen G5N prerequisite drifted: {relative_path}"
        )

    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected = f"{expected_sha256}  {path.name}"
    if sidecar.read_text(encoding="utf-8").strip() != expected:
        raise B0AuthorizationError(
            f"frozen G5N prerequisite sidecar drifted: {relative_path}"
        )


def _write_durable_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _write_or_verify_immutable_model(
    path: Path,
    value: ContractModel,
) -> str:
    expected_bytes = stable_model_bytes(value)
    expected_sha256 = _sha256_bytes(expected_bytes)
    sidecar = path.with_suffix(path.suffix + ".sha256")
    expected_sidecar = f"{expected_sha256}  {path.name}\n".encode()

    if path.exists():
        if path.read_bytes() != expected_bytes:
            raise B0AuthorizationError(
                f"refusing to replace different G5N evidence artifact: {path}"
            )
    else:
        if sidecar.exists():
            raise B0AuthorizationError(
                f"orphan G5N evidence sidecar exists without artifact: {sidecar}"
            )
        _write_durable_bytes(path, expected_bytes)

    if sidecar.exists():
        if sidecar.read_bytes() != expected_sidecar:
            raise B0AuthorizationError(
                f"G5N evidence sidecar mismatch: {sidecar}"
            )
    else:
        _write_durable_bytes(sidecar, expected_sidecar)

    return expected_sha256


def build_phase5_b0_primary_pipeline(
    repo_root: Path,
    *,
    fixture: Phase5B0ReplayFixtureV1,
) -> tuple[RuntimeConfiguration, DeterministicRagPipeline]:
    """Build the exact authorized replay pipeline without executing a case."""

    protocol = _load_frozen_controls(repo_root)
    config = _b0_runtime_config(protocol)

    if config.configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("G5N runtime configuration identity drifted")

    documents, _evidence_ids = _load_indexed_documents(repo_root)

    pipeline = DeterministicRagPipeline(
        config=config,
        retriever=OperationAwareRrfRetriever(
            config=config.retrieval,
            documents=documents,
            repo_root=repo_root,
        ),
        source_filter=CurrentGithubRestSourcePolicyFilter(
            config=config.source_policy
        ),
        context_builder=BoundedContextBuilder(config=config.context),
        provider=ReplayProvider(
            config=config.provider,
            entries=fixture.entries,
        ),
        citation_validator=ExactCitationValidator(config=config.citation),
    )

    return config, pipeline


def _ordered_runtime_cases(
    projection: Phase5B0RuntimeProjectionV1,
) -> tuple[tuple[B0Role, RuntimeCaseInput], ...]:
    return tuple(
        (projection.development.role, case)
        for case in projection.development.cases
    ) + tuple(
        (projection.tuning.role, case)
        for case in projection.tuning.cases
    )


def _terminal_error_stage(
    execution: PipelineExecution,
) -> TraceStage | None:
    if not isinstance(execution.outcome, ErrorOutcome):
        return None

    if not execution.trace.events:
        raise B0AuthorizationError("error execution must contain a trace event")

    return execution.trace.events[-1].stage


def _public_case_receipt(
    record: Phase5B0PrimaryExecutionRecordV1,
) -> Phase5B0PrimaryPublicCaseReceiptV1:
    outcome = record.execution.outcome
    error_code = (
        outcome.error_code
        if isinstance(outcome, ErrorOutcome)
        else None
    )
    events = record.execution.trace.events

    if not events:
        raise B0AuthorizationError("terminal execution has no trace events")

    return Phase5B0PrimaryPublicCaseReceiptV1(
        case_id=record.case_id,
        slot_id=record.slot_id,
        ordinal=record.ordinal,
        role=record.role,
        query_sha256=record.query_sha256,
        outcome_status=outcome.status,
        runtime_error_code=error_code,
        terminal_trace_stage=events[-1].stage,
        trace_event_count=len(events),
        execution_sha256=_sha256_model(record.execution),
        trace_sha256=_sha256_model(record.execution.trace),
    )


def _unreconciled_start(
    record: Phase5B0PrimaryStartRecordV1,
) -> Phase5B0PrimaryUnreconciledStartV1:
    return Phase5B0PrimaryUnreconciledStartV1(
        slot_id=record.slot_id,
        ordinal=record.ordinal,
        case_id=record.case_id,
        role=record.role,
        query_sha256=record.query_sha256,
    )


def _read_start_journal(
    path: Path,
) -> tuple[Phase5B0PrimaryStartRecordV1, ...]:
    if not path.exists():
        raise B0AuthorizationError("primary start journal does not exist")

    lines = path.read_bytes().splitlines()
    if not lines:
        raise B0AuthorizationError("primary start journal is empty")

    return tuple(
        Phase5B0PrimaryStartRecordV1.model_validate_json(line)
        for line in lines
    )


def _read_terminal_journal(
    path: Path,
) -> tuple[Phase5B0PrimaryExecutionRecordV1, ...]:
    if not path.exists():
        return ()

    lines = path.read_bytes().splitlines()
    if not lines:
        raise B0AuthorizationError("primary terminal journal is empty")

    return tuple(
        Phase5B0PrimaryExecutionRecordV1.model_validate_json(line)
        for line in lines
    )


def _primary_slot_for_case(
    authorization: Phase5B0ExecutionAuthorizationV1,
    case_id: str,
) -> Phase5B0ExecutionSlotV1:
    matches = tuple(
        slot
        for slot in authorization.slots
        if slot.arm == "primary" and slot.case_id == case_id
    )
    if len(matches) != 1:
        raise B0AuthorizationError(
            f"exactly one primary authorization required for {case_id}"
        )
    return matches[0]


def _validate_start_journal(
    *,
    authorization: Phase5B0ExecutionAuthorizationV1,
    projection: Phase5B0RuntimeProjectionV1,
    starts: tuple[Phase5B0PrimaryStartRecordV1, ...],
) -> None:
    ordered = _ordered_runtime_cases(projection)
    if len(starts) > len(ordered):
        raise B0AuthorizationError("primary start journal exceeds 42 slots")

    first = starts[0]
    identity = (
        first.execution_commit_sha,
        first.runner_source_sha256,
        first.index_loader_source_sha256,
    )

    observed_slot_ids: set[str] = set()

    for index, start in enumerate(starts):
        role, case = ordered[index]
        slot = _primary_slot_for_case(authorization, case.case_id)
        expected_query_sha = _sha256_text(case.query)

        if start.slot_id in observed_slot_ids:
            raise B0AuthorizationError("primary start journal repeats a slot")

        observed_slot_ids.add(start.slot_id)

        if start.ordinal != index + 1:
            raise B0AuthorizationError("primary start journal order drifted")
        if start.slot_id != slot.slot_id:
            raise B0AuthorizationError("primary start slot binding drifted")
        if start.case_id != case.case_id:
            raise B0AuthorizationError("primary start case binding drifted")
        if start.role != role or start.role != slot.role:
            raise B0AuthorizationError("primary start role binding drifted")
        if start.query_sha256 != expected_query_sha:
            raise B0AuthorizationError("primary start query binding drifted")
        if start.query_sha256 != slot.query_sha256:
            raise B0AuthorizationError("primary authorization query drifted")

        current_identity = (
            start.execution_commit_sha,
            start.runner_source_sha256,
            start.index_loader_source_sha256,
        )
        if current_identity != identity:
            raise B0AuthorizationError("primary start execution identity drifted")


def _validate_terminal_journal(
    *,
    starts: tuple[Phase5B0PrimaryStartRecordV1, ...],
    terminals: tuple[Phase5B0PrimaryExecutionRecordV1, ...],
) -> None:
    if len(terminals) > len(starts):
        raise B0AuthorizationError(
            "primary terminal journal exceeds consumed starts"
        )

    for index, terminal in enumerate(terminals):
        start = starts[index]
        expected = (
            start.slot_id,
            start.ordinal,
            start.case_id,
            start.role,
            start.query_sha256,
        )
        observed = (
            terminal.slot_id,
            terminal.ordinal,
            terminal.case_id,
            terminal.role,
            terminal.query_sha256,
        )
        if observed != expected:
            raise B0AuthorizationError(
                "primary terminal journal is not a prefix of consumed starts"
            )


def _typed_stop_stage(
    terminals: tuple[Phase5B0PrimaryExecutionRecordV1, ...],
    stop_count: int,
) -> tuple[TraceStage | None, int | None]:
    counts: Counter[TraceStage] = Counter()

    for index, record in enumerate(terminals, start=1):
        stage = _terminal_error_stage(record.execution)
        if stage is None:
            continue

        counts[stage] += 1
        if counts[stage] >= stop_count:
            return stage, index

    return None, None


def reconcile_primary_journals_with_objects(
    *,
    authorization: Phase5B0ExecutionAuthorizationV1,
    projection: Phase5B0RuntimeProjectionV1,
    start_journal_path: Path,
    terminal_journal_path: Path,
) -> tuple[
    Phase5B0PrimaryRawBatchV1,
    Phase5B0PrimaryExecutionReceiptV1,
]:
    """Reconcile durable journals without executing or resuming any case."""

    starts = _read_start_journal(start_journal_path)
    terminals = _read_terminal_journal(terminal_journal_path)

    _validate_start_journal(
        authorization=authorization,
        projection=projection,
        starts=starts,
    )
    _validate_terminal_journal(starts=starts, terminals=terminals)

    stop_stage, stop_position = _typed_stop_stage(
        terminals,
        authorization.same_stage_failure_stop_count,
    )

    if stop_position is not None:
        if stop_position != len(terminals):
            raise B0AuthorizationError(
                "terminal records exist after the mandatory typed stop"
            )
        if len(starts) != len(terminals):
            raise B0AuthorizationError(
                "a slot was started after the mandatory typed stop"
            )

    unreconciled = tuple(
        _unreconciled_start(start)
        for start in starts[len(terminals):]
    )

    complete = (
        len(starts) == 42
        and len(terminals) == 42
        and not unreconciled
        and stop_stage is None
    )

    if complete:
        decision: PrimaryBatchDecision = "COMPLETE"
    elif stop_stage is not None:
        decision = "STOPPED"
    else:
        decision = "INTERRUPTED"

    first = starts[0]
    raw_batch = Phase5B0PrimaryRawBatchV1(
        execution_commit_sha=first.execution_commit_sha,
        runner_source_sha256=first.runner_source_sha256,
        index_loader_source_sha256=first.index_loader_source_sha256,
        started_slot_count=len(starts),
        terminal_record_count=len(terminals),
        unreconciled_started_slot_count=len(unreconciled),
        records=terminals,
        unreconciled_starts=unreconciled,
        stop_triggered=stop_stage is not None,
        stop_stage=stop_stage,
        batch_decision=decision,
        batch_complete=complete,
    )

    public_cases = tuple(_public_case_receipt(record) for record in terminals)
    answer_count = sum(
        record.execution.outcome.status == "answer"
        for record in terminals
    )
    refusal_count = sum(
        record.execution.outcome.status == "refusal"
        for record in terminals
    )
    error_count = sum(
        record.execution.outcome.status == "error"
        for record in terminals
    )

    terminal_present = terminal_journal_path.exists()
    terminal_sha = (
        _sha256_file(terminal_journal_path)
        if terminal_present
        else None
    )

    receipt = Phase5B0PrimaryExecutionReceiptV1(
        execution_commit_sha=first.execution_commit_sha,
        runner_source_sha256=first.runner_source_sha256,
        index_loader_source_sha256=first.index_loader_source_sha256,
        raw_batch_sha256=_sha256_model(raw_batch),
        start_journal_sha256=_sha256_file(start_journal_path),
        terminal_journal_present=terminal_present,
        terminal_journal_sha256=terminal_sha,
        started_slot_count=len(starts),
        terminal_record_count=len(terminals),
        unreconciled_started_slot_count=len(unreconciled),
        answer_count=answer_count,
        refusal_count=refusal_count,
        error_count=error_count,
        cases=public_cases,
        unreconciled_starts=unreconciled,
        stop_triggered=stop_stage is not None,
        stop_stage=stop_stage,
        batch_decision=decision,
        primary_execution_complete=complete,
    )

    return raw_batch, receipt


async def execute_primary_batch_with_objects(
    *,
    repo_root: Path,
    specimen: Phase5B0SpecimenV1,
    authorization: Phase5B0ExecutionAuthorizationV1,
    coverage: Phase5B0ReplayFixtureCoverageV1,
    fixture: Phase5B0ReplayFixtureV1,
    projection: Phase5B0RuntimeProjectionV1,
    pipeline: PrimaryPipeline,
    execution_commit_sha: str,
    runner_source_sha256: str,
    index_loader_source_sha256: str,
    start_journal_path: Path,
    terminal_journal_path: Path,
) -> tuple[
    Phase5B0PrimaryRawBatchV1,
    Phase5B0PrimaryExecutionReceiptV1,
]:
    """Execute fresh primary slots only; unexpected crashes remain journal evidence."""

    del repo_root

    if start_journal_path.exists() or terminal_journal_path.exists():
        raise B0AuthorizationError(
            "primary journals already exist; execution cannot resume or rerun"
        )

    if specimen.runtime_configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("specimen runtime configuration drifted")
    if authorization.runtime_configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("authorization runtime configuration drifted")

    started_slot_ids: set[str] = set()
    error_stages: Counter[TraceStage] = Counter()

    for role, case in _ordered_runtime_cases(projection):
        slot = preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="primary",
            case_id=case.case_id,
            role=role,
            query=case.query,
            started_slot_ids=started_slot_ids,
            primary_batch_valid_and_custodied=False,
        )

        start_record = Phase5B0PrimaryStartRecordV1(
            slot_id=slot.slot_id,
            ordinal=slot.ordinal,
            case_id=case.case_id,
            role=role,
            query_sha256=slot.query_sha256,
            execution_commit_sha=execution_commit_sha,
            runner_source_sha256=runner_source_sha256,
            index_loader_source_sha256=index_loader_source_sha256,
        )

        _append_durable(
            start_journal_path,
            start_record,
            first=not started_slot_ids,
        )
        started_slot_ids.add(slot.slot_id)

        execution = await pipeline.run(case)

        terminal_record = Phase5B0PrimaryExecutionRecordV1(
            slot_id=slot.slot_id,
            ordinal=slot.ordinal,
            case_id=case.case_id,
            role=role,
            query_sha256=slot.query_sha256,
            execution=execution,
        )

        _append_durable(
            terminal_journal_path,
            terminal_record,
            first=not terminal_journal_path.exists(),
        )

        error_stage = _terminal_error_stage(execution)
        if error_stage is not None:
            error_stages[error_stage] += 1
            if (
                error_stages[error_stage]
                >= authorization.same_stage_failure_stop_count
            ):
                break

    return reconcile_primary_journals_with_objects(
        authorization=authorization,
        projection=projection,
        start_journal_path=start_journal_path,
        terminal_journal_path=terminal_journal_path,
    )


def _verify_execution_order(
    specimen: Phase5B0SpecimenV1,
    projection: Phase5B0RuntimeProjectionV1,
) -> None:
    observed = tuple(
        case.case_id
        for _role, case in _ordered_runtime_cases(projection)
    )
    if specimen.case_ids_in_execution_order != observed:
        raise B0AuthorizationError("G5N execution order drifted from specimen")


def _verify_frozen_g5n_identities(
    repo_root: Path,
    specimen: Phase5B0SpecimenV1,
    authorization: Phase5B0ExecutionAuthorizationV1,
) -> None:
    _verified_fixed_artifact(
        repo_root,
        _SPECIMEN_PATH,
        _SPECIMEN_SHA256,
    )
    _verified_fixed_artifact(
        repo_root,
        _AUTHORIZATION_PATH,
        _AUTHORIZATION_SHA256,
    )

    if specimen.runtime_configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("frozen specimen runtime identity drifted")
    if specimen.replay_fixture_sha256 != _REPLAY_FIXTURE_SHA256:
        raise B0AuthorizationError("frozen specimen fixture identity drifted")
    if specimen.environment_sha256 != _ENVIRONMENT_SHA256:
        raise B0AuthorizationError("frozen specimen environment identity drifted")
    if authorization.runtime_configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("frozen authorization runtime identity drifted")
    if authorization.replay_fixture_sha256 != _REPLAY_FIXTURE_SHA256:
        raise B0AuthorizationError("frozen authorization fixture identity drifted")


def _load_recovery_objects(
    repo_root: Path,
) -> tuple[
    Phase5B0SpecimenV1,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0RuntimeProjectionV1,
]:
    specimen, authorization = load_frozen_specimen_and_authorization(repo_root)
    _verify_frozen_g5n_identities(repo_root, specimen, authorization)

    projection = load_phase5_b0_runtime_projection(repo_root)
    _verify_execution_order(specimen, projection)

    return specimen, authorization, projection


def freeze_existing_primary_custody(
    repo_root: Path,
) -> tuple[
    Phase5B0PrimaryRawBatchV1,
    str,
    Phase5B0PrimaryExecutionReceiptV1,
    str,
]:
    """Freeze existing journals only; never execute or resume a primary case."""

    repo_root = repo_root.resolve()
    _specimen, authorization, projection = _load_recovery_objects(repo_root)

    raw_batch, receipt = reconcile_primary_journals_with_objects(
        authorization=authorization,
        projection=projection,
        start_journal_path=repo_root / _START_JOURNAL_PATH,
        terminal_journal_path=repo_root / _TERMINAL_JOURNAL_PATH,
    )

    raw_sha256 = _write_or_verify_immutable_model(
        repo_root / _RAW_BATCH_PATH,
        raw_batch,
    )
    if raw_sha256 != receipt.raw_batch_sha256:
        raise B0AuthorizationError(
            "raw G5N batch SHA does not match public receipt"
        )

    receipt_sha256 = _write_or_verify_immutable_model(
        repo_root / _PUBLIC_RECEIPT_PATH,
        receipt,
    )

    return raw_batch, raw_sha256, receipt, receipt_sha256


async def execute_phase5_b0_primary(
    repo_root: Path,
) -> tuple[
    Phase5B0PrimaryRawBatchV1,
    str,
    Phase5B0PrimaryExecutionReceiptV1,
    str,
]:
    """Execute once from clean main, or reconcile if evidence already exists."""

    repo_root = repo_root.resolve()

    if _existing_execution_evidence(repo_root):
        return freeze_existing_primary_custody(repo_root)

    _require_fresh_execution_paths(repo_root)
    _verified_fixed_artifact(
        repo_root,
        _SPECIMEN_PATH,
        _SPECIMEN_SHA256,
    )
    _verified_fixed_artifact(
        repo_root,
        _AUTHORIZATION_PATH,
        _AUTHORIZATION_SHA256,
    )

    specimen, authorization, coverage, fixture = preflight_specimen(
        repo_root,
        require_main_clean=True,
    )
    _verify_frozen_g5n_identities(repo_root, specimen, authorization)

    projection = load_phase5_b0_runtime_projection(repo_root)
    _verify_execution_order(specimen, projection)

    config, pipeline = build_phase5_b0_primary_pipeline(
        repo_root,
        fixture=fixture,
    )
    if config.configuration_id != authorization.runtime_configuration_id:
        raise B0AuthorizationError(
            "G5N pipeline does not match authorized runtime configuration"
        )

    execution_commit_sha = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    runner_source_sha256 = _sha256_file(
        repo_root / _RUNNER_RELATIVE_PATH
    )
    index_loader_source_sha256 = _sha256_file(
        repo_root / _INDEX_LOADER_RELATIVE_PATH
    )

    raw_batch, receipt = await execute_primary_batch_with_objects(
        repo_root=repo_root,
        specimen=specimen,
        authorization=authorization,
        coverage=coverage,
        fixture=fixture,
        projection=projection,
        pipeline=pipeline,
        execution_commit_sha=execution_commit_sha,
        runner_source_sha256=runner_source_sha256,
        index_loader_source_sha256=index_loader_source_sha256,
        start_journal_path=repo_root / _START_JOURNAL_PATH,
        terminal_journal_path=repo_root / _TERMINAL_JOURNAL_PATH,
    )

    raw_sha256 = _write_or_verify_immutable_model(
        repo_root / _RAW_BATCH_PATH,
        raw_batch,
    )
    if raw_sha256 != receipt.raw_batch_sha256:
        raise B0AuthorizationError(
            "raw G5N batch SHA does not match public receipt"
        )

    receipt_sha256 = _write_or_verify_immutable_model(
        repo_root / _PUBLIC_RECEIPT_PATH,
        receipt,
    )

    return raw_batch, raw_sha256, receipt, receipt_sha256


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]

    raw_batch, raw_sha256, receipt, receipt_sha256 = asyncio.run(
        execute_phase5_b0_primary(repo_root)
    )

    print(f"PHASE5_G5N_PRIMARY_DECISION={receipt.batch_decision}")
    print(f"PHASE5_G5N_PRIMARY_RECEIPT_SHA256={receipt_sha256}")
    print(f"PHASE5_G5N_PRIMARY_RAW_BATCH_SHA256={raw_sha256}")
    print(
        "PHASE5_G5N_PRIMARY_START_JOURNAL_SHA256="
        f"{receipt.start_journal_sha256}"
    )
    print(
        "PHASE5_G5N_PRIMARY_TERMINAL_JOURNAL_PRESENT="
        f"{str(receipt.terminal_journal_present).lower()}"
    )
    print(
        "PHASE5_G5N_PRIMARY_TERMINAL_JOURNAL_SHA256="
        f"{receipt.terminal_journal_sha256 or 'none'}"
    )
    print(
        "PHASE5_G5N_PRIMARY_STARTED_SLOTS="
        f"{receipt.started_slot_count}"
    )
    print(
        "PHASE5_G5N_PRIMARY_TERMINAL_RECORDS="
        f"{receipt.terminal_record_count}"
    )
    print(
        "PHASE5_G5N_PRIMARY_UNRECONCILED_STARTS="
        f"{receipt.unreconciled_started_slot_count}"
    )
    print(f"PHASE5_G5N_PRIMARY_ANSWERS={receipt.answer_count}")
    print(f"PHASE5_G5N_PRIMARY_REFUSALS={receipt.refusal_count}")
    print(f"PHASE5_G5N_PRIMARY_ERRORS={receipt.error_count}")
    print(
        "PHASE5_G5N_PRIMARY_STOP_TRIGGERED="
        f"{str(receipt.stop_triggered).lower()}"
    )
    print(
        "PHASE5_G5N_PRIMARY_COMPLETE="
        f"{str(receipt.primary_execution_complete).lower()}"
    )
    print("PHASE5_G5N_SCORING_PERFORMED=false")
    print("PHASE5_G5N_LIVE_PROVIDER_CALLS=0")
    print("PHASE5_G5O_REPLICATION_EXECUTED=false")
    print(f"PHASE5_G5N_RAW_RECORD_COUNT={len(raw_batch.records)}")

    return 0 if receipt.primary_execution_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
