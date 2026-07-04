# AGENTS.md

## Project Scope

This repository is an unofficial Python SDK for Toss Securities web API extensions that are not covered by `tossinvest-openapi`.
Keep the public API explicit, typed, and conservative. Prefer small resource methods that mirror observed web API behavior.

Generated source, documentation, comments, test names, and commit-facing text in this repository must be written in English unless a user explicitly asks for a translation.

## Sources of Truth

- Use the live TossInvest web app only to discover unsupported extension endpoints.
- Treat WTS web APIs as unstable, unofficial APIs. Keep models additive and avoid rejecting unknown response fields.
- Do not require TossInvest OpenAPI credentials for public web API reads.
- If a future feature can use official OpenAPI behavior safely, prefer `tossinvest-openapi` as an optional integration rather than duplicating official API logic.

## Dependency and Tooling Rules

- This project targets Python 3.12+.
- Use `uv` for project commands. Prefer locked commands in CI-like validation:
  `uv sync --locked --all-extras --group docs`.
- Before changing behavior that depends on third-party packages, GitHub Actions, Sphinx, pytest, Ruff, ty, uv, httpx, Pydantic, or other external tools, consult current documentation first.

## Quality Gate

Run the focused command for the change first. Before handing off broad changes, run the full local gate:

```bash
uv sync --locked --all-extras --group docs
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked ty check
uv run --locked pytest -m "not live"
uv run --locked --group docs sphinx-build -W -b html docs docs/_build/html
uv build
```

## Credentials and Live Tests

- The SDK must not read environment variables or `.env` files.
- Unit tests use mocked HTTP and must not require network access.
- Live tests are read-only and require `TOSSINVEST_EXTENSIONS_ENABLE_LIVE_TESTS=true`.

## Documentation

- Sphinx/autodoc is the documentation generator.
- Keep public classes, functions, resources, exceptions, and Pydantic models documented with useful docstrings.

## Implementation Guidelines

- Keep sync and async clients behaviorally aligned.
- Keep exception messages sanitized and avoid logging request cookies or headers.
- Prefer Pydantic v2 aliases over manual key conversion.
- Preserve additive web API fields with `extra="allow"` models.
