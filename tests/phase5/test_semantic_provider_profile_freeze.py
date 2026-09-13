from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.evaluation.semantic_provider_profile_freeze import (
    materialize_phase5_semantic_provider_profile_freeze,
)

ROOT = Path(__file__).resolve().parents[2]

PROFILE_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_semantic_provider_profile_v1.json"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase5_semantic_provider_profile_freeze_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_materialization_binds_exact_profile_bytes() -> None:
    (
        profile,
        profile_sha256,
        receipt,
        receipt_sha256,
    ) = (
        materialize_phase5_semantic_provider_profile_freeze(
            ROOT
        )
    )

    assert profile_sha256 == _sha256(
        PROFILE_PATH
    )
    assert receipt.profile_sha256 == profile_sha256
    assert receipt.receipt_version == (
        "phase5-semantic-provider-profile-freeze-v1"
    )
    assert receipt_sha256 == _sha256(
        RECEIPT_PATH
    )

    assert profile.baseline_execution_authorized is False
    assert receipt.profile_frozen is True
    assert receipt.live_qualification_satisfied is False
    assert receipt.baseline_execution_authorized is False


def test_freeze_binds_canonical_component_identities() -> None:
    (
        profile,
        _profile_sha256,
        receipt,
        _receipt_sha256,
    ) = (
        materialize_phase5_semantic_provider_profile_freeze(
            ROOT
        )
    )

    assert (
        receipt.binding_configuration_id
        == profile.binding.configuration_id
    )
    assert (
        receipt.provider_configuration_id
        == profile.provider_config.configuration_id
    )


def test_freeze_preserves_secret_and_held_out_boundaries() -> None:
    (
        _profile,
        _profile_sha256,
        receipt,
        _receipt_sha256,
    ) = (
        materialize_phase5_semantic_provider_profile_freeze(
            ROOT
        )
    )

    assert receipt.credential_value_persisted is False
    assert receipt.raw_provider_payload_persisted is False
    assert receipt.held_out_outcomes_exposed is False
    assert receipt.release_eligible is False


def test_materialization_is_deterministic() -> None:
    first = (
        materialize_phase5_semantic_provider_profile_freeze(
            ROOT
        )
    )
    second = (
        materialize_phase5_semantic_provider_profile_freeze(
            ROOT
        )
    )

    assert first[1] == second[1]
    assert first[3] == second[3]
