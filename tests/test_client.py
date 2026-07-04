from __future__ import annotations

import httpx

from tossinvest_extensions import TossInvestExtensionsClient

from .conftest import make_client


def test_context_manager_closes_owned_client() -> None:
    with make_client() as client:
        assert not client.is_closed

    assert client.is_closed


def test_injected_http_client_is_not_closed() -> None:
    http_client = httpx.Client()
    client = TossInvestExtensionsClient(http_client=http_client)

    client.close()

    assert not http_client.is_closed
    http_client.close()
