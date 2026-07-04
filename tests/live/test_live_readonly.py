from __future__ import annotations

import os

import pytest

from tossinvest_extensions import TossInvestExtensionsClient


@pytest.mark.live
def test_live_get_stock_comments_readonly() -> None:
    if os.getenv("TOSSINVEST_EXTENSIONS_ENABLE_LIVE_TESTS") != "true":
        pytest.skip("Set TOSSINVEST_EXTENSIONS_ENABLE_LIVE_TESTS=true to run live tests.")

    stock_code = os.getenv("TOSSINVEST_EXTENSIONS_LIVE_STOCK_CODE", "000660")
    with TossInvestExtensionsClient() as client:
        page = client.community.get_stock_comments(stock_code)

    assert page.results
    assert page.results[0].comment_id > 0
