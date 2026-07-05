from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import httpx
from pytest_httpx import HTTPXMock

from tossinvest_extensions import TossInvestExtensionsClient

BASE_URL = "https://wts-info-api.tossinvest.com"
CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"


def add_result_response(
    httpx_mock: HTTPXMock,
    *,
    method: str,
    url: str,
    result: Any,
    match_params: dict[str, str] | None = None,
) -> None:
    httpx_mock.add_response(
        method=method,
        url=url,
        match_params=match_params,
        json={"result": result},
    )


def make_client(
    *,
    base_url: str = BASE_URL,
    timeout: float | httpx.Timeout = 10.0,
    max_retries: int = 2,
    user_agent: str = "tossinvest-extensions/0.1.0",
    http_client: httpx.Client | None = None,
) -> TossInvestExtensionsClient:
    return TossInvestExtensionsClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        user_agent=user_agent,
        http_client=http_client,
    )


def stock_info_payload(stock_code: str = "A000660") -> dict[str, object]:
    return {
        "code": stock_code,
        "guid": "KR7000660001",
        "symbol": "000660",
        "isinCode": "KR7000660001",
        "status": "N",
        "name": "SK hynix",
        "englishName": "SK hynix",
        "detailName": "SK hynix",
        "market": {"code": "KSP", "displayName": "KOSPI"},
        "companyCode": "000660",
        "companyName": "SK hynix",
        "logoImageUrl": "https://static.toss.im/png-icons/securities/icn-sec-fill-000660.png",
        "currency": "KRW",
        "nxtSupported": True,
    }


def us_stock_info_payload(stock_code: str = "US19801212001") -> dict[str, object]:
    return {
        "code": stock_code,
        "guid": stock_code,
        "symbol": "AAPL",
        "isinCode": "US0378331005",
        "status": "N",
        "name": "Apple",
        "englishName": "Apple",
        "detailName": "Apple",
        "market": {"code": "NSQ", "displayName": "NASDAQ"},
        "companyCode": None,
        "companyName": "Apple",
        "logoImageUrl": "https://static.toss.im/png-icons/securities/icn-sec-fill-NAS000C7F-E0.png",
        "currency": "USD",
        "nxtSupported": None,
    }


def comment_payload(
    comment_id: int = 285316674,
    *,
    subject_id: str = "KR7000660001",
    stock_code: str = "A000660",
    topic: str = "SK hynix",
    logo_image_url: str = "https://static.toss.im/png-icons/securities/icn-sec-fill-000660.png",
) -> dict[str, object]:
    return {
        "type": "USER_COMMENT",
        "commentId": comment_id,
        "author": {
            "userProfileId": 7031068,
            "nickname": "investor",
            "profilePictureUrl": "https://static.toss.im/illusts/img-profile-emoji-13.png",
            "type": "USER",
            "badge": {"title": "badge", "color": "green", "iconImageUrl": None},
            "shortDescription": "",
            "description": "",
        },
        "parentId": None,
        "message": {
            "title": "Title",
            "message": "Community comment body",
            "representEmoji": "",
        },
        "board": {
            "topic": topic,
            "subjectId": subject_id,
            "subjectType": "STOCK",
            "stockCode": stock_code,
            "logoImageUrl": logo_image_url,
        },
        "image": None,
        "media": [
            {
                "type": "image",
                "url": "https://forum.tossinvest.com/forum/comment/image.png",
                "pictureRatio": 0.75,
                "ocrText": None,
            }
        ],
        "statistic": {
            "likeCount": 41,
            "replyCount": 10,
            "repostCount": 0,
            "readCount": 556,
            "followerCount": 48,
            "isLike": False,
            "isBookmarked": False,
            "isFollowing": False,
            "isMyProfile": False,
        },
        "vote": None,
        "execution": None,
        "disclosure": None,
        "holding": {"shareHoldingStatus": "HOLDING"},
        "edited": False,
        "createdAt": "2026-07-04T18:22:32.188924758+09:00",
        "updatedAt": "2026-07-04T18:22:32.188924758+09:00",
        "isRepost": False,
        "repostComment": None,
        "bestReplyComment": None,
        "accessLevel": "EXTERNAL_PUBLIC",
        "issueTopic": None,
        "topics": [{"type": "BOARD", "id": subject_id, "name": topic}],
        "authorUserProfileId": 7031068,
    }


def reply_payload(
    comment_id: int = 285316675,
    *,
    parent_id: int = 285316674,
    subject_id: str = "KR7000660001",
    stock_code: str = "A000660",
    topic: str = "SK hynix",
    logo_image_url: str = "https://static.toss.im/png-icons/securities/icn-sec-fill-000660.png",
    like_count: int = 12,
) -> dict[str, object]:
    payload = comment_payload(
        comment_id,
        subject_id=subject_id,
        stock_code=stock_code,
        topic=topic,
        logo_image_url=logo_image_url,
    )
    payload["parentId"] = parent_id
    payload["message"] = {
        "title": None,
        "message": "Community reply body",
        "representEmoji": "",
    }
    statistic = cast("dict[str, Any]", payload["statistic"]).copy()
    statistic["likeCount"] = like_count
    statistic["replyCount"] = 0
    payload["statistic"] = statistic
    payload["bestReplyComment"] = None
    return payload


def comments_page_payload(
    comment_ids: Sequence[int] | None = None,
    *,
    key: int | str | None = 285317124,
    total_count: int = 1129385,
    has_next: bool = True,
    subject_id: str = "KR7000660001",
    stock_code: str = "A000660",
    topic: str = "SK hynix",
    logo_image_url: str = "https://static.toss.im/png-icons/securities/icn-sec-fill-000660.png",
) -> dict[str, object]:
    ids = comment_ids or [285316674]
    return {
        "results": [
            comment_payload(
                comment_id,
                subject_id=subject_id,
                stock_code=stock_code,
                topic=topic,
                logo_image_url=logo_image_url,
            )
            for comment_id in ids
        ],
        "key": key,
        "totalCount": total_count,
        "hasNext": has_next,
    }


def replies_page_payload(
    comment_ids: Sequence[int] | None = None,
    *,
    parent_id: int = 285316674,
    key: int | str | None = 285316675,
    total_count: int = 3,
    has_next: bool = True,
    like_count: int = 12,
) -> dict[str, object]:
    ids = comment_ids or [285316675]
    return {
        "results": [
            reply_payload(
                comment_id,
                parent_id=parent_id,
                like_count=like_count,
            )
            for comment_id in ids
        ],
        "key": key,
        "totalCount": total_count,
        "hasNext": has_next,
    }
