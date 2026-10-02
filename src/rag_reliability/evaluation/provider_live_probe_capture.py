"""Capture one bounded live semantic-provider probe attempt safely."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.provider_live_probe import (
    LiveProbeReceipt,
    ProbeId,
    _run,
)
from rag_reliability.evaluation.semantic_provider_profile import (
    build_phase5_semantic_provider_binding,
    build_phase5_semantic_provider_config,
)
from rag_reliability.runtime.http_transport import ProviderHttpStatusError

AttemptOutcome = Literal["PASS", "HTTP_ERROR"]


class Phase5LiveProviderProbeAttemptV1(ContractModel):
    """Secret-safe receipt for exactly one live provider probe attempt."""

    receipt_version: Literal[
        "phase5-live-provider-probe-attempt-v1"
    ] = "phase5-live-provider-probe-attempt-v1"

    probe_id: ProbeId
    outcome: AttemptOutcome

    binding_configuration_id: Sha256
    provider_configuration_id: Sha256

    probe_call_count: Literal[1] = 1
    automatic_retry_count: Literal[0] = 0

    probe_passed: bool

    observed_decision: Literal["answer", "refusal"] | None = None
    marker_match: bool | None = None
    citation_match: bool | None = None
    refusal_reason_match: bool | None = None

    http_status_code: int | None = Field(default=None, ge=100, le=599)
    provider_error_code: NonEmptyStr | None = None
    normalized_throttle_category: NonEmptyStr | None = None
    retry_after: NonEmptyStr | None = None

    credential_value_persisted: Literal[False] = False
    raw_request_payload_persisted: Literal[False] = False
    raw_provider_payload_persisted: Literal[False] = False
    raw_provider_error_body_persisted: Literal[False] = False

    live_qualification_satisfied: Literal[False] = False
    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_attempt(self) -> Self:
        if self.outcome == "PASS":
            if not self.probe_passed:
                raise ValueError("PASS outcome requires probe_passed=true")
            if self.http_status_code is not None:
                raise ValueError("PASS outcome cannot carry HTTP error status")
            if self.provider_error_code is not None:
                raise ValueError("PASS outcome cannot carry provider error code")
            if self.normalized_throttle_category is not None:
                raise ValueError("PASS outcome cannot carry throttle category")
            if self.retry_after is not None:
                raise ValueError("PASS outcome cannot carry Retry-After")
            if self.observed_decision is None:
                raise ValueError("PASS outcome requires observed decision")
        else:
            if self.probe_passed:
                raise ValueError("HTTP_ERROR outcome requires probe_passed=false")
            if self.http_status_code is None:
                raise ValueError("HTTP_ERROR outcome requires HTTP status")
            if self.observed_decision is not None:
                raise ValueError("HTTP_ERROR outcome cannot claim model decision")

        if (
            self.live_qualification_satisfied
            or self.baseline_execution_authorized
            or self.b0_executed
            or self.held_out_outcomes_exposed
            or self.release_eligible
        ):
            raise ValueError("single probe attempt overclaims downstream state")

        return self


def _success_attempt(
    receipt: LiveProbeReceipt,
) -> Phase5LiveProviderProbeAttemptV1:
    return Phase5LiveProviderProbeAttemptV1(
        probe_id=receipt.probe_id,
        outcome="PASS",
        binding_configuration_id=receipt.binding_configuration_id,
        provider_configuration_id=receipt.provider_configuration_id,
        probe_passed=True,
        observed_decision=receipt.observed_decision,
        marker_match=receipt.marker_match,
        citation_match=receipt.citation_match,
        refusal_reason_match=receipt.refusal_reason_match,
    )


def _http_error_attempt(
    *,
    probe_id: ProbeId,
    error: ProviderHttpStatusError,
) -> Phase5LiveProviderProbeAttemptV1:
    binding = build_phase5_semantic_provider_binding()
    provider_config = build_phase5_semantic_provider_config()

    return Phase5LiveProviderProbeAttemptV1(
        probe_id=probe_id,
        outcome="HTTP_ERROR",
        binding_configuration_id=binding.configuration_id,
        provider_configuration_id=provider_config.configuration_id,
        probe_passed=False,
        http_status_code=error.status_code,
        provider_error_code=error.provider_error_code,
        normalized_throttle_category=error.rate_limit_kind,
        retry_after=error.retry_after,
    )


async def capture_one_probe_attempt(
    probe_id: ProbeId,
) -> Phase5LiveProviderProbeAttemptV1:
    """Execute exactly one live probe with no automatic retry."""

    try:
        receipt = await _run(probe_id)
    except ProviderHttpStatusError as exc:
        return _http_error_attempt(
            probe_id=probe_id,
            error=exc,
        )

    return _success_attempt(receipt)


def materialize_phase5_live_provider_probe_attempt(
    repo_root: Path,
    *,
    probe_id: ProbeId,
) -> tuple[
    Phase5LiveProviderProbeAttemptV1,
    str,
]:
    receipt = asyncio.run(
        capture_one_probe_attempt(probe_id)
    )

    path = (
        repo_root
        / "artifacts"
        / "development"
        / (
            "phase5_live_provider_"
            f"{probe_id.replace('-', '_')}_attempt_v1.json"
        )
    )

    digest = write_json_with_sha256(
        path,
        receipt,
    )

    return receipt, digest


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--probe",
        required=True,
        choices=(
            "context-a",
            "context-b",
            "refusal",
        ),
    )

    args = parser.parse_args()
    probe_id: ProbeId = args.probe

    repo_root = Path(__file__).resolve().parents[3]

    receipt, digest = materialize_phase5_live_provider_probe_attempt(
        repo_root,
        probe_id=probe_id,
    )

    print(f"PHASE5_LIVE_PROBE_ATTEMPT={receipt.probe_id}")
    print(f"PHASE5_LIVE_PROBE_OUTCOME={receipt.outcome}")
    print(
        "PHASE5_LIVE_PROBE_PASS="
        f"{str(receipt.probe_passed).lower()}"
    )

    if receipt.http_status_code is not None:
        print(
            "PHASE5_LIVE_PROBE_HTTP_STATUS="
            f"{receipt.http_status_code}"
        )

    if receipt.provider_error_code is not None:
        print(
            "PHASE5_LIVE_PROBE_PROVIDER_ERROR_CODE="
            f"{receipt.provider_error_code}"
        )

    if receipt.normalized_throttle_category is not None:
        print(
            "PHASE5_LIVE_PROBE_THROTTLE_CATEGORY="
            f"{receipt.normalized_throttle_category}"
        )

    if receipt.retry_after is not None:
        print(
            "PHASE5_LIVE_PROBE_RETRY_AFTER="
            f"{receipt.retry_after}"
        )

    print(
        "PHASE5_LIVE_PROBE_ATTEMPT_SHA256="
        f"{digest}"
    )
    print("PHASE5_LIVE_QUALIFICATION_SATISFIED=false")
    print("PHASE5_BASELINE_EXECUTION_AUTHORIZED=false")
    print("PHASE5_B0_EXECUTED=false")
    print("PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false")


if __name__ == "__main__":
    main()
