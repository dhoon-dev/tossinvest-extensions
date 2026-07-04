from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

CONVENTIONAL_COMMIT = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"(\([a-z0-9._-]+\))?!?: .+"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-event", action="store_true")
    args = parser.parse_args()
    if args.github_event and os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return 0

    base = os.environ.get("GITHUB_BASE_REF")
    if base:
        command = ["git", "log", "--format=%s", f"origin/{base}..HEAD"]
    else:
        command = ["git", "log", "--format=%s", "-1"]

    result = subprocess.run(command, check=True, capture_output=True, text=True)  # noqa: S603
    invalid = [line for line in result.stdout.splitlines() if not CONVENTIONAL_COMMIT.match(line)]
    if invalid:
        print("Invalid commit messages:", file=sys.stderr)
        for line in invalid:
            print(f"  {line}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
