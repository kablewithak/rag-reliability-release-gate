from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import pytest

from rag_reliability.contracts.enums import (
    RuntimeErrorCode,
    TraceStage,
    TraceStatus,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import ErrorOutcome, RefusalOutcome
from rag_reliability.contracts.tracing import TraceEvent, TraceRecord
from rag_reliability.evaluation.b0_authorization_models import (
    B0AuthorizationError,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0SpecimenV1,
)
from rag_reliability.evaluation.b0_primary_execution import (
    _ENVIRONMENT_SHA256,
    _REPLAY_FIXTURE_SHA256,
    _RUNTIME_CONFIGURATION_ID,
    _SPECIMEN_SHA256,
    _require_fresh_execution_paths,
    build_phase5_b0_primary_pipeline,
    execute_primary_batch_with_objects,
    reconcile_primary_journals_with_objects,
)
from rag_reliability.evaluation.b0_replay_fixture_materializer import (
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
    _build_materialization,
)
from rag_reliability.evaluation.b0_runtime_projection import (
    Phase5B0RuntimeProjectionV1,
    load_phase5_b0_runtime_projection,
)
from rag_reliability.evaluation.b0_specimen_authorization import load_coverage
from rag_reliability.runtime.models import PipelineExecution

ROOT = Path(__file__).resolve().parents[2]
_SPECIMEN_PATH = (
    ROOT / "artifacts" / "development" / "phase5_b0_specimen_v1.json"
)
_AUTHORIZATION_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_b0_execution_authorization_v1.json"
)


class _RefusalPipeline:
    async def run(self, case: RuntimeCaseInput) -> PipelineExecution:
        event = TraceEvent(
            event_id=f"{case.case_id}:1:refusal_fallback",
            stage=TraceStage.REFUSAL_FALLBACK,
            status=TraceStatus.REFUSED,
            occurred_at=datetime.now(UTC),
            duration_ms=0.0,
        )
        trace = TraceRecord(
            trace_id=f"test:{case.case_id}",
            case_id=case.case_id,
            configuration_id=_RUNTIME_CONFIGURATION_ID,
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            events=(event,),
            primary_failure=None,
        )
        return PipelineExecution(
            outcome=RefusalOutcome(
                reason="insufficient_evidence",
                message="Synthetic refusal.",
            ),
            trace=trace,
        )


class _ProviderErrorPipeline:
    async def run(self, case: RuntimeCaseInput) -> PipelineExecution:
        event = TraceEvent(
            event_id=f"{case.case_id}:1:provider_generation",
            stage=TraceStage.PROVIDER_GENERATION,
            status=TraceStatus.ERROR,
            occurred_at=datetime.now(UTC),
            duration_ms=0.0,
            error_code=RuntimeErrorCode.PROVIDER_TIMEOUT.value,
        )
        trace = TraceRecord(
            trace_id=f"test:{case.case_id}",
            case_id=case.case_id,
            configuration_id=_RUNTIME_CONFIGURATION_ID,
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            events=(event,),
            primary_failure="provider_timeout",
        )
        return PipelineExecution(
            outcome=ErrorOutcome(
                error_code=RuntimeErrorCode.PROVIDER_TIMEOUT,
                message="Synthetic provider timeout.",
                retryable=False,
            ),
            trace=trace,
        )


class _CrashAfterDurableStartPipeline:
    def __init__(self, start_journal_path: Path) -> None:
        self._start_journal_path = start_journal_path

    async def run(self, case: RuntimeCaseInput) -> PipelineExecution:
        del case
        lines = self._start_journal_path.read_bytes().splitlines()
        assert len(lines) == 1
        raise RuntimeError("synthetic crash after durable start")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _objects() -> tuple[
    Phase5B0SpecimenV1,
    Phase5B0ExecutionAuthorizationV1,
    Phase5B0ReplayFixtureCoverageV1,
    Phase5B0ReplayFixtureV1,
    Phase5B0RuntimeProjectionV1,
]:
    specimen = Phase5B0SpecimenV1.model_validate_json(
        _SPECIMEN_PATH.read_bytes()
    )
    authorization = Phase5B0ExecutionAuthorizationV1.model_validate_json(
        _AUTHORIZATION_PATH.read_bytes()
    )
    coverage = load_coverage(ROOT)

    fixture, rebuilt_coverage = asyncio.run(_build_materialization(ROOT))
    if fixture is None:
        raise AssertionError("deterministic B0 fixture did not materialize in memory")
    if rebuilt_coverage != coverage:
        raise AssertionError(
            "in-memory B0 coverage does not match tracked frozen coverage"
        )

    projection = load_phase5_b0_runtime_projection(ROOT)
    return specimen, authorization, coverage, fixture, projection


