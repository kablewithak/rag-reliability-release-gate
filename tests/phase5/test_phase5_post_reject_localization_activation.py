from __future__ import annotations

import hashlib
from functools import cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_reliability.evaluation.post_reject_localization_activation import (
    Phase5PostRejectLocalizationActivationV1,
    materialize_phase5_post_reject_localization_activation,
)

ROOT = Path(__file__).resolve().parents[2]
ACTIVATION_PATH = (
    ROOT / "artifacts" / "development" / "phase5_post_reject_localization_activation_v1.json"
)


@cache
def _materialized() -> tuple[
    Phase5PostRejectLocalizationActivationV1,
    str,
]:
    return materialize_phase5_post_reject_localization_activation(ROOT)


def test_localization_activation_marks_development_spent() -> None:
    receipt, _digest = _materialized()

    assert receipt.fresh_confirmation_materialized is True
    assert receipt.fresh_confirmation_frozen is True
    assert receipt.localization_activation_condition_satisfied is True

    assert receipt.failure_localization_started is True
    assert receipt.development_spent_for_future_confirmation is True

    assert (
        receipt.development_role_after_activation == "diagnostic_only_spent_for_future_confirmation"
    )


def test_localization_activation_precedes_failure_inspection() -> None:
    receipt, _digest = _materialized()

    assert receipt.failure_specific_development_evidence_opened is False
    assert receipt.failure_specific_case_ids_opened is False
    assert receipt.failure_specific_gold_opened is False

    assert receipt.held_out_case_content_read is False
    assert receipt.held_out_outcomes_exposed is False


def test_localization_activation_preserves_nonclaims() -> None:
    receipt, _digest = _materialized()

    assert receipt.candidate_retuning_authorized is False
    assert receipt.parameter_sweep_authorized is False
    assert receipt.new_candidate_execution_authorized is False
    assert receipt.provider_invocation_authorized is False
    assert receipt.semantic_runtime_configuration_selected is False
    assert receipt.semantic_runtime_configuration_frozen is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False
    assert receipt.release_eligible is False


def test_localization_activation_rejects_held_out_tamper() -> None:
    receipt, _digest = _materialized()
    payload = receipt.model_dump(mode="json")
    payload["held_out_outcomes_exposed"] = True

    with pytest.raises(ValidationError):
        Phase5PostRejectLocalizationActivationV1.model_validate(payload)


def test_localization_activation_artifact_hash_matches_bytes() -> None:
    _receipt, digest = _materialized()

    assert digest == hashlib.sha256(ACTIVATION_PATH.read_bytes()).hexdigest()
