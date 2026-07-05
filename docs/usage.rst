Usage
=====

Stock community comments
------------------------

Use ``get_stock_comments`` to read comments from a TossInvest stock community.

.. code-block:: python

   from tossinvest_extensions import TossInvestExtensionsClient

   with TossInvestExtensionsClient() as client:
       page = client.community.get_stock_comments("000660", sort="RECENT", count=5)
       for comment in page.results:
           print(comment.comment_id, comment.message.message)

Use common stock codes and symbols such as ``000660`` for Korean stocks and
``AAPL`` for US stocks. TossInvest's internal stock code is resolved by the
SDK.

Signature
^^^^^^^^^

.. code-block:: python

   get_stock_comments(
       stock_code: str,
       *,
       sort: CommentSortType = "POPULAR",
       cursor: int | str | None = None,
       count: int | None = None,
   ) -> CommunityCommentsPage

Parameters
^^^^^^^^^^

``stock_code``
   Common stock code or symbol. Use values such as ``000660`` for Korean
   stocks, ``AAPL`` for US stocks, or ``TSLA`` for Tesla. The SDK resolves this
   to TossInvest's internal ``guid`` before requesting comments.

``sort``
   Comment order. Accepted values are ``"POPULAR"`` and ``"RECENT"``.
   ``"POPULAR"`` is the default.

``cursor``
   Optional ``key`` from a previous ``CommunityCommentsPage``. Pass this value
   to fetch the next page.

``count``
   Optional positive integer that limits the number of returned comments.
   TossInvest's web API does not expose a page-size query parameter, so the SDK
   fetches additional pages internally when needed and truncates
   ``page.results``.

Return value
^^^^^^^^^^^^

``get_stock_comments`` returns ``CommunityCommentsPage``.

.. code-block:: python

   page.results       # list[CommunityComment]
   page.key           # cursor for the next page
   page.total_count   # total comments reported by TossInvest
   page.has_next      # whether another page is available

Each ``CommunityComment`` exposes parsed fields for author, message, board
metadata, statistics, and timestamps.

.. code-block:: python

   comment = page.results[0]

   comment.comment_id
   comment.id
   comment.author.nickname
   comment.message.message
   comment.board.subject_id
   comment.board.stock_code
   comment.statistic.like_count
   comment.statistic.reply_count
   comment.created_at
   comment.updated_at

Use Pydantic serialization when a dictionary is needed.

.. code-block:: python

   page.model_dump()
   page.model_dump(by_alias=True)

Pagination
^^^^^^^^^^

The comment page response exposes ``has_next`` and ``key``. Pass ``key`` back
as ``cursor`` to fetch the next page.

.. code-block:: python

   first = client.community.get_stock_comments("000660")
   if first.has_next:
       second = client.community.get_stock_comments("000660", cursor=first.key)

When ``count`` cuts through the middle of a server page, ``page.key`` is
adjusted to the last returned comment ID. This keeps pagination usable even
when the SDK has truncated ``page.results``.

.. code-block:: python

   first = client.community.get_stock_comments("000660", sort="RECENT", count=5)
   if first.has_next:
       second = client.community.get_stock_comments(
           "000660",
           sort="RECENT",
           cursor=first.key,
           count=5,
       )

Comment replies
^^^^^^^^^^^^^^^

Use ``get_comment_replies`` with a parent comment ID to read replies to a
community comment.

.. code-block:: python

   replies = client.community.get_comment_replies(
       comment.comment_id,
       sort="POPULAR",
   )

   for reply in replies.results:
       print(reply.parent_id, reply.comment_id, reply.message.message)

Signature:

.. code-block:: python

   get_comment_replies(
       comment_id: int | str,
       *,
       sort: ReplySortType = "POPULAR",
       cursor: int | str | None = None,
       last_like_count: int | None = None,
   ) -> CommunityCommentsPage

``sort`` accepts ``"POPULAR"``, ``"NEWEST"``, and ``"OLDEST"``. The return
value is the same ``CommunityCommentsPage`` shape used by
``get_stock_comments``. Each reply is parsed as ``CommunityComment`` with
``parent_id`` set to the parent comment ID.

For the next replies page, pass ``page.key`` as ``cursor``. TossInvest's web
app also sends the like count from the last reply as ``lastLikeCount`` while
paginating replies; pass that value as ``last_like_count``. This is mainly
relevant for ``"POPULAR"`` sorting: the server appears to use the last reply's
like count as an extra cursor value because popular replies are not ordered by
comment ID alone. It is optional for the first page and is usually unnecessary
for ``"NEWEST"`` or ``"OLDEST"``.

.. code-block:: python

   if replies.has_next and replies.results:
       last = replies.results[-1]
       next_replies = client.community.get_comment_replies(
           comment.comment_id,
           sort="POPULAR",
           cursor=replies.key,
           last_like_count=last.statistic.like_count,
       )

Async usage
^^^^^^^^^^^

The async client exposes the same resource API.

.. code-block:: python

   import asyncio

   from tossinvest_extensions import AsyncTossInvestExtensionsClient


   async def main() -> None:
       async with AsyncTossInvestExtensionsClient() as client:
           page = await client.community.get_stock_comments("AAPL", sort="RECENT", count=5)
           print(page.total_count)


   asyncio.run(main())

Errors
^^^^^^

Invalid local inputs raise ``TossInvestExtensionsValidationError`` before an API
request is sent. Examples include an empty ``stock_code`` or a non-positive
``count``.

TossInvest web API error responses raise ``TossInvestExtensionsAPIError``.
Rate-limit responses raise ``TossInvestExtensionsRateLimitError``.

The API is unofficial and may change without notice. Models preserve additive
fields returned by TossInvest so callers can still access newly-added response
data through Pydantic's extra field support.
