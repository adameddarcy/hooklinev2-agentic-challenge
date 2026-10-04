import pytest

from hookline.services.matching import event_type_matches, matches_any


@pytest.mark.parametrize(
    ("pattern", "event_type"),
    [
        ("order.created", "order.created"),
        ("order.*", "order.created"),
        ("order.*", "order.item.added"),
        ("order.item.*", "order.item.added"),
        ("*", "order.created"),
        ("*", "ping"),
        ("ping", "ping"),
    ],
)
def test_pattern_matches(pattern: str, event_type: str) -> None:
    assert event_type_matches(pattern, event_type)


@pytest.mark.parametrize(
    ("pattern", "event_type"),
    [
        ("order.created", "order.updated"),
        ("order.created", "order.created_v2"),
        ("order", "order.created"),
        ("order", "orders.created"),
        ("order.*", "order"),
        ("order.*", "orders.created"),
        ("order.item.*", "order.created"),
        ("invoice.*", "order.created"),
    ],
)
def test_pattern_does_not_match(pattern: str, event_type: str) -> None:
    assert not event_type_matches(pattern, event_type)


def test_matches_any() -> None:
    assert matches_any(["invoice.*", "order.created"], "order.created")
    assert not matches_any(["invoice.*", "order.updated"], "order.created")
    assert not matches_any([], "order.created")
