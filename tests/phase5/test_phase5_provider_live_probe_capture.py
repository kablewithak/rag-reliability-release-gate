from __future__ import annotations

from rag_reliability.evaluation.provider_live_probe import LiveProbeReceipt
from rag_reliability.evaluation.provider_live_probe_capture import (
    _http_error_attempt,
    _success_attempt,
)
from rag_reliability.evaluation.semantic_provider_profile import (
    build_phase5_semantic_provider_binding,
    build_phase5_semantic_provider_config,
)
from rag_reliability.runtime.http_transport import ProviderHttpStatusError


def test_success_attempt_preserves_only_probe_verdict_metadata() -> None:
    binding = build_phase5_semantic_provider_binding()
    provider_config = build_phase5_semantic_provider_config()

    original = LiveProbeReceipt(
        probe_id="refusal",
        binding_configuration_id=binding.configuration_id,
        provider_configuration_id=provider_config.configuration_id,
        expected_decision="refusal",
        observed_decision="refusal",
        marker_match=False,
        citation_match=False,
        refusal_reason_match=True,
    )

    receipt = _success_attempt(original)

    assert receipt.outcome == "PASS"
    assert receipt.probe_passed is True
    assert receipt.observed_decision == "refusal"
    assert receipt.refusal_reason_match is True
    assert receipt.http_status_code is None
    assert receipt.provider_error_code is None
    assert receipt.normalized_throttle_category is None
    assert receipt.retry_after is None

    assert receipt.live_qualification_satisfied is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False


def test_http_error_attempt_records_sanitized_throttle_metadata() -> None:
    error = ProviderHttpStatusError(
        429,
        provider_error_code="ModelArts.81116",
        rate_limit_kind="scaling_protection",
        retry_after="60",
    )

    receipt = _http_error_attempt(
        probe_id="refusal",
        error=error,
    )

    assert receipt.outcome == "HTTP_ERROR"
    assert receipt.probe_passed is False
    assert receipt.http_status_code == 429
    assert receipt.provider_error_code == "ModelArts.81116"
    assert receipt.normalized_throttle_category == "scaling_protection"
    assert receipt.retry_after == "60"

    assert receipt.raw_request_payload_persisted is False
    assert receipt.raw_provider_payload_persisted is False
    assert receipt.raw_provider_error_body_persisted is False

    assert receipt.live_qualification_satisfied is False
    assert receipt.baseline_execution_authorized is False
    assert receipt.b0_executed is False
    assert receipt.held_out_outcomes_exposed is False
