from __future__ import annotations

from tossinvest_extensions import TossInvestExtensionsClient


def main() -> None:
    with TossInvestExtensionsClient() as client:
        page = client.community.get_stock_comments("000660")
        for comment in page.results:
            print(comment.comment_id, comment.author.nickname, comment.message.message)


if __name__ == "__main__":
    main()
