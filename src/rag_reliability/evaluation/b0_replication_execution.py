"""Execute and reconcile exactly one authorized Phase 5 G5O B0 replication batch.

This module is the replication execution boundary. It reuses the already-qualified
G5N deterministic replay pipeline builder and frozen runtime configuration, but
uses only the 42 fresh replication slots from the frozen 84-slot authorization.

Replication is fail-closed on tracked G5N primary execution/scoring custody:
the primary execution must be complete, the primary scoring evidence must be valid,
and the scoring receipt must explicitly mark replication as eligible.

A replication slot is consumed when its durable start record is appended.
Existing replication evidence switches the top-level entry point into
reconciliation-only mode; it never resumes or replaces consumed evidence.
"""

from __future__ import annotations

import asyncio
import subprocess
from collections import Counter
from pathlib import Path
from typing import Literal, Protocol, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import RuntimeErrorCode, TraceStage
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import ErrorOutcome
from rag_reliability.evaluation.b0_authorization_models import (
    B0AuthorizationError,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ExecutionSlotV1,
    Phase5B0SpecimenV1,
)
from rag_reliability.evaluation.b0_execution_preflight import (
    load_frozen_specimen_and_authorization,
    preflight_execution_slot_with_objects,
    preflight_specimen,
)
from rag_reliability.evaluation.b0_primary_execution import (
    _AUTHORIZATION_SHA256,
    _ENVIRONMENT_SHA256,
    _INDEX_LOADER_RELATIVE_PATH,
    _REPLAY_FIXTURE_SHA256,
    _RUNTIME_CONFIGURATION_ID,
    _SPECIMEN_SHA256,
    Phase5B0PrimaryExecutionReceiptV1,
    _append_durable,
    _ordered_runtime_cases,
    _sha256_file,
    _sha256_model,
    _sha256_text,
    _terminal_error_stage,
    _verified_fixed_artifact,
    _verify_execution_order,
    _verify_frozen_g5n_identities,
    _write_or_verify_immutable_model,
    build_phase5_b0_primary_pipeline,
)
from rag_reliability.evaluation.b0_primary_scoring import (
    Phase5B0PrimaryScoringReceiptV1,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    B0Role,
    Phase5B0RuntimeProjectionV1,
    load_phase5_b0_runtime_projection,
)
from rag_reliability.runtime.models import PipelineExecution

_PRIMARY_EXECUTION_RECEIPT_SHA256: Sha256 = (
    "1849a3d64740374d7890c6201ec4696b8fcfc5458d7f7c1217d76970f7cf661d"
)
_PRIMARY_SCORING_RECEIPT_SHA256: Sha256 = (
    "442eceef4876613eac03429f8a083872642d915ffdc542ecd078124333669e60"
)

_PRIMARY_EXECUTION_RECEIPT_PATH = Path(
    "artifacts/development/phase5_b0_primary_execution_receipt_v1.json"
)
_PRIMARY_SCORING_RECEIPT_PATH = Path(
    "artifacts/development/phase5_b0_primary_scoring_receipt_v1.json"
)

_START_JOURNAL_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_replication_start_journal_v1.jsonl"
)
_TERMINAL_JOURNAL_PATH = Path(
    "evidence_vault/eval_reports/phase5_b0_replication_terminal_journal_v1.jsonl"
)
_RAW_BATCH_PATH = Path("evidence_vault/eval_reports/phase5_b0_replication_execution_v1.json")
_PUBLIC_RECEIPT_PATH = Path("artifacts/development/phase5_b0_replication_execution_receipt_v1.json")

_RUNNER_RELATIVE_PATH = "src/rag_reliability/evaluation/b0_replication_execution.py"

ReplicationBatchDecision = Literal["COMPLETE", "STOPPED", "INTERRUPTED"]


class ReplicationPipeline(Protocol):
    """Minimal runtime-only execution seam used by the G5O runner."""

    async def run(self, case: RuntimeCaseInput) -> PipelineExecution:
        """Execute one runtime-projected case."""


class Phase5B0ReplicationStartRecordV1(ContractModel):
    """Durable evidence that an authorized replication slot was consumed."""

    record_version: Literal["phase5-b0-replication-start-record-v1"] = (
        "phase5-b0-replication-start-record-v1"
    )

    slot_id: NonEmptyStr
    ordinal: int = Field(ge=1, le=42)
    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256

    execution_commit_sha: NonEmptyStr
    runner_source_sha256: Sha256
    index_loader_source_sha256: Sha256


