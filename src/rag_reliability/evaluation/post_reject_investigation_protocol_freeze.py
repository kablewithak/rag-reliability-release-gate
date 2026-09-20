"""Freeze the Phase 5 post-reject investigation protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.post_reject_investigation_protocol import (
    Phase5PostRejectInvestigationProtocolV1,
    build_phase5_post_reject_investigation_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_investigation_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_investigation_protocol_freeze_v1.json"
)


class Phase5PostRejectInvestigationProtocolFreezeReceipt(ContractModel):
    receipt_version: Literal["phase5-post-reject-investigation-protocol-freeze-v1"] = (
        "phase5-post-reject-investigation-protocol-freeze-v1"
    )

    protocol_version: Literal["phase5-post-reject-investigation-protocol-v1"] = (
        "phase5-post-reject-investigation-protocol-v1"
    )

    protocol_sha256: Sha256
    protocol_frozen: Literal[True] = True

    failure_specific_development_evidence_opened: Literal[False] = False
    fresh_confirmation_materialized: Literal[False] = False
    fresh_confirmation_frozen: Literal[False] = False
    development_spent_for_future_confirmation: Literal[False] = False

    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_boundary(self) -> Self:
        if self.failure_specific_development_evidence_opened:
            raise ValueError("freeze must precede DEVELOPMENT failure localization")
        if self.fresh_confirmation_materialized or self.fresh_confirmation_frozen:
            raise ValueError("freeze must precede fresh confirmation authoring")
        if self.development_spent_for_future_confirmation:
            raise ValueError("DEVELOPMENT is spent only when localization starts")
        if self.held_out_outcomes_exposed:
            raise ValueError("HELD_OUT must remain sealed")
        return self


def materialize_phase5_post_reject_investigation_protocol_freeze(
    repo_root: Path,
) -> tuple[
    Phase5PostRejectInvestigationProtocolV1,
    str,
    Phase5PostRejectInvestigationProtocolFreezeReceipt,
    str,
]:
    protocol = build_phase5_post_reject_investigation_protocol_v1()

    protocol_sha256 = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5PostRejectInvestigationProtocolFreezeReceipt(
        protocol_sha256=protocol_sha256,
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )

    return protocol, protocol_sha256, receipt, receipt_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    (
        protocol,
        protocol_sha256,
        _receipt,
        receipt_sha256,
    ) = materialize_phase5_post_reject_investigation_protocol_freeze(repo_root)

    print(f"PHASE5_POST_REJECT_PROTOCOL_SHA256={protocol_sha256}")
    print(f"PHASE5_POST_REJECT_FRESH_CONFIRMATION_ROLE={protocol.fresh_confirmation.role_id}")
    print(
        "PHASE5_POST_REJECT_FRESH_CONFIRMATION_SHAPE="
        f"cases:{protocol.fresh_confirmation.case_count},"
        f"clusters:{protocol.fresh_confirmation.cluster_count},"
        f"answerable:{protocol.fresh_confirmation.answerable_case_count},"
        f"refusal:{protocol.fresh_confirmation.refusal_case_count}"
    )
    print(
        "PHASE5_POST_REJECT_FAILURE_LOCALIZATION_STARTED="
        f"{str(protocol.failure_localization_started).lower()}"
    )
    print(f"PHASE5_POST_REJECT_HELD_OUT_EXPOSED={str(protocol.held_out.outcomes_exposed).lower()}")
    print(f"PHASE5_POST_REJECT_FREEZE_SHA256={receipt_sha256}")


if __name__ == "__main__":
    main()
