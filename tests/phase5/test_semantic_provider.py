from __future__ import annotations

import asyncio
import json

import pytest

from rag_reliability.config.identity import ProviderConfig
from rag_reliability.config.provider_binding import SemanticProviderBinding
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    RefusalReason,
    SourceState,
)
from rag_reliability.contracts.runtime import (
    ContextBundle,
    ContextItem,
    ProviderRefusalDecision,
    ProviderRequest,
    ProviderResponse,
)
from rag_reliability.runtime.errors import (
    ProviderMalformedResponseError,
    ProviderTimeoutError,
)
from rag_reliability.runtime.semantic_provider import (
    OpenAICompatibleSemanticProvider,
)


def provider_config() -> ProviderConfig:
    return ProviderConfig(
        adapter_id="openai-compatible-json-v1",
        model_id="test-semantic-model",
        timeout_ms=2500,
        max_retries=0,
    )


def provider_binding() -> SemanticProviderBinding:
    return SemanticProviderBinding(
        model_id="test-semantic-model",
        endpoint_url=(
            "https://example.invalid/v1/chat/completions"
        ),
        api_key_env_var="RAG_PROVIDER_API_KEY",
    )


def context() -> ContextBundle:
    item = ContextItem(
        evidence_id="evidence-001",
        source_ids=("source-001",),
        document_ids=("document-001",),
        content=(
            "Requests may include the "
            "X-GitHub-Api-Version header."
        ),
        position=1,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        eligible_as_final_citation=True,
    )

    return ContextBundle(
        query="Which version header may requests include?",
        items=(item,),
        assembled_context=(
            "EVIDENCE: evidence-001\n"
            "Requests may include the "
            "X-GitHub-Api-Version header."
        ),
    )


class FakeTransport:
    def __init__(
        self,
        response: dict[str, object],
    ) -> None:
        self.response = response
        self.calls: list[
            dict[str, object]
        ] = []

    async def post_json(
        self,
        *,
        endpoint_url: str,
        api_key_env_var: str,
        payload: dict[str, object],
        timeout_ms: int,
    ) -> dict[str, object]:
        self.calls.append(
            {
                "endpoint_url": endpoint_url,
                "api_key_env_var": api_key_env_var,
                "payload": payload,
                "timeout_ms": timeout_ms,
            }
        )

        return self.response


class TimeoutTransport:
    async def post_json(
        self,
        *,
        endpoint_url: str,
        api_key_env_var: str,
        payload: dict[str, object],
        timeout_ms: int,
    ) -> dict[str, object]:
        raise TimeoutError("deterministic fake timeout")


def completion(
    decision: dict[str, object],
) -> dict[str, object]:
    return {
        "id": "fake-completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(
                        decision
                    ),
                },
                "finish_reason": "stop",
            }
        ],
    }


def request() -> ProviderRequest:
    return ProviderRequest(
        query="Which version header may requests include?",
        context=context(),
    )


def test_binding_is_secret_free_and_deterministic() -> None:
    binding = provider_binding()

    first = binding.configuration_id
    second = binding.configuration_id

    assert first == second
    assert len(first) == 64

    serialized = binding.canonical_json()

    assert "RAG_PROVIDER_API_KEY" in serialized
    assert "test-secret-value" not in serialized


def test_adapter_preserves_runtime_provider_identity() -> None:
    config = provider_config()
    binding = provider_binding()

    adapter = OpenAICompatibleSemanticProvider(
        config=config,
        binding=binding,
        transport=FakeTransport(
            completion(
                {
                    "decision": "refusal",
                    "reason": "insufficient_evidence",
                    "message": "Insufficient evidence.",
                }
            )
        ),
    )

    assert adapter.configuration_id == config.configuration_id
    assert adapter.binding_id == binding.configuration_id


