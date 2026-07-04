"""Synchronous TossInvest extension client."""

from __future__ import annotations

from types import TracebackType
from typing import Self

import httpx

from ._http import SyncHTTPClient
from .config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    TossInvestExtensionsConfig,
)
from .resources.community import CommunityResource


class TossInvestExtensionsClient:
    """Synchronous entry point for TossInvest web API extensions."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: str = DEFAULT_USER_AGENT,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.config = TossInvestExtensionsConfig(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent,
        )
        self._http = SyncHTTPClient(self.config, http_client=http_client)
        self.community = CommunityResource(self._http)

    @property
    def is_closed(self) -> bool:
        """Return whether this client owns a closed HTTP transport."""
        return self._http.is_closed

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, object | None] | None = None,
        json: object | None = None,
    ) -> object | None:
        """Send a lower-level request through the SDK HTTP layer."""
        return self._http.request(method, path, params=params, json=json)

    def close(self) -> None:
        """Close the owned HTTP client if this instance created one."""
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
