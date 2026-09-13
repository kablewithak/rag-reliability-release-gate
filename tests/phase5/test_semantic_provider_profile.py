from __future__ import annotations

from rag_reliability.evaluation.semantic_provider_profile import (
    build_phase5_semantic_provider_binding,
    build_phase5_semantic_provider_config,
    build_phase5_semantic_provider_profile_v1,
)


def test_profile_uses_exact_live_qualification_configuration() -> None:
    profile = build_phase5_semantic_provider_profile_v1()

    assert profile.binding.model_id == "glm-5.2"
    assert (
        profile.binding.endpoint_url
        == "https://api-ap-southeast-1.modelarts-maas.com/"
        "openai/v1/chat/completions"
    )
    assert (
        profile.binding.api_key_env_var
        == "HUAWEI_MAAS_API_KEY"
    )

    assert (
        profile.provider_config.adapter_id
        == "openai-compatible-json-v1"
    )
    assert profile.provider_config.model_id == "glm-5.2"
    assert profile.provider_config.timeout_ms == 30000
    assert profile.provider_config.max_retries == 0


def test_profile_identity_matches_canonical_components() -> None:
    profile = build_phase5_semantic_provider_profile_v1()

    assert (
        profile.binding_configuration_id
        == profile.binding.configuration_id
    )
    assert (
        profile.provider_configuration_id
        == profile.provider_config.configuration_id
    )


def test_profile_builders_are_deterministic() -> None:
    first_binding = build_phase5_semantic_provider_binding()
    second_binding = build_phase5_semantic_provider_binding()

    first_config = build_phase5_semantic_provider_config()
    second_config = build_phase5_semantic_provider_config()

    assert (
        first_binding.configuration_id
        == second_binding.configuration_id
    )
    assert (
        first_config.configuration_id
        == second_config.configuration_id
    )


def test_profile_contains_no_credential_value() -> None:
    profile = build_phase5_semantic_provider_profile_v1()
    payload = profile.model_dump(mode="json")

    assert "api_key" not in payload
    assert (
        payload["binding"]["api_key_env_var"]
        == "HUAWEI_MAAS_API_KEY"
    )
    assert profile.credential_value_persisted is False
    assert profile.raw_provider_payload_persisted is False


def test_profile_does_not_authorize_b0() -> None:
    profile = build_phase5_semantic_provider_profile_v1()

    assert profile.generation_is_context_sensitive is True
    assert profile.baseline_execution_authorized is False
    assert profile.held_out_outcomes_exposed is False
    assert profile.release_eligible is False
    assert profile.required_live_probe_ids == (
        "context-a",
        "context-b",
        "refusal",
    )
