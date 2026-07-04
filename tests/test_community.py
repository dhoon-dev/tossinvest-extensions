from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from tossinvest_extensions.errors import TossInvestExtensionsValidationError

from .conftest import (
    BASE_URL,
    add_result_response,
    comments_page_payload,
    make_client,
    stock_info_payload,
    us_stock_info_payload,
)


def test_get_stock_comments_resolves_guid_and_parses_response(httpx_mock: HTTPXMock) -> None:
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
    client = make_client()

    page = client.community.get_stock_comments("000660")

    assert page.results[0].comment_id == 285316674
    assert page.results[0].id == 285316674
    assert page.results[0].author.nickname == "investor"
    assert page.results[0].message.message == "Community comment body"
    assert page.results[0].statistic.like_count == 41
    assert page.key == 285317124
    assert page.total_count == 1129385
    assert page.has_next


def test_get_stock_comments_resolves_krx_symbol_without_tossinvest_prefix(
    httpx_mock: HTTPXMock,
) -> None:
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
            "commentSortType": "RECENT",
            "lastCommentId": "285317124",
        },
        result=comments_page_payload(),
    )
    client = make_client()

    page = client.community.get_stock_comments("000660", sort="RECENT", cursor=285317124)

    assert page.results[0].board.stock_code == "A000660"


def test_get_stock_comments_resolves_us_symbol(httpx_mock: HTTPXMock) -> None:
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
            "commentSortType": "RECENT",
        },
        result=comments_page_payload(
            subject_id="US19801212001",
            stock_code="US19801212001",
            topic="Apple",
            logo_image_url="https://static.toss.im/png-icons/securities/icn-sec-fill-NAS000C7F-E0.png",
        ),
    )
    client = make_client()

    page = client.community.get_stock_comments("aapl", sort="RECENT")

    assert page.results[0].board.subject_id == "US19801212001"
    assert page.results[0].board.stock_code == "US19801212001"


def test_get_stock_comments_limits_results_within_server_page(httpx_mock: HTTPXMock) -> None:
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
            "commentSortType": "RECENT",
        },
        result=comments_page_payload([1003, 1002, 1001], key=1001),
    )
    client = make_client()

    page = client.community.get_stock_comments("000660", sort="RECENT", count=2)

    assert [comment.comment_id for comment in page.results] == [1003, 1002]
    assert page.key == 1002
    assert page.has_next


def test_get_stock_comments_fetches_until_count_is_reached(httpx_mock: HTTPXMock) -> None:
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
        result=comments_page_payload([1004, 1003], key=1003),
    )
    add_result_response(
        httpx_mock,
        method="GET",
        url=f"{BASE_URL}/api/v4/comments",
        match_params={
            "subjectType": "STOCK",
            "subjectId": "KR7000660001",
            "commentSortType": "POPULAR",
            "lastCommentId": "1003",
        },
        result=comments_page_payload([1002, 1001], key=1001),
    )
    client = make_client()

    page = client.community.get_stock_comments("000660", count=3)

    assert [comment.comment_id for comment in page.results] == [1004, 1003, 1002]
    assert page.key == 1002
    assert page.has_next


def test_get_stock_comments_count_exhausts_available_results(httpx_mock: HTTPXMock) -> None:
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
        result=comments_page_payload([1004, 1003], key=1003),
    )
    add_result_response(
        httpx_mock,
        method="GET",
        url=f"{BASE_URL}/api/v4/comments",
        match_params={
            "subjectType": "STOCK",
            "subjectId": "KR7000660001",
            "commentSortType": "POPULAR",
            "lastCommentId": "1003",
        },
        result=comments_page_payload([1002], key=None, has_next=False),
    )
    client = make_client()

    page = client.community.get_stock_comments("000660", count=5)

    assert [comment.comment_id for comment in page.results] == [1004, 1003, 1002]
    assert page.key is None
    assert not page.has_next


def test_get_comments_uses_subject_id_directly(httpx_mock: HTTPXMock) -> None:
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
    client = make_client()

    page = client.community.get_comments("STOCK", "KR7000660001")

    assert page.results[0].board.subject_id == "KR7000660001"


def test_get_stock_info_rejects_empty_stock_code() -> None:
    client = make_client()

    with pytest.raises(TossInvestExtensionsValidationError, match="stock_code must not be empty"):
        client.community.get_stock_info("")


def test_get_stock_comments_rejects_invalid_count() -> None:
    client = make_client()

    with pytest.raises(
        TossInvestExtensionsValidationError, match="count must be a positive integer"
    ):
        client.community.get_stock_comments("000660", count=0)
