"""Shared helpers for resource input handling."""

from __future__ import annotations

from tossinvest_extensions.errors import TossInvestExtensionsValidationError


def require_non_empty(name: str, value: str) -> str:
    """Return ``value`` or raise when it is empty."""
    if not value:
        raise TossInvestExtensionsValidationError(f"{name} must not be empty.")
    return value


def require_positive_int(name: str, value: int | None) -> int | None:
    """Return ``value`` or raise when it is not a positive integer."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TossInvestExtensionsValidationError(f"{name} must be a positive integer.")
    return value
