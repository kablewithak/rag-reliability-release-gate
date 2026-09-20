from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.post_reject_confirmation_freeze import (
    materialize_phase5_post_reject_confirmation_freeze,
)

ROOT = Path(__file__).resolve().parents[2]
FREEZE_PATH = ROOT / "artifacts" / "development" / "phase5_post_reject_confirmation_freeze_v1.json"


def test_fresh_confirmation_freeze_binds_exact_bytes() -> None:
    _suite, suite_sha, receipt, freeze_sha = materialize_phase5_post_reject_confirmation_freeze(
        ROOT
    )
    suite_path = (
        ROOT / "artifacts" / "development" / "phase5_post_reject_confirmation_cases_v1.json"
    )
    assert suite_sha == hashlib.sha256(suite_path.read_bytes()).hexdigest()
    assert receipt.suite_sha256 == suite_sha
    assert freeze_sha == hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest()


def test_fresh_confirmation_freeze_unlocks_localization_precondition() -> None:
    _suite, _suite_sha, receipt, _freeze_sha = materialize_phase5_post_reject_confirmation_freeze(
        ROOT
    )
    assert receipt.fresh_confirmation_materialized is True
    assert receipt.fresh_confirmation_frozen is True
    assert receipt.failure_localization_activation_condition_satisfied is True
    assert receipt.failure_specific_development_evidence_opened is False
    assert receipt.failure_localization_started is False
    assert receipt.development_spent_for_future_confirmation is False
    assert receipt.held_out_case_content_read is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.provider_invoked is False
    assert receipt.b0_executed is False