class Phase5B0ReplicationExecutionRecordV1(ContractModel):
    """One terminal replication record retained only in the evidence vault."""

    record_version: Literal["phase5-b0-replication-execution-record-v1"] = (
        "phase5-b0-replication-execution-record-v1"
    )

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


class Phase5B0ReplicationUnreconciledStartV1(ContractModel):
    """Metadata-safe consumed replication start with no terminal record."""

    slot_id: NonEmptyStr
    ordinal: int = Field(ge=1, le=42)
    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256


class Phase5B0ReplicationPublicCaseReceiptV1(ContractModel):
    """Metadata-safe terminal replication custody."""

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


class Phase5B0ReplicationRawBatchV1(ContractModel):
    """Internal raw G5O custody; may represent interrupted consumed evidence."""

    batch_version: Literal["phase5-b0-replication-execution-v1"] = (
        "phase5-b0-replication-execution-v1"
    )

    specimen_sha256: Sha256 = _SPECIMEN_SHA256
    authorization_sha256: Sha256 = _AUTHORIZATION_SHA256
    runtime_configuration_id: Sha256 = _RUNTIME_CONFIGURATION_ID
    replay_fixture_sha256: Sha256 = _REPLAY_FIXTURE_SHA256
    environment_sha256: Sha256 = _ENVIRONMENT_SHA256

    primary_execution_receipt_sha256: Sha256 = _PRIMARY_EXECUTION_RECEIPT_SHA256
    primary_scoring_receipt_sha256: Sha256 = _PRIMARY_SCORING_RECEIPT_SHA256

    execution_commit_sha: NonEmptyStr
    runner_source_sha256: Sha256
    index_loader_source_sha256: Sha256

    arm: Literal["replication"] = "replication"
    authorized_case_count: Literal[42] = 42
    authorized_replication_slot_count: Literal[42] = 42

    started_slot_count: int = Field(ge=1, le=42)
    terminal_record_count: int = Field(ge=0, le=42)
    unreconciled_started_slot_count: int = Field(ge=0, le=42)

    records: tuple[Phase5B0ReplicationExecutionRecordV1, ...] = Field(
        default=(),
        max_length=42,
    )
    unreconciled_starts: tuple[
        Phase5B0ReplicationUnreconciledStartV1,
        ...,
    ] = Field(default=(), max_length=42)

    same_stage_failure_stop_count: Literal[2] = 2
    stop_triggered: bool
    stop_stage: TraceStage | None = None
    batch_decision: ReplicationBatchDecision
    batch_complete: bool

    primary_evidence_valid_and_custodied: Literal[True] = True
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

        if self.unreconciled_started_slot_count != len(self.unreconciled_starts):
            raise ValueError("unreconciled start count does not reconcile")

        if self.started_slot_count != (
            self.terminal_record_count + self.unreconciled_started_slot_count
        ):
            raise ValueError("started slot count does not reconcile")

        terminal_slots = tuple(record.slot_id for record in self.records)
        unreconciled_slots = tuple(record.slot_id for record in self.unreconciled_starts)
        all_slots = terminal_slots + unreconciled_slots

        if len(all_slots) != len(set(all_slots)):
            raise ValueError("replication raw batch contains duplicate slots")

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


