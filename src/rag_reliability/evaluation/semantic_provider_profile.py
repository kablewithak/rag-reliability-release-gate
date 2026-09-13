"""Canonical secret-free Phase 5 semantic-provider profile."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from rag_reliability.config.identity import ProviderConfig
from rag_reliability.config.provider_binding import SemanticProviderBinding
from rag_reliability.contracts.base import ContractModel, Sha256

_ENDPOINT = (
    "https://api-ap-southeast-1.modelarts-maas.com/"
    "openai/v1/chat/completions"
)
_MODEL_ID = "glm-5.2"
_API_KEY_ENV_VAR = "HUAWEI_MAAS_API_KEY"


class Phase5SemanticProviderProfileV1(ContractModel):
    """Exact semantic-provider configuration intended for Phase 5 qualification."""

    profile_version: Literal[
        "phase5-semantic-provider-profile-v1"
    ] = "phase5-semantic-provider-profile-v1"

    binding: SemanticProviderBinding
    provider_config: ProviderConfig

    binding_configuration_id: Sha256
    provider_configuration_id: Sha256

    required_live_probe_ids: tuple[
        Literal["context-a", "context-b", "refusal"],
        Literal["context-a", "context-b", "refusal"],
        Literal["context-a", "context-b", "refusal"],
    ]

    generation_is_context_sensitive: Literal[True] = True
    credential_value_persisted: Literal[False] = False
    raw_provider_payload_persisted: Literal[False] = False

    baseline_execution_authorized: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_profile(self) -> Self:
        if self.binding.adapter_id != self.provider_config.adapter_id:
            raise ValueError(
                "semantic binding adapter_id does not match provider config"
            )

        if self.binding.model_id != self.provider_config.model_id:
            raise ValueError(
                "semantic binding model_id does not match provider config"
            )

        if self.provider_config.max_retries != 0:
            raise ValueError(
                "Phase 5 semantic provider profile requires max_retries=0"
            )

        if (
            self.binding_configuration_id
            != self.binding.configuration_id
        ):
            raise ValueError(
                "binding_configuration_id does not match canonical binding"
            )

        if (
            self.provider_configuration_id
            != self.provider_config.configuration_id
        ):
            raise ValueError(
                "provider_configuration_id does not match canonical config"
            )

        if self.required_live_probe_ids != (
            "context-a",
            "context-b",
            "refusal",
        ):
            raise ValueError(
                "required live semantic-provider probe set drifted"
            )

        if self.baseline_execution_authorized:
            raise ValueError(
                "semantic provider profile cannot authorize B0"
            )

        if self.held_out_outcomes_exposed:
            raise ValueError(
                "semantic provider profile cannot expose HELD_OUT outcomes"
            )

        return self


def build_phase5_semantic_provider_binding(
) -> SemanticProviderBinding:
    """Build the exact secret-free semantic-provider binding."""

    return SemanticProviderBinding(
        model_id=_MODEL_ID,
        endpoint_url=_ENDPOINT,
        api_key_env_var=_API_KEY_ENV_VAR,
    )


def build_phase5_semantic_provider_config(
) -> ProviderConfig:
    """Build the exact runtime provider configuration used for qualification."""

    return ProviderConfig(
        adapter_id="openai-compatible-json-v1",
        model_id=_MODEL_ID,
        timeout_ms=30000,
        max_retries=0,
    )


def build_phase5_semantic_provider_profile_v1(
) -> Phase5SemanticProviderProfileV1:
    """Build the still-unqualified semantic-provider profile."""

    binding = build_phase5_semantic_provider_binding()
    provider_config = build_phase5_semantic_provider_config()

    return Phase5SemanticProviderProfileV1(
        binding=binding,
        provider_config=provider_config,
        binding_configuration_id=binding.configuration_id,
        provider_configuration_id=provider_config.configuration_id,
        required_live_probe_ids=(
            "context-a",
            "context-b",
            "refusal",
        ),
    )
