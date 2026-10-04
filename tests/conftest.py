"""Shared fixtures: an isolated app per test with an in-memory database."""

from collections.abc import Callable, Iterator
from typing import Any

import pytest
import respx
from fastapi.testclient import TestClient

from hookline.config import Settings
from hookline.main import create_app

SubscriptionFactory = Callable[..., dict[str, Any]]


@pytest.fixture
def settings() -> Settings:
    return Settings(database_url="sqlite://", delivery_timeout_seconds=1.0)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def receiver() -> Iterator[respx.MockRouter]:
    """Intercept outbound webhook requests. Unmocked hosts raise an error."""
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
def make_subscription(client: TestClient) -> SubscriptionFactory:
    """Create a subscription through the API and return the response body."""

    def _make(**overrides: Any) -> dict[str, Any]:
        body: dict[str, Any] = {
            "target_url": "https://example.com/hooks",
            "event_types": ["order.created"],
        }
        body.update(overrides)
        response = client.post("/subscriptions", json=body)
        assert response.status_code == 201, response.text
        return dict(response.json())

    return _make
