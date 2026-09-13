"""Minimal secret-safe JSON HTTP transport for semantic providers."""

from __future__ import annotations

import asyncio
import json
import os
import socket
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rag_reliability.runtime.errors import ProviderMalformedResponseError


class ProviderCredentialMissingError(RuntimeError):
    """Raised when the configured credential environment variable is absent."""


class ProviderHttpStatusError(RuntimeError):
    """Raised for a non-success provider HTTP response."""

    def __init__(
        self,
        status_code: int,
        *,
        provider_error_code: str | None = None,
        rate_limit_kind: str | None = None,
        retry_after: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.provider_error_code = provider_error_code
        self.rate_limit_kind = rate_limit_kind
        self.retry_after = retry_after

        details: list[str] = []

        if provider_error_code is not None:
            details.append(
                f"provider_error_code={provider_error_code}"
            )

        if rate_limit_kind is not None:
            details.append(
                f"rate_limit_kind={rate_limit_kind}"
            )

        if retry_after is not None:
            details.append(
                f"retry_after={retry_after}"
            )

        suffix = (
            f"; {', '.join(details)}"
            if details
            else ""
        )

        super().__init__(
            f"provider HTTP request failed with status "
            f"{status_code}{suffix}"
        )


class ProviderNetworkError(RuntimeError):
    """Raised for a provider network failure other than timeout."""


class StdlibJsonTransport:
    """POST JSON without adding an external HTTP-client dependency."""

    async def post_json(
        self,
        *,
        endpoint_url: str,
        api_key_env_var: str,
        payload: dict[str, object],
        timeout_ms: int,
    ) -> dict[str, object]:
        return await asyncio.to_thread(
            self._post_json_sync,
            endpoint_url=endpoint_url,
            api_key_env_var=api_key_env_var,
            payload=payload,
            timeout_ms=timeout_ms,
        )

    @staticmethod
    def _post_json_sync(
        *,
        endpoint_url: str,
        api_key_env_var: str,
        payload: dict[str, object],
        timeout_ms: int,
    ) -> dict[str, object]:
        api_key = os.environ.get(
            api_key_env_var
        )

        if api_key is None or not api_key.strip():
            raise ProviderCredentialMissingError(
                f"credential environment variable is not set: "
                f"{api_key_env_var}"
            )

        body = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        request = Request(
            endpoint_url,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=timeout_ms / 1000,
            ) as response:
                raw_body = response.read()

        except HTTPError as exc:
            provider_error_code: str | None = None
            rate_limit_kind: str | None = None

            try:
                raw_error = exc.read()
                decoded_error = json.loads(
                    raw_error.decode("utf-8")
                )

                if isinstance(
                    decoded_error,
                    dict,
                ):
                    raw_code = decoded_error.get(
                        "error_code"
                    )
                    raw_message = decoded_error.get(
                        "error_msg"
                    )

                    nested_error = decoded_error.get(
                        "error"
                    )

                    if (
                        raw_code is None
                        and isinstance(
                            nested_error,
                            dict,
                        )
                    ):
                        raw_code = nested_error.get(
                            "code"
                        )

                    if (
                        raw_message is None
                        and isinstance(
                            nested_error,
                            dict,
                        )
                    ):
                        raw_message = nested_error.get(
                            "message"
                        )

                    if isinstance(
                        raw_code,
                        str,
                    ):
                        provider_error_code = raw_code

                    if isinstance(
                        raw_message,
                        str,
                    ):
                        normalized_message = (
                            raw_message.lower()
                        )

                        if (
                            "scaling protection"
                            in normalized_message
                        ):
                            rate_limit_kind = (
                                "scaling_protection"
                            )
                        elif (
                            "tokens per minute"
                            in normalized_message
                        ):
                            rate_limit_kind = "tpm"
                        elif (
                            "times per second"
                            in normalized_message
                            or "qps"
                            in normalized_message
                        ):
                            rate_limit_kind = "qps"
                        elif (
                            "times per minute"
                            in normalized_message
                            or "rpm"
                            in normalized_message
                        ):
                            rate_limit_kind = "rpm"
                        elif (
                            "throttling threshold"
                            in normalized_message
                        ):
                            rate_limit_kind = (
                                "gateway_rate_limit"
                            )

            except (
                AttributeError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):
                pass

            if (
                rate_limit_kind is None
                and provider_error_code
                == "ModelArts.81111"
            ):
                rate_limit_kind = (
                    "tpm_stability_protection"
                )

            if (
                rate_limit_kind is None
                and provider_error_code
                == "ModelArts.81114"
            ):
                rate_limit_kind = "tpm"

            if (
                rate_limit_kind is None
                and provider_error_code
                == "ModelArts.81116"
            ):
                rate_limit_kind = (
                    "scaling_protection"
                )

            retry_after = (
                exc.headers.get("Retry-After")
                if exc.headers is not None
                else None
            )

            raise ProviderHttpStatusError(
                exc.code,
                provider_error_code=(
                    provider_error_code
                ),
                rate_limit_kind=rate_limit_kind,
                retry_after=retry_after,
            ) from exc

        except TimeoutError as exc:
            raise TimeoutError(
                "provider request timed out"
            ) from exc

        except URLError as exc:
            if isinstance(
                exc.reason,
                (TimeoutError, socket.timeout),
            ):
                raise TimeoutError(
                    "provider request timed out"
                ) from exc

            raise ProviderNetworkError(
                "provider network request failed"
            ) from exc

        try:
            decoded = json.loads(
                raw_body.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise ProviderMalformedResponseError(
                "provider HTTP response was not valid JSON"
            ) from exc

        if not isinstance(
            decoded,
            dict,
        ):
            raise ProviderMalformedResponseError(
                "provider HTTP response must be a JSON object"
            )

        return cast(
            dict[str, object],
            decoded,
        )
