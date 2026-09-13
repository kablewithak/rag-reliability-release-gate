"""Freeze the Phase 5 semantic-provider profile without authorizing B0."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.semantic_provider_profile import (
    Phase5SemanticProviderProfileV1,
    build_phase5_semantic_provider_profile_v1,
)

_PROFILE_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_semantic_provider_profile_v1.json"
)

_FREEZE_RECEIPT_PATH = (
    Path("artifacts")
    / "development"
    / "phase5_semantic_provider_profile_freeze_v1.json"
)

_PROFILE_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "evaluation"
    / "semantic_provider_profile.py"
)

_PROVIDER_BINDING_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "config"
    / "provider_binding.py"
)

_SEMANTIC_PROVIDER_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "runtime"
    / "semantic_provider.py"
)

_LIVE_PROBE_SOURCE_PATH = (
    Path("src")
    / "rag_reliability"
    / "evaluation"
    / "provider_live_probe.py"
)


class Phase5SemanticProviderProfileFreezeReceipt(ContractModel):
    """Custody receipt for the exact secret-free semantic-provider profile."""

    receipt_version: Literal[
        "phase5-semantic-provider-profile-freeze-v1"
    ] = "phase5-semantic-provider-profile-freeze-v1"

    profile_version: Literal[
        "phase5-semantic-provider-profile-v1"
    ] = "phase5-semantic-provider-profile-v1"

    profile_sha256: Sha256
    binding_configuration_id: Sha256
    provider_configuration_id: Sha256

    profile_source_sha256: Sha256
    provider_binding_source_sha256: Sha256
    semantic_provider_source_sha256: Sha256
    live_probe_source_sha256: Sha256

    profile_frozen: Literal[True] = True
    live_qualification_required: Literal[True] = True
    live_qualification_satisfied: Literal[False] = False

    credential_value_persisted: Literal[False] = False
    raw_provider_payload_persisted: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_freeze_boundary(self) -> Self:
        if self.live_qualification_satisfied:
            raise ValueError(
                "profile freeze cannot claim live qualification"
            )

        if self.baseline_execution_authorized:
            raise ValueError(
                "semantic provider profile freeze cannot authorize B0"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "semantic provider profile freeze cannot expose HELD_OUT outcomes"
            )

        return self


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def materialize_phase5_semantic_provider_profile_freeze(
    repo_root: Path,
) -> tuple[
    Phase5SemanticProviderProfileV1,
    str,
    Phase5SemanticProviderProfileFreezeReceipt,
    str,
]:
    """Materialize exact profile bytes and an external freeze receipt."""

    profile = build_phase5_semantic_provider_profile_v1()

    if profile.baseline_execution_authorized:
        raise ValueError(
            "semantic provider profile unexpectedly authorizes B0"
        )

    if profile.held_out_outcomes_exposed:
        raise ValueError(
            "HELD_OUT outcomes became exposed before profile freeze"
        )

    profile_sha256 = write_json_with_sha256(
        repo_root / _PROFILE_PATH,
        profile,
    )

    receipt = Phase5SemanticProviderProfileFreezeReceipt(
        profile_sha256=profile_sha256,
        binding_configuration_id=(
            profile.binding_configuration_id
        ),
        provider_configuration_id=(
            profile.provider_configuration_id
        ),
        profile_source_sha256=_sha256_file(
            repo_root / _PROFILE_SOURCE_PATH
        ),
        provider_binding_source_sha256=_sha256_file(
            repo_root / _PROVIDER_BINDING_SOURCE_PATH
        ),
        semantic_provider_source_sha256=_sha256_file(
            repo_root / _SEMANTIC_PROVIDER_SOURCE_PATH
        ),
        live_probe_source_sha256=_sha256_file(
            repo_root / _LIVE_PROBE_SOURCE_PATH
        ),
    )

    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_RECEIPT_PATH,
        receipt,
    )

    return (
        profile,
        profile_sha256,
        receipt,
        receipt_sha256,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    (
        profile,
        profile_sha256,
        receipt,
        receipt_sha256,
    ) = (
        materialize_phase5_semantic_provider_profile_freeze(
            repo_root
        )
    )

    print(
        "PHASE5_SEMANTIC_PROVIDER_PROFILE_VERSION="
        f"{profile.profile_version}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_PROFILE_SHA256="
        f"{profile_sha256}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_PROFILE_FROZEN="
        f"{str(receipt.profile_frozen).lower()}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_LIVE_QUALIFICATION_SATISFIED="
        f"{str(receipt.live_qualification_satisfied).lower()}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED="
        f"{str(receipt.baseline_execution_authorized).lower()}"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED="
        f"{str(receipt.held_out_outcomes_exposed).lower()}"
    )
    print(
        "PHASE5_SEMANTIC_PROVIDER_PROFILE_FREEZE_RECEIPT_SHA256="
        f"{receipt_sha256}"
    )


if __name__ == "__main__":
    main()
