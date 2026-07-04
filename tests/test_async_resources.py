from __future__ import annotations

from pytest_httpx import HTTPXMock

from tossinvest_extensions import AsyncTossInvestExtensionsClient

from .conftest import (
    BASE_URL,
    add_result_response,
    comments_page_payload,
    stock_info_payload,
    us_stock_info_payload,
)


async def test_async_get_stock_comments(httpx_mock: HTTPXMock) -> None:
    add_result_response(
        httpx_mock,
        method="GET",
        url=f"{BASE_URL}/api/v2/stock-infos/code-or-symbol/000660",
        result=stock_info_payload(),
    )
    add_result_response(
        httpx_mock,
        method="GET",
        url=f"{BASE_URL}/api/v4/comments",
        match_params={
            "subjectType": "STOCK",
            "subjectId": "KR7000660001",
            "commentSortType": "POPULAR",
        },
        result=comments_page_payload(),
    )

    async with AsyncTossInvestExtensionsClient() as client:
        page = await client.community.get_stock_comments("000660")

    assert page.results[0].author.nickname == "investor"
    assert client.is_closed


async def test_async_get_stock_comments_limits_results(httpx_mock: HTTPXMock) -> None:
    add_result_response(
        httpx_mock,
        method="GET",
        url=f"{BASE_URL}/api/v2/stock-infos/code-or-symbol/AAPL",
        result=us_stock_info_payload(),
    )
    add_result_response(
        httpx_mock,
        method="GET",
        url=f"{BASE_URL}/api/v4/comments",
        match_params={
            "subjectType": "STOCK",
            "subjectId": "US19801212001",
            "commentSortType": "POPULAR",
        },
        result=comments_page_payload(
            [1003, 1002, 1001],
            key=1001,
            subject_id="US19801212001",
            stock_code="US19801212001",
            topic="Apple",
            logo_image_url="https://static.toss.im/png-icons/securities/icn-sec-fill-NAS000C7F-E0.png",
        ),
    )

    async with AsyncTossInvestExtensionsClient() as client:
        page = await client.community.get_stock_comments("aapl", count=2)

    assert [comment.comment_id for comment in page.results] == [1003, 1002]
    assert page.key == 1002
    assert page.has_next
