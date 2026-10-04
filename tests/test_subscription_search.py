from fastapi.testclient import TestClient

from tests.conftest import SubscriptionFactory


def test_search_by_target_url(client: TestClient, make_subscription: SubscriptionFactory) -> None:
    make_subscription(target_url="https://acme.example.com/hooks")
    make_subscription(target_url="https://globex.example.com/hooks")

    response = client.get("/subscriptions", params={"target_url": "acme"})

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_search_by_event_type(client: TestClient, make_subscription: SubscriptionFactory) -> None:
    make_subscription(event_types=["order.*"])
    make_subscription(event_types=["invoice.paid"])

    response = client.get("/subscriptions", params={"event_type": "order.created"})

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_search_combines_filters(
    client: TestClient, make_subscription: SubscriptionFactory
) -> None:
    make_subscription(target_url="https://acme.example.com/hooks", event_types=["order.*"])
    make_subscription(target_url="https://acme.example.com/hooks", active=False)
    make_subscription(target_url="https://globex.example.com/hooks", event_types=["order.*"])

    response = client.get(
        "/subscriptions",
        params={"target_url": "acme", "event_type": "order.created", "active": "true"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_pagination(client: TestClient, make_subscription: SubscriptionFactory) -> None:
    for _ in range(3):
        make_subscription()

    response = client.get("/subscriptions", params={"page": 1, "size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["size"] == 2


def test_page_must_be_positive(client: TestClient) -> None:
    assert client.get("/subscriptions", params={"page": 0}).status_code == 422