class Phase5B0ReplicationExecutionReceiptV1(ContractModel):
    """Tracked public-safe custody receipt for the G5O replication batch."""

    receipt_version: Literal["phase5-b0-replication-execution-receipt-v1"] = (
        "phase5-b0-replication-execution-receipt-v1"
    )

    specimen_sha256: Sha256 = _SPECIMEN_SHA256
    authorization_sha256: Sha256 = _AUTHORIZATION_SHA256
    runtime_configuration_id: Sha256 = _RUNTIME_CONFIGURATION_ID
    replay_fixture_sha256: Sha256 = _REPLAY_FIXTURE_SHA256
    environment_sha256: Sha256 = _ENVIRONMENT_SHA256

    primary_execution_receipt_sha256: Sha256 = _PRIMARY_EXECUTION_RECEIPT_SHA256
    primary_scoring_receipt_sha256: Sha256 = _PRIMARY_SCORING_RECEIPT_SHA256

    execution_commit_sha: NonEmptyStr
    runner_source_sha256: Sha256
    index_loader_source_sha256: Sha256

    raw_batch_relative_path: Literal[
        "evidence_vault/eval_reports/phase5_b0_replication_execution_v1.json"
    ] = "evidence_vault/eval_reports/phase5_b0_replication_execution_v1.json"

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

    cases: tuple[Phase5B0ReplicationPublicCaseReceiptV1, ...] = Field(
        default=(),
        max_length=42,
    )
    unreconciled_starts: tuple[
        Phase5B0ReplicationUnreconciledStartV1,
        ...,
    ] = Field(default=(), max_length=42)

    same_stage_failure_stop_count: Literal[2] = 2
    stop_triggered: bool
    stop_stage: TraceStage | None = None
    batch_decision: ReplicationBatchDecision
    replication_execution_complete: bool

    primary_evidence_valid_and_custodied: Literal[True] = True
    scoring_performed: Literal[False] = False
    evaluator_fields_used_by_runtime: Literal[False] = False
    live_provider_call_count: Literal[0] = 0
    protected_roles_accessed: Literal[False] = False
    selective_rerun_used: Literal[False] = False
    replacement_start_used: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    replication_executed: Literal[True] = True
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_receipt(self) -> Self:
        if self.terminal_record_count != len(self.cases):
            raise ValueError("receipt terminal count does not reconcile")

        if self.unreconciled_started_slot_count != len(self.unreconciled_starts):
            raise ValueError("receipt unreconciled count does not reconcile")

        if self.started_slot_count != (
            self.terminal_record_count + self.unreconciled_started_slot_count
        ):
            raise ValueError("receipt started count does not reconcile")

        outcome_total = self.answer_count + self.refusal_count + self.error_count
        if outcome_total != self.terminal_record_count:
            raise ValueError("receipt outcome counts do not reconcile")

        case_ids = tuple(case.case_id for case in self.cases)
        slot_ids = tuple(case.slot_id for case in self.cases)
        unresolved_slot_ids = tuple(item.slot_id for item in self.unreconciled_starts)

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("receipt terminal case IDs must be unique")
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("receipt terminal slot IDs must be unique")
        if set(slot_ids) & set(unresolved_slot_ids):
            raise ValueError("terminal and unreconciled slots overlap")

        if self.terminal_journal_present != (self.terminal_journal_sha256 is not None):
            raise ValueError("terminal journal presence does not reconcile")

        expected_complete = (
            self.started_slot_count == 42
            and self.terminal_record_count == 42
            and self.unreconciled_started_slot_count == 0
            and not self.stop_triggered
        )
        if self.replication_execution_complete != expected_complete:
            raise ValueError("replication execution completeness does not reconcile")

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
        str(relative) for relative in _execution_evidence_paths() if (repo_root / relative).exists()
    )


def _require_fresh_execution_paths(repo_root: Path) -> None:
    existing = _existing_execution_evidence(repo_root)
    if existing:
        joined = ", ".join(existing)
        raise B0AuthorizationError(
            "G5O replication evidence path already exists; "
            f"execution cannot continue or rerun: {joined}"
        )


