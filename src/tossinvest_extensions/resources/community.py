"""Community resource methods."""

from __future__ import annotations

from urllib.parse import quote

from tossinvest_extensions._http import AsyncHTTPClient, SyncHTTPClient
from tossinvest_extensions.models import (
    CommentSortType,
    CommunityComment,
    CommunityCommentsPage,
    StockInfo,
    SubjectType,
    normalize_stock_code,
    parse_model,
)

from ._utils import require_non_empty, require_positive_int


def _limited_comments_page(
    base_page: CommunityCommentsPage,
    collected: list[CommunityComment],
    count: int,
    *,
    has_next_page: bool,
) -> CommunityCommentsPage:
    """Return ``base_page`` with collected comments limited to ``count``."""
    limited = collected[:count]
    if not limited:
        return base_page.model_copy(update={"results": [], "key": None, "has_next": False})

    has_more = len(collected) > count or has_next_page
    return base_page.model_copy(
        update={
            "results": limited,
            "key": limited[-1].comment_id if has_more else None,
            "has_next": has_more,
        },
    )


def _stock_info_lookup_path(stock_code: str) -> str:
    """Return the stock-info lookup path for a common stock code or symbol."""
    code = require_non_empty("stock_code", normalize_stock_code(stock_code))
    return f"/api/v2/stock-infos/code-or-symbol/{quote(code, safe='')}"


class CommunityResource:
    """Synchronous TossInvest community web API endpoints."""

    def __init__(self, http: SyncHTTPClient) -> None:
        self._http = http

    def get_stock_info(self, stock_code: str) -> StockInfo:
        """Return web stock information for a common stock code or symbol.

        The returned ``guid`` is the community ``subjectId`` used by comment
        endpoints.

        Args:
            stock_code: Common stock code or symbol such as ``"000660"`` for
                Korean stocks or ``"AAPL"`` for US stocks.

        Returns:
            Resolved TossInvest stock information. ``guid`` is the community
            ``subjectId`` used by comment endpoints.

        Raises:
            TossInvestExtensionsValidationError: ``stock_code`` is empty.
            TossInvestExtensionsAPIError: The web API returns an error response.

        """
        result = self._http.request("GET", _stock_info_lookup_path(stock_code))
        return parse_model(StockInfo, result)

    def get_comments(
        self,
        subject_type: SubjectType,
        subject_id: str,
        *,
        sort: CommentSortType = "POPULAR",
        cursor: int | str | None = None,
    ) -> CommunityCommentsPage:
        """Return a page of community comments for a subject.

        Args:
            subject_type: TossInvest community subject type.
            subject_id: Community subject identifier.
            sort: Comment sort order. ``"POPULAR"`` mirrors the stock page
                default; ``"RECENT"`` returns recent comments.
            cursor: Optional ``key`` from the previous page.

        Returns:
            A ``CommunityCommentsPage`` containing one server page of comments.

        Raises:
            TossInvestExtensionsValidationError: ``subject_id`` is empty.
            TossInvestExtensionsAPIError: The web API returns an error response.

        """
        result = self._http.request(
            "GET",
            "/api/v4/comments",
            params={
                "subjectType": subject_type,
                "subjectId": require_non_empty("subject_id", subject_id),
                "commentSortType": sort,
                "lastCommentId": cursor,
            },
        )
        return parse_model(CommunityCommentsPage, result)

    def get_stock_comments(
        self,
        stock_code: str,
        *,
        sort: CommentSortType = "POPULAR",
        cursor: int | str | None = None,
        count: int | None = None,
    ) -> CommunityCommentsPage:
        """Return community comments for a TossInvest stock page.

        This resolves ``stock_code`` through
        ``/api/v2/stock-infos/code-or-symbol/{stock_code}`` and then calls
        ``/api/v4/comments`` with ``subjectType=STOCK`` and the resolved
        ``guid`` as ``subjectId``.

        Args:
            stock_code: Common stock code or symbol such as ``"000660"`` for
                Korean stocks or ``"AAPL"`` for US stocks.
            sort: Comment sort order.
            cursor: Optional ``key`` from the previous page.
            count: Optional positive number of comments to return. The web API
                does not expose a page-size parameter, so the SDK fetches pages
                internally and truncates ``results`` to this count.

        Returns:
            A ``CommunityCommentsPage``. When ``count`` is set, ``results`` is
            limited to at most that many comments and ``key`` is adjusted to the
            last returned comment ID when another page is available.

        Raises:
            TossInvestExtensionsValidationError: ``stock_code`` is empty.
            TossInvestExtensionsValidationError: ``count`` is not positive.
            TossInvestExtensionsAPIError: The web API returns an error response.

        """
        validated_count = require_positive_int("count", count)
        stock = self.get_stock_info(stock_code)
        page = self.get_comments("STOCK", stock.guid, sort=sort, cursor=cursor)
        if validated_count is None:
            return page

        collected = list(page.results)
        current_page = page
        while (
            len(collected) < validated_count
            and current_page.has_next
            and current_page.key is not None
            and current_page.results
        ):
            current_page = self.get_comments(
                "STOCK",
                stock.guid,
                sort=sort,
                cursor=current_page.key,
            )
            collected.extend(current_page.results)

        return _limited_comments_page(
            page,
            collected,
            validated_count,
            has_next_page=current_page.has_next,
        )


