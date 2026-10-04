import pytest
from pydantic import ValidationError

from hookline.schemas import EventIn, SubscriptionCreate


def test_subscription_create_accepts_valid_input() -> None:
    data = SubscriptionCreate.model_validate(
        {
            "target_url": "https://example.com/hooks",
            "event_types": ["order.*", "invoice.paid", "*"],
            "description": "  Orders  ",
        }
    )
    assert data.active is True
    assert data.description == "Orders"


@pytest.mark.parametrize(
    "event_types",
    [[], ["Order.Created"], ["order."], ["order.*.created"], ["*.created"], ["order created"]],
)
def test_subscription_create_rejects_bad_event_types(event_types: list[str]) -> None:
    with pytest.raises(ValidationError):
        SubscriptionCreate.model_validate(
            {"target_url": "https://example.com/hooks", "event_types": event_types}
        )


@pytest.mark.parametrize("url", ["not-a-url", "ftp://example.com/hooks", ""])
def test_subscription_create_rejects_bad_urls(url: str) -> None:
    with pytest.raises(ValidationError):
        SubscriptionCreate.model_validate({"target_url": url, "event_types": ["ping"]})


def test_subscription_create_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        SubscriptionCreate.model_validate(
            {"target_url": "https://example.com", "event_types": ["ping"], "secret": "mine"}
        )


def test_subscription_create_rejects_long_description() -> None:
    with pytest.raises(ValidationError):
        SubscriptionCreate.model_validate(
            {"target_url": "https://example.com", "event_types": ["ping"], "description": "x" * 201}
        )


def test_event_in_rejects_wildcards() -> None:
    with pytest.raises(ValidationError):
        EventIn.model_validate({"type": "order.*"})


def test_event_in_defaults_payload() -> None:
    assert EventIn.model_validate({"type": "ping"}).payload == {}
