"""Pydantic models for TossInvest web API extension payloads."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type CommentSortType = Literal["POPULAR", "RECENT"]
type SubjectType = Literal["STOCK", "NEWS", "LOUNGE", "CONTENTS", "ETC", "OPTION", "PROFILE"]


class TossInvestExtensionsModel(BaseModel):
    """Base model that preserves additive web API fields and aliases."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Market(TossInvestExtensionsModel):
    """Market descriptor returned by TossInvest stock information."""

    code: str
    display_name: str = Field(alias="displayName")


class StockInfo(TossInvestExtensionsModel):
    """Stock information used to resolve community subject IDs.

    Attributes:
        code: TossInvest internal stock code.
        guid: Identifier used as the stock community ``subjectId``.
        symbol: Market symbol, such as ``"000660"`` or ``"AAPL"``.
        isin_code: ISIN code when returned by TossInvest.
        market: Market descriptor.
        currency: Trading currency.

    """

    code: str
    guid: str
    symbol: str
    isin_code: str = Field(alias="isinCode")
    status: str
    name: str
    english_name: str | None = Field(default=None, alias="englishName")
    detail_name: str | None = Field(default=None, alias="detailName")
    market: Market
    company_code: str | None = Field(default=None, alias="companyCode")
    company_name: str | None = Field(default=None, alias="companyName")
    logo_image_url: str | None = Field(default=None, alias="logoImageUrl")
    currency: str
    nxt_supported: bool | None = Field(default=None, alias="nxtSupported")


class CommunityBadge(TossInvestExtensionsModel):
    """Badge attached to a community author."""

    title: str
    color: str | None = None
    icon_image_url: str | None = Field(default=None, alias="iconImageUrl")


class CommunityAuthor(TossInvestExtensionsModel):
    """Community comment author."""

    user_profile_id: int = Field(alias="userProfileId")
    nickname: str
    profile_picture_url: str | None = Field(default=None, alias="profilePictureUrl")
    type: str
    badge: CommunityBadge | None = None
    short_description: str | None = Field(default=None, alias="shortDescription")
    description: str | None = None


class CommunityMessage(TossInvestExtensionsModel):
    """Community comment title and body."""

    title: str | None = None
    message: str
    represent_emoji: str | None = Field(default=None, alias="representEmoji")


class CommunityBoard(TossInvestExtensionsModel):
    """Community board metadata attached to a comment."""

    topic: str
    subject_id: str = Field(alias="subjectId")
    subject_type: SubjectType = Field(alias="subjectType")
    stock_code: str | None = Field(default=None, alias="stockCode")
    logo_image_url: str | None = Field(default=None, alias="logoImageUrl")


class CommunityImage(TossInvestExtensionsModel):
    """Legacy single image metadata attached to a comment."""

    comment_picture_url: str = Field(alias="commentPictureUrl")
    picture_ratio: float = Field(alias="pictureRatio")


class CommunityMedia(TossInvestExtensionsModel):
    """Media metadata attached to a comment."""

    type: str
    url: str
    picture_ratio: float | None = Field(default=None, alias="pictureRatio")
    ocr_text: str | None = Field(default=None, alias="ocrText")


class CommunityStatistic(TossInvestExtensionsModel):
    """Community interaction counts and current-viewer flags."""

    like_count: int = Field(alias="likeCount")
    reply_count: int = Field(alias="replyCount")
    repost_count: int = Field(alias="repostCount")
    read_count: int = Field(alias="readCount")
    follower_count: int = Field(alias="followerCount")
    is_like: bool = Field(alias="isLike")
    is_bookmarked: bool = Field(alias="isBookmarked")
    is_following: bool = Field(alias="isFollowing")
    is_my_profile: bool = Field(alias="isMyProfile")


class CommunityHolding(TossInvestExtensionsModel):
    """Author holding status attached to a comment when available."""

    share_holding_status: str | None = Field(default=None, alias="shareHoldingStatus")


class CommunityTopic(TossInvestExtensionsModel):
    """Topic metadata attached to a community comment."""

    type: str
    id: str
    name: str


class CommunityComment(TossInvestExtensionsModel):
    """Single TossInvest community comment.

    Attributes:
        comment_id: TossInvest comment identifier.
        author: Comment author information.
        message: Comment title, body, and representative emoji.
        board: Stock community board metadata.
        statistic: Like, reply, repost, read, and viewer-state values.
        created_at: Comment creation timestamp string returned by TossInvest.
        updated_at: Comment update timestamp string returned by TossInvest.

    """

    type: str
    comment_id: int = Field(alias="commentId")
    author: CommunityAuthor
    parent_id: int | None = Field(default=None, alias="parentId")
    message: CommunityMessage
    board: CommunityBoard
    image: CommunityImage | None = None
    media: list[CommunityMedia] | None = None
    statistic: CommunityStatistic
    vote: object | None = None
    execution: object | None = None
    disclosure: object | None = None
    holding: CommunityHolding | None = None
    edited: bool
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    is_repost: bool = Field(alias="isRepost")
    repost_comment: object | None = Field(default=None, alias="repostComment")
    best_reply_comment: object | None = Field(default=None, alias="bestReplyComment")
    access_level: str | None = Field(default=None, alias="accessLevel")
    issue_topic: object | None = Field(default=None, alias="issueTopic")
    topics: list[CommunityTopic] | None = None
    author_user_profile_id: int | None = Field(default=None, alias="authorUserProfileId")

    @property
    def id(self) -> int:
        """Return ``comment_id`` for callers mirroring the web app naming."""
        return self.comment_id


class CommunityCommentsPage(TossInvestExtensionsModel):
    """Paginated community comments response.

    Attributes:
        results: Comments returned for this page. When ``count`` is passed to
            ``get_stock_comments``, this list is truncated to that count.
        key: Cursor for the next page. Pass this value as ``cursor`` to
            continue pagination.
        total_count: Total number of comments reported by TossInvest.
        has_next: Whether another page is available.

    """

    results: list[CommunityComment]
    key: int | str | None = None
    total_count: int | None = Field(default=None, alias="totalCount")
    has_next: bool = Field(alias="hasNext")


def normalize_stock_code(stock_code: str) -> str:
    """Normalize a user-facing stock code or symbol for TossInvest lookup."""
    return stock_code.strip().upper()


def parse_model[ModelT: TossInvestExtensionsModel](model: type[ModelT], data: object) -> ModelT:
    """Validate one API result object as the requested SDK model."""
    return model.model_validate(data)
