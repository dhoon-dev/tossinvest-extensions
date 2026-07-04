"""Asynchronous TossInvest extension client."""

from __future__ import annotations

from types import TracebackType
from typing import Self

import httpx

from ._http import AsyncHTTPClient
from .config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    TossInvestExtensionsConfig,
)
from .resources.community import AsyncCommunityResource


class AsyncTossInvestExtensionsClient:
    """Asynchronous entry point for TossInvest web API extensions."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: str = DEFAULT_USER_AGENT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = TossInvestExtensionsConfig(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent,
        )
        self._http = AsyncHTTPClient(self.config, http_client=http_client)
        self.community = AsyncCommunityResource(self._http)

    @property
    def is_closed(self) -> bool:
        """Return whether this client owns a closed HTTP transport."""
        return self._http.is_closed

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, object | None] | None = None,
        json: object | None = None,
    ) -> object | None:
        """Send a lower-level request through the async SDK HTTP layer."""
        return await self._http.request(method, path, params=params, json=json)

    async def close(self) -> None:
        """Close the owned async HTTP client if this instance created one."""
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()