def _load_primary_eligibility(
    repo_root: Path,
) -> tuple[
    Phase5B0PrimaryExecutionReceiptV1,
    Phase5B0PrimaryScoringReceiptV1,
    set[str],
]:
    """Verify tracked G5N custody and return already-consumed primary slots."""

    _verified_fixed_artifact(
        repo_root,
        _PRIMARY_EXECUTION_RECEIPT_PATH,
        _PRIMARY_EXECUTION_RECEIPT_SHA256,
    )
    _verified_fixed_artifact(
        repo_root,
        _PRIMARY_SCORING_RECEIPT_PATH,
        _PRIMARY_SCORING_RECEIPT_SHA256,
    )

    execution_receipt = Phase5B0PrimaryExecutionReceiptV1.model_validate_json(
        (repo_root / _PRIMARY_EXECUTION_RECEIPT_PATH).read_bytes()
    )
    scoring_receipt = Phase5B0PrimaryScoringReceiptV1.model_validate_json(
        (repo_root / _PRIMARY_SCORING_RECEIPT_PATH).read_bytes()
    )

    if not execution_receipt.primary_execution_complete:
        raise B0AuthorizationError(
            "G5O replication requires complete G5N primary execution custody"
        )
    if execution_receipt.started_slot_count != 42:
        raise B0AuthorizationError("G5O replication requires exactly 42 consumed primary starts")
    if execution_receipt.terminal_record_count != 42:
        raise B0AuthorizationError("G5O replication requires 42 primary terminal records")
    if execution_receipt.unreconciled_started_slot_count != 0:
        raise B0AuthorizationError("G5O replication rejects unreconciled primary starts")

    if scoring_receipt.primary_execution_receipt_sha256 != (_PRIMARY_EXECUTION_RECEIPT_SHA256):
        raise B0AuthorizationError("G5N scoring receipt is not bound to the frozen primary receipt")
    if scoring_receipt.primary_raw_batch_sha256 != execution_receipt.raw_batch_sha256:
        raise B0AuthorizationError("G5N scoring receipt raw batch binding does not reconcile")
    if scoring_receipt.observed_case_count != 42:
        raise B0AuthorizationError("G5N scoring receipt does not cover all 42 primary cases")
    if not scoring_receipt.evidence_valid:
        raise B0AuthorizationError("G5O replication requires valid primary scoring evidence")
    if not scoring_receipt.replication_eligible:
        raise B0AuthorizationError("G5N scoring receipt does not authorize G5O replication")
    if scoring_receipt.runtime_reexecuted:
        raise B0AuthorizationError("G5N scoring receipt unexpectedly reports runtime re-execution")
    if scoring_receipt.live_provider_call_count != 0:
        raise B0AuthorizationError("G5N scoring receipt unexpectedly reports live provider calls")
    if scoring_receipt.held_out_outcomes_exposed:
        raise B0AuthorizationError("G5N scoring receipt reports HELD_OUT exposure")
    if scoring_receipt.post_reject_confirmation_inspected:
        raise B0AuthorizationError("G5N scoring receipt reports POST_REJECT_CONFIRMATION exposure")

    primary_slot_ids = {case.slot_id for case in execution_receipt.cases}
    if len(primary_slot_ids) != 42:
        raise B0AuthorizationError("G5N primary custody does not contain 42 unique terminal slots")

    return execution_receipt, scoring_receipt, primary_slot_ids


def _replication_slot_for_case(
    authorization: Phase5B0ExecutionAuthorizationV1,
    case_id: str,
) -> Phase5B0ExecutionSlotV1:
    matches = tuple(
        slot
        for slot in authorization.slots
        if slot.arm == "replication" and slot.case_id == case_id
    )
    if len(matches) != 1:
        raise B0AuthorizationError(f"exactly one replication authorization required for {case_id}")
    return matches[0]


def _public_case_receipt(
    record: Phase5B0ReplicationExecutionRecordV1,
) -> Phase5B0ReplicationPublicCaseReceiptV1:
    outcome = record.execution.outcome
    error_code = outcome.error_code if isinstance(outcome, ErrorOutcome) else None
    events = record.execution.trace.events

    if not events:
        raise B0AuthorizationError("terminal execution has no trace events")

    return Phase5B0ReplicationPublicCaseReceiptV1(
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
    record: Phase5B0ReplicationStartRecordV1,
) -> Phase5B0ReplicationUnreconciledStartV1:
    return Phase5B0ReplicationUnreconciledStartV1(
        slot_id=record.slot_id,
        ordinal=record.ordinal,
        case_id=record.case_id,
        role=record.role,
        query_sha256=record.query_sha256,
    )


def _read_start_journal(
    path: Path,
) -> tuple[Phase5B0ReplicationStartRecordV1, ...]:
    if not path.exists():
        raise B0AuthorizationError("replication start journal does not exist")

    lines = path.read_bytes().splitlines()
    if not lines:
        raise B0AuthorizationError("replication start journal is empty")

    return tuple(Phase5B0ReplicationStartRecordV1.model_validate_json(line) for line in lines)


def _read_terminal_journal(
    path: Path,
) -> tuple[Phase5B0ReplicationExecutionRecordV1, ...]:
    if not path.exists():
        return ()

    lines = path.read_bytes().splitlines()
    if not lines:
        raise B0AuthorizationError("replication terminal journal is empty")

    return tuple(Phase5B0ReplicationExecutionRecordV1.model_validate_json(line) for line in lines)


