"""Secret-free binding for a context-sensitive semantic provider."""

from typing import Literal

from pydantic import Field

from rag_reliability.config.identity import CanonicalConfigModel
from rag_reliability.contracts.base import NonEmptyStr


class SemanticProviderBinding(CanonicalConfigModel):
    """Frozen-capable provider details that never contain credential values."""

    binding_version: Literal[
        "semantic-provider-binding-v1"
    ] = "semantic-provider-binding-v1"

    adapter_id: Literal[
        "openai-compatible-json-v1"
    ] = "openai-compatible-json-v1"

    model_id: NonEmptyStr
    endpoint_url: NonEmptyStr

    api_key_env_var: str = Field(
        min_length=1,
        pattern=r"^[A-Z][A-Z0-9_]*$",
    )

    prompt_version: Literal[
        "rag-grounded-provider-v1"
    ] = "rag-grounded-provider-v1"

    response_contract_version: Literal[
        "provider-decision-json-v1"
    ] = "provider-decision-json-v1"

    temperature: Literal[0] = 0

    max_output_tokens: int = Field(
        default=768,
        ge=1,
        le=4096,
    )