def test_frozen_g5m_identities_are_the_authorized_values() -> None:
    specimen, authorization, _coverage, fixture, projection = _objects()

    assert specimen.environment_sha256 == _ENVIRONMENT_SHA256
    assert specimen.runtime_configuration_id == _RUNTIME_CONFIGURATION_ID
    assert specimen.replay_fixture_sha256 == _REPLAY_FIXTURE_SHA256

    assert authorization.specimen_sha256 == _SPECIMEN_SHA256
    assert authorization.runtime_configuration_id == _RUNTIME_CONFIGURATION_ID
    assert authorization.replay_fixture_sha256 == _REPLAY_FIXTURE_SHA256

    assert len(fixture.entries) == 42
    assert len(projection.development.cases) == 24
    assert len(projection.tuning.cases) == 18


def test_real_pipeline_build_matches_authorized_configuration() -> None:
    _specimen, authorization, _coverage, fixture, _projection = _objects()

    config, _pipeline = build_phase5_b0_primary_pipeline(
        ROOT,
        fixture=fixture,
    )

    assert config.configuration_id == _RUNTIME_CONFIGURATION_ID
    assert config.configuration_id == authorization.runtime_configuration_id
    assert config.provider.adapter_id == "replay-provider-v1"
    assert config.provider.max_retries == 0


def test_synthetic_complete_batch_consumes_exactly_42_primary_slots(
    tmp_path: Path,
) -> None:
    specimen, authorization, coverage, fixture, projection = _objects()

    start_path = tmp_path / "start.jsonl"
    terminal_path = tmp_path / "terminal.jsonl"

    raw_batch, receipt = asyncio.run(
        execute_primary_batch_with_objects(
            repo_root=ROOT,
            specimen=specimen,
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            projection=projection,
            pipeline=_RefusalPipeline(),
            execution_commit_sha="a" * 40,
            runner_source_sha256="b" * 64,
            index_loader_source_sha256="c" * 64,
            start_journal_path=start_path,
            terminal_journal_path=terminal_path,
        )
    )

    assert raw_batch.batch_decision == "COMPLETE"
    assert raw_batch.batch_complete is True
    assert raw_batch.started_slot_count == 42
    assert raw_batch.terminal_record_count == 42
    assert raw_batch.unreconciled_started_slot_count == 0
    assert len(raw_batch.records) == 42

    assert receipt.primary_execution_complete is True
    assert receipt.started_slot_count == 42
    assert receipt.terminal_record_count == 42
    assert receipt.unreconciled_started_slot_count == 0
    assert receipt.answer_count == 0
    assert receipt.refusal_count == 42
    assert receipt.error_count == 0
    assert receipt.scoring_performed is False
    assert receipt.live_provider_call_count == 0

    assert len(start_path.read_text(encoding="utf-8").splitlines()) == 42
    assert len(terminal_path.read_text(encoding="utf-8").splitlines()) == 42
    assert receipt.start_journal_sha256 == _sha256_file(start_path)
    assert receipt.terminal_journal_sha256 == _sha256_file(terminal_path)

    public_text = receipt.model_dump_json()
    assert "Synthetic refusal." not in public_text
    assert '"query":' not in public_text
    assert '"answer_text":' not in public_text


