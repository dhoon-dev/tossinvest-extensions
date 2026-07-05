# tossinvest-extensions

Unofficial Python SDK for Toss Securities web API extensions that are not covered by [`tossinvest-openapi`](https://github.com/dhoon-dev/tossinvest-openapi).

This project is not affiliated with, endorsed by, or maintained by Toss Securities. Web APIs are unofficial and may change without notice.

## Installation

```bash
uv add tossinvest-extensions
pip install tossinvest-extensions
```

## Stock Community Comments

```python
from tossinvest_extensions import TossInvestExtensionsClient

with TossInvestExtensionsClient() as client:
    page = client.community.get_stock_comments("000660", sort="RECENT", count=5)
    for comment in page.results:
        print(comment.comment_id, comment.author.nickname, comment.message.message)
```

`stock_code` accepts common stock codes and symbols such as `000660` for Korean
stocks and `AAPL` for US stocks. TossInvest's internal stock code is resolved by
the SDK before comments are requested.

```python
page = client.community.get_stock_comments(
    "AAPL",
    sort="RECENT",
    count=5,
)
```

`sort` accepts `"POPULAR"` or `"RECENT"`. `count` is optional and must be a
positive integer. TossInvest's web API does not expose a page-size query
parameter, so the SDK fetches additional pages internally when needed and
truncates `page.results`.

The method returns `CommunityCommentsPage`.

```python
page.results       # list[CommunityComment]
page.key           # cursor for the next page
page.total_count   # total comments reported by TossInvest
page.has_next      # whether another page is available
```

Each `CommunityComment` exposes parsed fields for author, body, board metadata,
statistics, and timestamps.

```python
comment = page.results[0]
comment.comment_id
comment.author.nickname
comment.message.message
comment.statistic.like_count
comment.statistic.reply_count
comment.created_at
```

## Comment Replies

Use `get_comment_replies` with a parent comment ID to read replies.

```python
replies = client.community.get_comment_replies(
    comment.comment_id,
    sort="POPULAR",
)
for reply in replies.results:
    print(reply.parent_id, reply.comment_id, reply.message.message)
```

`sort` accepts `"POPULAR"`, `"NEWEST"`, or `"OLDEST"`. The method returns the
same `CommunityCommentsPage` shape used for stock comments. Reply objects are
`CommunityComment` instances with `parent_id` set to the parent comment ID.

For the next replies page, pass `page.key` as `cursor`. TossInvest's web app
also sends the like count from the last reply as `lastLikeCount`, which the SDK
exposes as `last_like_count`. This is mainly relevant for `"POPULAR"` sorting:
the server appears to use the last reply's like count as an extra cursor value
because popular replies are not ordered by comment ID alone. It is optional for
the first page and is usually unnecessary for `"NEWEST"` or `"OLDEST"`.

```python
if replies.has_next and replies.results:
    last = replies.results[-1]
    next_replies = client.community.get_comment_replies(
        comment.comment_id,
        sort="POPULAR",
        cursor=replies.key,
        last_like_count=last.statistic.like_count,
    )
```

When `count` cuts through the middle of a server page, `page.key` is adjusted to
the last returned comment ID so it can still be passed as `cursor` for the next
call.

```python
first = client.community.get_stock_comments("000660", sort="RECENT", count=5)
if first.has_next:
    second = client.community.get_stock_comments(
        "000660",
        sort="RECENT",
        cursor=first.key,
        count=5,
    )
```

Use Pydantic serialization when a dictionary is needed.

```python
page.model_dump()
page.model_dump(by_alias=True)
```

## Async Usage

```python
import asyncio

from tossinvest_extensions import AsyncTossInvestExtensionsClient


async def main() -> None:
    async with AsyncTossInvestExtensionsClient() as client:
        page = await client.community.get_stock_comments("AAPL", count=5)
        print(page.total_count)


asyncio.run(main())
```

## Development

```bash
uv sync
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest
uv run --group docs sphinx-build -b html docs docs/_build/html
uv build
```

Install the repository commit hook before committing locally:

```bash
git config core.hooksPath .githooks
```

## Commit and Release Policy

Commit messages follow the same repository policy as `tossinvest-openapi`.

- Allowed types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`.
- Title format: `<type>: <summary>` or `<type>(scope): <summary>`.
- Title length: 50 characters or fewer.
- Body required after one blank line.
- Body lines: 72 characters or fewer.
- English only unless a translation is explicitly requested.

Validate the current commit or a range manually:

```bash
uv run --locked python scripts/check_commit_messages.py --range -1
uv run --locked python scripts/check_commit_messages.py --range origin/main..HEAD
```

Version bumps must update all package version declarations together:

- `pyproject.toml` `[project].version`
- `src/tossinvest_extensions/_version.py` `__version__`
- `docs/conf.py` `release`
- `uv.lock` package `tossinvest-extensions` version

After editing source declarations, update the lockfile and validate the release
tag:

```bash
uv lock
uv run --locked python scripts/validate_release_tag.py vX.Y.Z
```

The GitHub Actions workflow in `.github/workflows/ci.yml` runs formatting,
linting, type checking, mocked unit tests, documentation builds, package builds,
commit-message validation, and release-tag validation on `v*` tag pushes.
Pushing a `v*` tag starts `.github/workflows/release.yml`, which creates a draft
GitHub Release with package and documentation artifacts. Published manual
release runs can deploy documentation to GitHub Pages when `deploy_docs=true`
and Pages is configured to use GitHub Actions.
