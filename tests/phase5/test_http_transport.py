from __future__ import annotations

import asyncio
import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

import rag_reliability.runtime.http_transport as transport_module
from rag_reliability.runtime.http_transport import (
    ProviderCredentialMissingError,
    ProviderHttpStatusError,
    StdlibJsonTransport,
)


class FakeResponse:
    def __init__(
        self,
        payload: dict[str, object],
    ) -> None:
        self._body = json.dumps(
            payload
        ).encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_transport_requires_environment_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "RAG_TEST_API_KEY",
        raising=False,
    )

    transport = StdlibJsonTransport()

    with pytest.raises(
        ProviderCredentialMissingError,
        match="RAG_TEST_API_KEY",
    ):
        asyncio.run(
            transport.post_json(
                endpoint_url=(
                    "https://example.invalid/v1/chat/completions"
                ),
                api_key_env_var="RAG_TEST_API_KEY",
                payload={"model": "test-model"},
                timeout_ms=1000,
            )
        )


def test_transport_returns_decoded_json_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "RAG_TEST_API_KEY",
        "test-secret-value",
    )

    def fake_urlopen(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        assert timeout == 1.0
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": "{}"
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(
        transport_module,
        "urlopen",
        fake_urlopen,
    )

    result = asyncio.run(
        StdlibJsonTransport().post_json(
            endpoint_url=(
                "https://example.invalid/v1/chat/completions"
            ),
            api_key_env_var="RAG_TEST_API_KEY",
            payload={"model": "test-model"},
            timeout_ms=1000,
        )
    )

    assert "choices" in result


def test_http_error_exposes_status_not_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "do-not-leak-this-secret"

    monkeypatch.setenv(
        "RAG_TEST_API_KEY",
        secret,
    )

    def fake_urlopen(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        raise HTTPError(
            url="https://example.invalid",
            code=429,
            msg="Too Many Requests",
            hdrs={
                "Retry-After": "60",
            },
            fp=BytesIO(
                json.dumps(
                    {
                        "error_code": "ModelArts.81114",
                        "error_msg": (
                            "Too many requests, "
                            "the rate limit is 1000 "
                            "tokens per minute."
                        ),
                    }
                ).encode("utf-8")
            ),
        )

    monkeypatch.setattr(
        transport_module,
        "urlopen",
        fake_urlopen,
    )

    with pytest.raises(
        ProviderHttpStatusError,
    ) as exc_info:
        asyncio.run(
            StdlibJsonTransport().post_json(
                endpoint_url=(
                    "https://example.invalid/v1/chat/completions"
                ),
                api_key_env_var="RAG_TEST_API_KEY",
                payload={"model": "test-model"},
                timeout_ms=1000,
            )
        )

    assert exc_info.value.status_code == 429
    assert (
        exc_info.value.provider_error_code
        == "ModelArts.81114"
    )
    assert exc_info.value.rate_limit_kind == "tpm"
    assert exc_info.value.retry_after == "60"
    assert secret not in str(
        exc_info.value
    )