def test_answer_uses_context_and_exact_evidence_ids() -> None:
    transport = FakeTransport(
        completion(
            {
                "decision": "answer",
                "answer_text": (
                    "Requests may include "
                    "X-GitHub-Api-Version."
                ),
                "cited_evidence_ids": [
                    "evidence-001"
                ],
            }
        )
    )

    adapter = OpenAICompatibleSemanticProvider(
        config=provider_config(),
        binding=provider_binding(),
        transport=transport,
    )

    result = asyncio.run(
        adapter.generate(
            request()
        )
    )

    assert isinstance(
        result,
        ProviderResponse,
    )
    assert result.cited_evidence_ids == (
        "evidence-001",
    )

    assert len(transport.calls) == 1

    call = transport.calls[0]

    assert (
        call["endpoint_url"]
        == "https://example.invalid/v1/chat/completions"
    )
    assert call["api_key_env_var"] == "RAG_PROVIDER_API_KEY"
    assert call["timeout_ms"] == 2500

    payload = call["payload"]

    assert isinstance(
        payload,
        dict,
    )

    serialized_payload = json.dumps(
        payload
    )

    assert "evidence-001" in serialized_payload
    assert "X-GitHub-Api-Version" in serialized_payload
    assert "test-semantic-model" in serialized_payload


def test_adapter_parses_semantic_refusal() -> None:
    adapter = OpenAICompatibleSemanticProvider(
        config=provider_config(),
        binding=provider_binding(),
        transport=FakeTransport(
            completion(
                {
                    "decision": "refusal",
                    "reason": "insufficient_evidence",
                    "message": (
                        "The supplied context does not "
                        "support the requested conclusion."
                    ),
                }
            )
        ),
    )

    result = asyncio.run(
        adapter.generate(
            request()
        )
    )

    assert isinstance(
        result,
        ProviderRefusalDecision,
    )
    assert (
        result.reason
        is RefusalReason.INSUFFICIENT_EVIDENCE
    )


def test_adapter_rejects_citation_outside_context() -> None:
    adapter = OpenAICompatibleSemanticProvider(
        config=provider_config(),
        binding=provider_binding(),
        transport=FakeTransport(
            completion(
                {
                    "decision": "answer",
                    "answer_text": "Unsupported.",
                    "cited_evidence_ids": [
                        "not-in-context"
                    ],
                }
            )
        ),
    )

    with pytest.raises(
        ProviderMalformedResponseError,
        match="provider-decision-json-v1",
    ):
        asyncio.run(
            adapter.generate(
                request()
            )
        )


def test_adapter_rejects_non_json_model_content() -> None:
    adapter = OpenAICompatibleSemanticProvider(
        config=provider_config(),
        binding=provider_binding(),
        transport=FakeTransport(
            {
                "choices": [
                    {
                        "message": {
                            "content": "not-json"
                        }
                    }
                ]
            }
        ),
    )

    with pytest.raises(
        ProviderMalformedResponseError,
        match="provider-decision-json-v1",
    ):
        asyncio.run(
            adapter.generate(
                request()
            )
        )


def test_transport_timeout_becomes_typed_provider_timeout() -> None:
    adapter = OpenAICompatibleSemanticProvider(
        config=provider_config(),
        binding=provider_binding(),
        transport=TimeoutTransport(),
    )

    with pytest.raises(
        ProviderTimeoutError,
        match="transport timed out",
    ):
        asyncio.run(
            adapter.generate(
                request()
            )
        )


def test_adapter_rejects_binding_model_drift() -> None:
    config = provider_config()

    drifted_binding = SemanticProviderBinding(
        model_id="different-model",
        endpoint_url=(
            "https://example.invalid/v1/chat/completions"
        ),
        api_key_env_var="RAG_PROVIDER_API_KEY",
    )

    with pytest.raises(
        ValueError,
        match="model_id",
    ):
        OpenAICompatibleSemanticProvider(
            config=config,
            binding=drifted_binding,
            transport=FakeTransport({}),
        )