def test_same_stage_stop_fires_after_second_terminal_error(
    tmp_path: Path,
) -> None:
    specimen, authorization, coverage, fixture, projection = _objects()

    raw_batch, receipt = asyncio.run(
        execute_primary_batch_with_objects(
            repo_root=ROOT,
            specimen=specimen,
            authorization=authorization,
            coverage=coverage,
            fixture=fixture,
            projection=projection,
            pipeline=_ProviderErrorPipeline(),
            execution_commit_sha="a" * 40,
            runner_source_sha256="b" * 64,
            index_loader_source_sha256="c" * 64,
            start_journal_path=tmp_path / "start.jsonl",
            terminal_journal_path=tmp_path / "terminal.jsonl",
        )
    )

    assert raw_batch.batch_decision == "STOPPED"
    assert raw_batch.stop_triggered is True
    assert raw_batch.stop_stage is TraceStage.PROVIDER_GENERATION
    assert raw_batch.started_slot_count == 2
    assert raw_batch.terminal_record_count == 2
    assert raw_batch.unreconciled_started_slot_count == 0

    assert receipt.primary_execution_complete is False
    assert receipt.batch_decision == "STOPPED"
    assert receipt.stop_triggered is True
    assert receipt.stop_stage is TraceStage.PROVIDER_GENERATION
    assert receipt.error_count == 2


def test_crash_after_start_preserves_spent_slot_and_never_resumes(
    tmp_path: Path,
) -> None:
    specimen, authorization, coverage, fixture, projection = _objects()

    start_path = tmp_path / "start.jsonl"
    terminal_path = tmp_path / "terminal.jsonl"

    with pytest.raises(
        RuntimeError,
        match="synthetic crash after durable start",
    ):
        asyncio.run(
            execute_primary_batch_with_objects(
                repo_root=ROOT,
                specimen=specimen,
                authorization=authorization,
                coverage=coverage,
                fixture=fixture,
                projection=projection,
                pipeline=_CrashAfterDurableStartPipeline(start_path),
                execution_commit_sha="a" * 40,
                runner_source_sha256="b" * 64,
                index_loader_source_sha256="c" * 64,
                start_journal_path=start_path,
                terminal_journal_path=terminal_path,
            )
        )

    assert len(start_path.read_bytes().splitlines()) == 1
    assert not terminal_path.exists()

    raw_batch, receipt = reconcile_primary_journals_with_objects(
        authorization=authorization,
        projection=projection,
        start_journal_path=start_path,
        terminal_journal_path=terminal_path,
    )

    assert raw_batch.batch_decision == "INTERRUPTED"
    assert raw_batch.started_slot_count == 1
    assert raw_batch.terminal_record_count == 0
    assert raw_batch.unreconciled_started_slot_count == 1
    assert len(raw_batch.unreconciled_starts) == 1

    assert receipt.batch_decision == "INTERRUPTED"
    assert receipt.primary_execution_complete is False
    assert receipt.started_slot_count == 1
    assert receipt.terminal_record_count == 0
    assert receipt.unreconciled_started_slot_count == 1
    assert receipt.terminal_journal_present is False
    assert receipt.terminal_journal_sha256 is None

    with pytest.raises(
        B0AuthorizationError,
        match="cannot resume or rerun",
    ):
        asyncio.run(
            execute_primary_batch_with_objects(
                repo_root=ROOT,
                specimen=specimen,
                authorization=authorization,
                coverage=coverage,
                fixture=fixture,
                projection=projection,
                pipeline=_RefusalPipeline(),
                execution_commit_sha="a" * 40,
                runner_source_sha256="b" * 64,
                index_loader_source_sha256="c" * 64,
                start_journal_path=start_path,
                terminal_journal_path=terminal_path,
            )
        )


def test_existing_primary_evidence_blocks_fresh_run(tmp_path: Path) -> None:
    relative = Path(
        "evidence_vault/eval_reports/"
        "phase5_b0_primary_start_journal_v1.jsonl"
    )
    existing = tmp_path / relative
    existing.parent.mkdir(parents=True)
    existing.write_text("{}\n", encoding="utf-8")

    with pytest.raises(
        B0AuthorizationError,
        match="execution cannot continue or rerun",
    ):
        _require_fresh_execution_paths(tmp_path)


def test_runner_never_requires_live_provider_credentials() -> None:
    _specimen, authorization, _coverage, fixture, _projection = _objects()
    config, _pipeline = build_phase5_b0_primary_pipeline(
        ROOT,
        fixture=fixture,
    )

    assert authorization.live_provider_calls_authorized == 0
    assert config.provider.adapter_id == "replay-provider-v1"


def test_ci_qualification_does_not_call_private_fixture_preflight() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = "preflight_specimen" + "("
    assert forbidden not in source
