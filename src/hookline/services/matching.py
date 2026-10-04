"""Matching of concrete event types against subscription patterns.

Event types are dot-separated segments, e.g. ``order.created``. A pattern is either:

* an exact event type: ``order.created`` matches only ``order.created``;
* a prefix wildcard: ``order.*`` matches ``order.created`` and ``order.item.added``,
  but not ``order`` itself and not ``orders.created``;
* a bare ``*``, which matches everything.
"""

from collections.abc import Iterable

WILDCARD = "*"


def event_type_matches(pattern: str, event_type: str) -> bool:
    """Return ``True`` if ``event_type`` is selected by ``pattern``."""
    if pattern == WILDCARD:
        return True
    return event_type.startswith(pattern.removesuffix(WILDCARD))


def matches_any(patterns: Iterable[str], event_type: str) -> bool:
    """Return ``True`` if any of ``patterns`` selects ``event_type``."""
    return any(event_type_matches(pattern, event_type) for pattern in patterns)
