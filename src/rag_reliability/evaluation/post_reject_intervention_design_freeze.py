"""Freeze the Phase 5 post-reject intervention design protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.post_reject_intervention_design_protocol import (
    Phase5PostRejectInterventionDesignProtocolV1,
    build_phase5_post_reject_intervention_design_protocol_v1,
)

_PROTOCOL_PATH = (
    Path("artifacts") / "development" / "phase5_post_reject_intervention_design_protocol_v1.json"
)
_FREEZE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_post_reject_intervention_design_protocol_freeze_v1.json"
)


class Phase5PostRejectInterventionDesignFreezeV1(ContractModel):
    receipt_version: Literal["phase5-post-reject-intervention-design-freeze-v1"] = (
        "phase5-post-reject-intervention-design-freeze-v1"
    )

    protocol_sha256: Sha256
    protocol_frozen: Literal[True] = True

    resolver_candidate_executed: Literal[False] = False
    companion_candidate_executed: Literal[False] = False
    composed_candidate_executed: Literal[False] = False
    fresh_confirmation_executed: Literal[False] = False

    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False
    b0_executed: Literal[False] = False


def materialize_phase5_post_reject_intervention_design_freeze(
    repo_root: Path,
) -> tuple[
    Phase5PostRejectInterventionDesignProtocolV1,
    str,
    Phase5PostRejectInterventionDesignFreezeV1,
    str,
]:
    protocol = build_phase5_post_reject_intervention_design_protocol_v1()
    protocol_sha = write_json_with_sha256(
        repo_root / _PROTOCOL_PATH,
        protocol,
    )

    receipt = Phase5PostRejectInterventionDesignFreezeV1(
        protocol_sha256=protocol_sha,
    )
    freeze_sha = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )

    return protocol, protocol_sha, receipt, freeze_sha


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    protocol, protocol_sha, _receipt, freeze_sha = (
        materialize_phase5_post_reject_intervention_design_freeze(repo_root)
    )

    print(f"PHASE5_INTERVENTION_DESIGN_PROTOCOL_SHA256={protocol_sha}")
    print(f"PHASE5_INTERVENTION_DESIGN_FREEZE_SHA256={freeze_sha}")
    print("PHASE5_INTERVENTION_ORDER=" + ",".join(protocol.experiment_order))
    print(f"PHASE5_RESOLVER_CANDIDATE={protocol.resolver_experiment.experiment_id}")
    print(f"PHASE5_COMPANION_CANDIDATE={protocol.companion_experiment.experiment_id}")
    print("PHASE5_FRESH_CONFIRMATION_EXECUTED=false")
    print("PHASE5_HELD_OUT_EXPOSED=false")
    print("PHASE5_B0_EXECUTED=false")


if __name__ == "__main__":
    main()
