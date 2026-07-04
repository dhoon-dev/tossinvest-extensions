"""Serialization helpers for HTTP requests."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel


def join_url(base_url: str, path: str) -> str:
    """Join a base URL and API path without dropping path segments."""
    if path.startswith(("http://", "https://")):
        return path
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def serialize_query(params: Mapping[str, object | None] | None) -> dict[str, str] | None:
    """Return query parameters with ``None`` values removed."""
    if params is None:
        return None
    serialized: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            serialized[key] = str(value).lower()
        else:
            serialized[key] = str(value)
    return serialized


def json_body(value: object | None) -> object | None:
    """Convert Pydantic models to alias-preserving JSON-compatible bodies."""
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, exclude_none=True)
    return value