class AsyncCommunityResource:
    """Asynchronous TossInvest community web API endpoints."""

    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    async def get_stock_info(self, stock_code: str) -> StockInfo:
        """Return web stock information for a common stock code or symbol.

        Args:
            stock_code: Common stock code or symbol such as ``"000660"`` for
                Korean stocks or ``"AAPL"`` for US stocks.

        Returns:
            Resolved TossInvest stock information. ``guid`` is the community
            ``subjectId`` used by comment endpoints.

        Raises:
            TossInvestExtensionsValidationError: ``stock_code`` is empty.
            TossInvestExtensionsAPIError: The web API returns an error response.

        """
        result = await self._http.request("GET", _stock_info_lookup_path(stock_code))
        return parse_model(StockInfo, result)

    async def get_comments(
        self,
        subject_type: SubjectType,
        subject_id: str,
        *,
        sort: CommentSortType = "POPULAR",
        cursor: int | str | None = None,
    ) -> CommunityCommentsPage:
        """Return a page of community comments for a subject.

        Args:
            subject_type: TossInvest community subject type.
            subject_id: Community subject identifier.
            sort: Comment sort order. ``"POPULAR"`` mirrors the stock page
                default; ``"RECENT"`` returns recent comments.
            cursor: Optional ``key`` from the previous page.

        Returns:
            A ``CommunityCommentsPage`` containing one server page of comments.

        Raises:
            TossInvestExtensionsValidationError: ``subject_id`` is empty.
            TossInvestExtensionsAPIError: The web API returns an error response.

        """
        result = await self._http.request(
            "GET",
            "/api/v4/comments",
            params={
                "subjectType": subject_type,
                "subjectId": require_non_empty("subject_id", subject_id),
                "commentSortType": sort,
                "lastCommentId": cursor,
            },
        )
        return parse_model(CommunityCommentsPage, result)

    async def get_stock_comments(
        self,
        stock_code: str,
        *,
        sort: CommentSortType = "POPULAR",
        cursor: int | str | None = None,
        count: int | None = None,
    ) -> CommunityCommentsPage:
        """Return community comments for a TossInvest stock page.

        This resolves ``stock_code`` through
        ``/api/v2/stock-infos/code-or-symbol/{stock_code}`` and then calls
        ``/api/v4/comments`` with ``subjectType=STOCK`` and the resolved
        ``guid`` as ``subjectId``.

        Args:
            stock_code: Common stock code or symbol such as ``"000660"`` for
                Korean stocks or ``"AAPL"`` for US stocks.
            sort: Comment sort order.
            cursor: Optional ``key`` from the previous page.
            count: Optional positive number of comments to return. The web API
                does not expose a page-size parameter, so the SDK fetches pages
                internally and truncates ``results`` to this count.

        Returns:
            A ``CommunityCommentsPage``. When ``count`` is set, ``results`` is
            limited to at most that many comments and ``key`` is adjusted to the
            last returned comment ID when another page is available.

        Raises:
            TossInvestExtensionsValidationError: ``stock_code`` is empty.
            TossInvestExtensionsValidationError: ``count`` is not positive.
            TossInvestExtensionsAPIError: The web API returns an error response.

        """
        validated_count = require_positive_int("count", count)
        stock = await self.get_stock_info(stock_code)
        page = await self.get_comments("STOCK", stock.guid, sort=sort, cursor=cursor)
        if validated_count is None:
            return page

        collected = list(page.results)
        current_page = page
        while (
            len(collected) < validated_count
            and current_page.has_next
            and current_page.key is not None
            and current_page.results
        ):
            current_page = await self.get_comments(
                "STOCK",
                stock.guid,
                sort=sort,
                cursor=current_page.key,
            )
            collected.extend(current_page.results)

        return _limited_comments_page(
            page,
            collected,
            validated_count,
            has_next_page=current_page.has_next,
        )
