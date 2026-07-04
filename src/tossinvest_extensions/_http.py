from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping

import httpx

from ._serialization import join_url, json_body, serialize_query
from .config import TossInvestExtensionsConfig
from .errors import (
    TossInvestExtensionsAPIError,
    TossInvestExtensionsHTTPError,
    TossInvestExtensionsRateLimitError,
)

SAFE_RETRY_METHODS = {"GET", "HEAD", "OPTIONS"}
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
DEFAULT_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 30.0


class SyncHTTPClient:
    """Internal synchronous HTTP adapter shared by public resources."""

    def __init__(
        self,
        config: TossInvestExtensionsConfig,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.config = config
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=config.timeout)

    @property
    def is_closed(self) -> bool:
        """Return whether the owned or injected sync HTTP client is closed."""
        return self._client.is_closed

    def close(self) -> None:
        """Close the owned sync HTTP client, leaving injected clients open."""
        if self._owns_client:
            self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object | None] | None = None,
        json: object | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> object | None:
        """Send a sync API request with retry and error mapping."""
        method = method.upper()
        attempt = 0
        while True:
            response = self._send(method, path, params=params, json=json, headers=headers)
            if response.status_code < 400:
                return parse_success_response(response)
            if _should_retry(method, response.status_code, attempt, self.config.max_retries):
                _sleep_before_retry(response, attempt)
                attempt += 1
                continue
            raise_api_error(response, endpoint=path)

    def _send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object | None] | None,
        json: object | None,
        headers: Mapping[str, str] | None,
    ) -> httpx.Response:
        request_headers = self._headers()
        if headers:
            request_headers.update(headers)
        try:
            return self._client.request(
                method,
                join_url(self.config.base_url, path),
                params=serialize_query(params),
                json=json_body(json),
                headers=request_headers,
            )
        except httpx.TransportError as exc:
            raise TossInvestExtensionsHTTPError(
                f"TossInvest web API HTTP transport failed for {method} {path}.",
                endpoint=path,
            ) from exc

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        }


class AsyncHTTPClient:
    """Internal asynchronous HTTP adapter shared by public resources."""

    def __init__(
        self,
        config: TossInvestExtensionsConfig,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=config.timeout)

    @property
    def is_closed(self) -> bool:
        """Return whether the owned or injected async HTTP client is closed."""
        return self._client.is_closed

    async def close(self) -> None:
        """Close the owned async HTTP client, leaving injected clients open."""
        if self._owns_client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object | None] | None = None,
        json: object | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> object | None:
        """Send an async API request with retry and error mapping."""
        method = method.upper()
        attempt = 0
        while True:
            response = await self._send(method, path, params=params, json=json, headers=headers)
            if response.status_code < 400:
                return parse_success_response(response)
            if _should_retry(method, response.status_code, attempt, self.config.max_retries):
                await _async_sleep_before_retry(response, attempt)
                attempt += 1
                continue
            raise_api_error(response, endpoint=path)

    async def _send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object | None] | None,
        json: object | None,
        headers: Mapping[str, str] | None,
    ) -> httpx.Response:
        request_headers = self._headers()
        if headers:
            request_headers.update(headers)
        try:
            return await self._client.request(
                method,
                join_url(self.config.base_url, path),
                params=serialize_query(params),
                json=json_body(json),
                headers=request_headers,
            )
        except httpx.TransportError as exc:
            raise TossInvestExtensionsHTTPError(
                f"TossInvest web API HTTP transport failed for {method} {path}.",
                endpoint=path,
            ) from exc

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        }


def parse_success_response(response: httpx.Response) -> object | None:
    """Parse a successful TossInvest web API response."""
    if not response.content:
        return None
    data = response.json()
    if isinstance(data, dict) and "result" in data:
        return data["result"]
    return data


def raise_api_error(response: httpx.Response, *, endpoint: str) -> None:
    """Raise a sanitized SDK exception for a non-success response."""
    body = _safe_response_body(response)
    api_error = _extract_error_object(body)
    api_code = _string_or_none(api_error.get("code") or api_error.get("errorCode"))
    api_message = _string_or_none(api_error.get("message") or api_error.get("displayMessage"))
    message = f"TossInvest web API request failed with status {response.status_code}."
    if api_code is not None:
        message = (
            f"TossInvest web API request failed with status {response.status_code} "
            f"and code {api_code}."
        )
    error_type: type[TossInvestExtensionsAPIError]
    if response.status_code == 429:
        error_type = TossInvestExtensionsRateLimitError
    else:
        error_type = TossInvestExtensionsAPIError
    raise error_type(
        message,
        status_code=response.status_code,
        response_body=body,
        endpoint=endpoint,
        api_code=api_code,
        api_message=api_message,
        response_headers=response.headers,
    )


def _safe_response_body(response: httpx.Response) -> object | None:
    try:
        return response.json()
    except ValueError:
        return response.text


def _extract_error_object(body: object | None) -> dict[str, object]:
    if not isinstance(body, dict):
        return {}
    error = body.get("error")
    if isinstance(error, dict):
        return {str(key): value for key, value in error.items()}
    result = body.get("result")
    if isinstance(result, dict):
        result_error = result.get("error")
        if isinstance(result_error, dict):
            return {str(key): value for key, value in result_error.items()}
    return {str(key): value for key, value in body.items()}


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _should_retry(method: str, status_code: int, attempt: int, max_retries: int) -> bool:
    return (
        method in SAFE_RETRY_METHODS and status_code in RETRYABLE_STATUSES and attempt < max_retries
    )


def _sleep_before_retry(response: httpx.Response, attempt: int) -> None:
    time.sleep(_retry_delay(response, attempt))


async def _async_sleep_before_retry(response: httpx.Response, attempt: int) -> None:
    await asyncio.sleep(_retry_delay(response, attempt))


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    for header in ("retry-after", "x-ratelimit-reset"):
        delay = _retry_header_delay(response.headers.get(header))
        if delay is not None:
            return delay
    return min(MAX_RETRY_DELAY, DEFAULT_RETRY_DELAY * (2**attempt))


def _retry_header_delay(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None
