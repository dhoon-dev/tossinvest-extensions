"""Exception hierarchy and metadata-bearing HTTP errors."""

from __future__ import annotations

from collections.abc import Mapping


class TossInvestExtensionsError(Exception):
    """Base class for all extension SDK exceptions."""


class TossInvestExtensionsValidationError(TossInvestExtensionsError):
    """Raised before an invalid request is sent."""


class TossInvestExtensionsHTTPError(TossInvestExtensionsError):
    """Raised for HTTP transport failures or non-success API responses.

    Attributes:
        status_code: HTTP status code when a response exists.
        response_body: Parsed JSON body, plain text body, or ``None``.
        endpoint: SDK endpoint path associated with the failed request.
        api_code: Upstream error code when returned by the API.
        api_message: Upstream API message when returned by the API.
        response_headers: Response headers copied without request secrets.

    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: object | None = None,
        endpoint: str | None = None,
        api_code: str | None = None,
        api_message: str | None = None,
        response_headers: Mapping[str, str] | None = None,
    ) -> None:
        """Store sanitized response metadata without exposing request headers."""
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.endpoint = endpoint
        self.api_code = api_code
        self.api_message = api_message
        self.response_headers = dict(response_headers or {})


class TossInvestExtensionsAPIError(TossInvestExtensionsHTTPError):
    """Raised for TossInvest web API error responses."""


class TossInvestExtensionsRateLimitError(TossInvestExtensionsAPIError):
    """Raised when the API returns a rate limit response."""
