import respx
from fastapi.testclient import TestClient

from tests.conftest import SubscriptionFactory

HOOK_URL = "https://example.com/hooks"


def _publish(client: TestClient, event_type: str = "order.created") -> None:
    assert client.post("/events", json={"type": event_type}).status_code == 202


def test_list_deliveries_newest_first(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).respond(200)
    make_subscription(target_url=HOOK_URL, event_types=["order.*"])
    _publish(client, "order.created")
    _publish(client, "order.shipped")

    body = client.get("/deliveries").json()

    assert [d["event_type"] for d in body] == ["order.shipped", "order.created"]


def test_list_deliveries_filters_by_subscription(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).respond(200)
    first = make_subscription(target_url=HOOK_URL)
    make_subscription(target_url=HOOK_URL)
    _publish(client)

    body = client.get(f"/deliveries?subscription_id={first['id']}").json()

    assert [d["subscription_id"] for d in body] == [first["id"]]


def test_list_deliveries_filters_by_success(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post("https://ok.example.com/").respond(200)
    receiver.post("https://broken.example.com/").respond(503)
    make_subscription(target_url="https://ok.example.com/")
    broken = make_subscription(target_url="https://broken.example.com/")
    _publish(client)

    failures = client.get("/deliveries?success=false").json()

    assert [d["subscription_id"] for d in failures] == [broken["id"]]


def test_list_deliveries_respects_limit(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).respond(200)
    make_subscription(target_url=HOOK_URL)
    for _ in range(3):
        _publish(client)

    assert len(client.get("/deliveries?limit=2").json()) == 2
    assert client.get("/deliveries?limit=0").status_code == 422
    assert client.get("/deliveries?limit=201").status_code == 422


def test_get_delivery(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).respond(200)
    make_subscription(target_url=HOOK_URL)
    _publish(client)
    delivery_id = client.get("/deliveries").json()[0]["id"]

    response = client.get(f"/deliveries/{delivery_id}")

    assert response.status_code == 200
    assert response.json()["id"] == delivery_id


def test_get_missing_delivery_returns_404(client: TestClient) -> None:
    assert client.get("/deliveries/999").status_code == 404


def test_deleting_subscription_removes_its_deliveries(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).respond(200)
    subscription = make_subscription(target_url=HOOK_URL)
    _publish(client)

    client.delete(f"/subscriptions/{subscription['id']}")

    assert client.get("/deliveries").json() == []
