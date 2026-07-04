from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from tossinvest_extensions import TossInvestExtensionsAPIError, TossInvestExtensionsRateLimitError

from .conftest import BASE_URL, make_client


def test_api_error_preserves_sanitized_metadata(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}/api/v2/stock-infos/code-or-symbol/000660",
        status_code=500,
        json={"error": {"code": "INTERNAL", "message": "failed"}},
    )
    client = make_client(max_retries=0)

    with pytest.raises(TossInvestExtensionsAPIError) as exc_info:
        client.community.get_stock_info("000660")

    exc = exc_info.value
    assert exc.status_code == 500
    assert exc.api_code == "INTERNAL"
    assert exc.api_message == "failed"
    assert exc.endpoint == "/api/v2/stock-infos/code-or-symbol/000660"


def test_rate_limit_error_type(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}/api/v2/stock-infos/code-or-symbol/000660",
        status_code=429,
        json={"error": {"code": "RATE_LIMIT", "message": "retry later"}},
    )
    client = make_client(max_retries=0)

    with pytest.raises(TossInvestExtensionsRateLimitError):
        client.community.get_stock_info("000660")