def _validate_start_journal(
    *,
    authorization: Phase5B0ExecutionAuthorizationV1,
    projection: Phase5B0RuntimeProjectionV1,
    starts: tuple[Phase5B0ReplicationStartRecordV1, ...],
) -> None:
    ordered = _ordered_runtime_cases(projection)
    if len(starts) > len(ordered):
        raise B0AuthorizationError("replication start journal exceeds 42 slots")

    first = starts[0]
    identity = (
        first.execution_commit_sha,
        first.runner_source_sha256,
        first.index_loader_source_sha256,
    )

    observed_slot_ids: set[str] = set()

    for index, start in enumerate(starts):
        role, case = ordered[index]
        slot = _replication_slot_for_case(authorization, case.case_id)
        expected_query_sha = _sha256_text(case.query)

        if start.slot_id in observed_slot_ids:
            raise B0AuthorizationError("replication start journal repeats a slot")

        observed_slot_ids.add(start.slot_id)

        if start.ordinal != index + 1:
            raise B0AuthorizationError("replication start journal order drifted")
        if start.slot_id != slot.slot_id:
            raise B0AuthorizationError("replication start slot binding drifted")
        if start.case_id != case.case_id:
            raise B0AuthorizationError("replication start case binding drifted")
        if start.role != role or start.role != slot.role:
            raise B0AuthorizationError("replication start role binding drifted")
        if start.query_sha256 != expected_query_sha:
            raise B0AuthorizationError("replication start query binding drifted")
        if start.query_sha256 != slot.query_sha256:
            raise B0AuthorizationError("replication authorization query drifted")

        current_identity = (
            start.execution_commit_sha,
            start.runner_source_sha256,
            start.index_loader_source_sha256,
        )
        if current_identity != identity:
            raise B0AuthorizationError("replication start execution identity drifted")


def _validate_terminal_journal(
    *,
    starts: tuple[Phase5B0ReplicationStartRecordV1, ...],
    terminals: tuple[Phase5B0ReplicationExecutionRecordV1, ...],
) -> None:
    if len(terminals) > len(starts):
        raise B0AuthorizationError("replication terminal journal exceeds consumed starts")

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
                "replication terminal journal is not a prefix of consumed starts"
            )


