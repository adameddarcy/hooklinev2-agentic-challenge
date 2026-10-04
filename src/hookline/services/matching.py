"""Matching of concrete event types against subscription patterns.

Event types are dot-separated segments, e.g. ``order.created``. A pattern is either:

* an exact event type: ``order.created`` matches only ``order.created``;
* a prefix wildcard: ``order.*`` matches ``order.created`` and ``order.item.added``,
  but not ``order`` itself and not ``orders.created``;
* a bare ``*``, which matches everything.
"""

from collections.abc import Iterable

WILDCARD = "*"
SEPARATOR = "."


def event_type_matches(pattern: str, event_type: str) -> bool:
    """Return ``True`` if ``event_type`` is selected by ``pattern``."""
    if pattern == WILDCARD:
        return True

    pattern_parts = pattern.split(SEPARATOR)
    event_parts = event_type.split(SEPARATOR)

    if pattern_parts[-1] == WILDCARD:
        prefix = pattern_parts[:-1]
        return len(event_parts) > len(prefix) and event_parts[: len(prefix)] == prefix

    return pattern_parts == event_parts


def matches_any(patterns: Iterable[str], event_type: str) -> bool:
    """Return ``True`` if any of ``patterns`` selects ``event_type``."""
    return any(event_type_matches(pattern, event_type) for pattern in patterns)
