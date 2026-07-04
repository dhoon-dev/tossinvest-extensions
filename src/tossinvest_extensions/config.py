"""Configuration defaults and immutable client configuration."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from ._version import __version__

DEFAULT_BASE_URL = "https://wts-info-api.tossinvest.com"
DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_USER_AGENT = f"tossinvest-extensions/{__version__}"


@dataclass(frozen=True, slots=True)
class TossInvestExtensionsConfig:
    """Resolved settings shared by sync and async extension clients."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float | httpx.Timeout = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    user_agent: str = DEFAULT_USER_AGENT