def _typed_stop_stage(
    terminals: tuple[Phase5B0ReplicationExecutionRecordV1, ...],
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


def reconcile_replication_journals_with_objects(
    *,
    authorization: Phase5B0ExecutionAuthorizationV1,
    projection: Phase5B0RuntimeProjectionV1,
    start_journal_path: Path,
    terminal_journal_path: Path,
) -> tuple[
    Phase5B0ReplicationRawBatchV1,
    Phase5B0ReplicationExecutionReceiptV1,
]:
    """Reconcile durable replication journals without executing or resuming."""

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
            raise B0AuthorizationError("terminal records exist after the mandatory typed stop")
        if len(starts) != len(terminals):
            raise B0AuthorizationError("a slot was started after the mandatory typed stop")

    unreconciled = tuple(_unreconciled_start(start) for start in starts[len(terminals) :])

    complete = (
        len(starts) == 42 and len(terminals) == 42 and not unreconciled and stop_stage is None
    )

    if complete:
        decision: ReplicationBatchDecision = "COMPLETE"
    elif stop_stage is not None:
        decision = "STOPPED"
    else:
        decision = "INTERRUPTED"

    first = starts[0]
    raw_batch = Phase5B0ReplicationRawBatchV1(
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
    answer_count = sum(record.execution.outcome.status == "answer" for record in terminals)
    refusal_count = sum(record.execution.outcome.status == "refusal" for record in terminals)
    error_count = sum(record.execution.outcome.status == "error" for record in terminals)

    terminal_present = terminal_journal_path.exists()
    terminal_sha = _sha256_file(terminal_journal_path) if terminal_present else None

    receipt = Phase5B0ReplicationExecutionReceiptV1(
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
        replication_execution_complete=complete,
    )

    return raw_batch, receipt


def _validate_primary_slot_set(
    authorization: Phase5B0ExecutionAuthorizationV1,
    primary_started_slot_ids: set[str],
) -> None:
    expected = {slot.slot_id for slot in authorization.slots if slot.arm == "primary"}
    if len(expected) != 42:
        raise B0AuthorizationError("authorization does not contain exactly 42 primary slots")
    if primary_started_slot_ids != expected:
        raise B0AuthorizationError("primary consumed-slot set does not match frozen authorization")


async def execute_replication_batch_with_objects(
    *,
    specimen: Phase5B0SpecimenV1,
    authorization: Phase5B0ExecutionAuthorizationV1,
    coverage: Phase5B0ReplayFixtureCoverageV1,
    fixture: Phase5B0ReplayFixtureV1,
    projection: Phase5B0RuntimeProjectionV1,
    pipeline: ReplicationPipeline,
    execution_commit_sha: str,
    runner_source_sha256: str,
    index_loader_source_sha256: str,
    primary_started_slot_ids: set[str],
    primary_batch_valid_and_custodied: bool,
    start_journal_path: Path,
    terminal_journal_path: Path,
) -> tuple[
    Phase5B0ReplicationRawBatchV1,
    Phase5B0ReplicationExecutionReceiptV1,
]:
    """Execute fresh replication slots only."""

    if start_journal_path.exists() or terminal_journal_path.exists():
        raise B0AuthorizationError(
            "replication journals already exist; execution cannot resume or rerun"
        )

    if not primary_batch_valid_and_custodied:
        raise B0AuthorizationError("replication requires valid, custodied G5N primary evidence")

    _validate_primary_slot_set(authorization, primary_started_slot_ids)

    if specimen.runtime_configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("specimen runtime configuration drifted")
    if authorization.runtime_configuration_id != _RUNTIME_CONFIGURATION_ID:
        raise B0AuthorizationError("authorization runtime configuration drifted")

    all_started_slot_ids = set(primary_started_slot_ids)
    replication_started_slot_ids: set[str] = set()
    error_stages: Counter[TraceStage] = Counter()

    for role, case in _ordered_runtime_cases(projection):
        slot = preflight_execution_slot_with_objects(
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            arm="replication",
            case_id=case.case_id,
            role=role,
            query=case.query,
            started_slot_ids=all_started_slot_ids,
            primary_batch_valid_and_custodied=True,
        )

        start_record = Phase5B0ReplicationStartRecordV1(
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
            first=not replication_started_slot_ids,
        )
        replication_started_slot_ids.add(slot.slot_id)
        all_started_slot_ids.add(slot.slot_id)

        execution = await pipeline.run(case)

        terminal_record = Phase5B0ReplicationExecutionRecordV1(
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
            if error_stages[error_stage] >= authorization.same_stage_failure_stop_count:
                break

    return reconcile_replication_journals_with_objects(
        authorization=authorization,
        projection=projection,
        start_journal_path=start_journal_path,
        terminal_journal_path=terminal_journal_path,
    )


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


def freeze_existing_replication_custody(
    repo_root: Path,
) -> tuple[
    Phase5B0ReplicationRawBatchV1,
    str,
    Phase5B0ReplicationExecutionReceiptV1,
    str,
]:
    """Freeze existing replication journals only; never execute or resume."""

    repo_root = repo_root.resolve()
    _load_primary_eligibility(repo_root)
    _specimen, authorization, projection = _load_recovery_objects(repo_root)

    raw_batch, receipt = reconcile_replication_journals_with_objects(
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
        raise B0AuthorizationError("raw G5O batch SHA does not match public receipt")

    receipt_sha256 = _write_or_verify_immutable_model(
        repo_root / _PUBLIC_RECEIPT_PATH,
        receipt,
    )

    return raw_batch, raw_sha256, receipt, receipt_sha256


async def execute_phase5_b0_replication(
    repo_root: Path,
) -> tuple[
    Phase5B0ReplicationRawBatchV1,
    str,
    Phase5B0ReplicationExecutionReceiptV1,
    str,
]:
    """Execute once from clean main, or reconcile if evidence already exists."""

    repo_root = repo_root.resolve()

    if _existing_execution_evidence(repo_root):
        return freeze_existing_replication_custody(repo_root)

    _require_fresh_execution_paths(repo_root)

    specimen, authorization, coverage, fixture = preflight_specimen(
        repo_root,
        require_main_clean=True,
    )
    _verify_frozen_g5n_identities(repo_root, specimen, authorization)

    (
        primary_execution_receipt,
        _primary_scoring_receipt,
        primary_slot_ids,
    ) = _load_primary_eligibility(repo_root)

    projection = load_phase5_b0_runtime_projection(repo_root)
    _verify_execution_order(specimen, projection)

    config, pipeline = build_phase5_b0_primary_pipeline(
        repo_root,
        fixture=fixture,
    )
    if config.configuration_id != authorization.runtime_configuration_id:
        raise B0AuthorizationError("G5O pipeline does not match authorized runtime configuration")

    current_index_loader_sha = _sha256_file(repo_root / _INDEX_LOADER_RELATIVE_PATH)
    if current_index_loader_sha != (primary_execution_receipt.index_loader_source_sha256):
        raise B0AuthorizationError("G5O index loader bytes differ from G5N primary execution")

    execution_commit_sha = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    runner_source_sha256 = _sha256_file(repo_root / _RUNNER_RELATIVE_PATH)

    raw_batch, receipt = await execute_replication_batch_with_objects(
        specimen=specimen,
        authorization=authorization,
        coverage=coverage,
        fixture=fixture,
        projection=projection,
        pipeline=pipeline,
        execution_commit_sha=execution_commit_sha,
        runner_source_sha256=runner_source_sha256,
        index_loader_source_sha256=current_index_loader_sha,
        primary_started_slot_ids=primary_slot_ids,
        primary_batch_valid_and_custodied=True,
        start_journal_path=repo_root / _START_JOURNAL_PATH,
        terminal_journal_path=repo_root / _TERMINAL_JOURNAL_PATH,
    )

    raw_sha256 = _write_or_verify_immutable_model(
        repo_root / _RAW_BATCH_PATH,
        raw_batch,
    )
    if raw_sha256 != receipt.raw_batch_sha256:
        raise B0AuthorizationError("raw G5O batch SHA does not match public receipt")

    receipt_sha256 = _write_or_verify_immutable_model(
        repo_root / _PUBLIC_RECEIPT_PATH,
        receipt,
    )

    return raw_batch, raw_sha256, receipt, receipt_sha256


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]

    raw_batch, raw_sha256, receipt, receipt_sha256 = asyncio.run(
        execute_phase5_b0_replication(repo_root)
    )

    print(f"PHASE5_G5O_REPLICATION_DECISION={receipt.batch_decision}")
    print(f"PHASE5_G5O_REPLICATION_RECEIPT_SHA256={receipt_sha256}")
    print(f"PHASE5_G5O_REPLICATION_RAW_BATCH_SHA256={raw_sha256}")
    print(f"PHASE5_G5O_REPLICATION_START_JOURNAL_SHA256={receipt.start_journal_sha256}")
    print(
        "PHASE5_G5O_REPLICATION_TERMINAL_JOURNAL_PRESENT="
        f"{str(receipt.terminal_journal_present).lower()}"
    )
    print(
        "PHASE5_G5O_REPLICATION_TERMINAL_JOURNAL_SHA256="
        f"{receipt.terminal_journal_sha256 or 'none'}"
    )
    print(f"PHASE5_G5O_REPLICATION_STARTED_SLOTS={receipt.started_slot_count}")
    print(f"PHASE5_G5O_REPLICATION_TERMINAL_RECORDS={receipt.terminal_record_count}")
    print(f"PHASE5_G5O_REPLICATION_UNRECONCILED_STARTS={receipt.unreconciled_started_slot_count}")
    print(f"PHASE5_G5O_REPLICATION_ANSWERS={receipt.answer_count}")
    print(f"PHASE5_G5O_REPLICATION_REFUSALS={receipt.refusal_count}")
    print(f"PHASE5_G5O_REPLICATION_ERRORS={receipt.error_count}")
    print(f"PHASE5_G5O_REPLICATION_STOP_TRIGGERED={str(receipt.stop_triggered).lower()}")
    print(f"PHASE5_G5O_REPLICATION_COMPLETE={str(receipt.replication_execution_complete).lower()}")
    print("PHASE5_G5O_PRIMARY_EVIDENCE_VALID_AND_CUSTODIED=true")
    print("PHASE5_G5O_SCORING_PERFORMED=false")
    print("PHASE5_G5O_LIVE_PROVIDER_CALLS=0")
    print(f"PHASE5_G5O_RAW_RECORD_COUNT={len(raw_batch.records)}")

    return 0 if receipt.replication_execution_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
