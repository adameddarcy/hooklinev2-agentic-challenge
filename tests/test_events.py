import json

import httpx
import respx
from fastapi.testclient import TestClient

from hookline.services.dispatcher import (
    EVENT_HEADER,
    EVENT_ID_HEADER,
    SIGNATURE_HEADER,
    TIMESTAMP_HEADER,
)
from hookline.services.signing import verify_signature
from tests.conftest import SubscriptionFactory

HOOK_URL = "https://example.com/hooks"


def test_event_is_delivered_with_valid_signature(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    route = receiver.post(HOOK_URL).respond(204)
    subscription = make_subscription(target_url=HOOK_URL)

    response = client.post("/events", json={"type": "order.created", "payload": {"order_id": 42}})

    assert response.status_code == 202
    body = response.json()
    assert len(body["deliveries"]) == 1
    delivery = body["deliveries"][0]
    assert delivery["subscription_id"] == subscription["id"]
    assert delivery["status_code"] == 204
    assert delivery["success"] is True

    request = route.calls.last.request
    assert request.headers[EVENT_HEADER] == "order.created"
    assert request.headers[EVENT_ID_HEADER] == body["event_id"]
    assert verify_signature(
        subscription["secret"],
        request.content,
        int(request.headers[TIMESTAMP_HEADER]),
        request.headers[SIGNATURE_HEADER],
    )
    assert json.loads(request.content) == {
        "id": body["event_id"],
        "type": "order.created",
        "payload": {"order_id": 42},
    }


def test_wildcard_subscription_receives_event(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    route = receiver.post(HOOK_URL).respond(200)
    make_subscription(target_url=HOOK_URL, event_types=["order.*"])

    client.post("/events", json={"type": "order.refunded"})

    assert route.call_count == 1


def test_event_is_not_delivered_to_non_matching_subscription(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    route = receiver.post(HOOK_URL).respond(200)
    make_subscription(target_url=HOOK_URL, event_types=["order.created"])

    response = client.post("/events", json={"type": "order.created_v2"})

    assert response.status_code == 202
    assert response.json()["deliveries"] == []
    assert not route.called


def test_inactive_subscription_is_skipped(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    route = receiver.post(HOOK_URL).respond(200)
    subscription = make_subscription(target_url=HOOK_URL)
    client.patch(f"/subscriptions/{subscription['id']}", json={"active": False})

    response = client.post("/events", json={"type": "order.created"})

    assert response.json()["deliveries"] == []
    assert not route.called


def test_event_fans_out_to_every_matching_subscription(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    first = receiver.post("https://one.example.com/hooks").respond(200)
    second = receiver.post("https://two.example.com/hooks").respond(200)
    make_subscription(target_url="https://one.example.com/hooks", event_types=["*"])
    make_subscription(target_url="https://two.example.com/hooks", event_types=["order.*"])

    response = client.post("/events", json={"type": "order.created"})

    assert len(response.json()["deliveries"]) == 2
    assert first.call_count == 1
    assert second.call_count == 1


def test_each_subscription_is_signed_with_its_own_secret(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    first = receiver.post("https://one.example.com/hooks").respond(200)
    second = receiver.post("https://two.example.com/hooks").respond(200)
    sub_one = make_subscription(target_url="https://one.example.com/hooks")
    sub_two = make_subscription(target_url="https://two.example.com/hooks")

    client.post("/events", json={"type": "order.created"})

    for route, sub in ((first, sub_one), (second, sub_two)):
        request = route.calls.last.request
        assert verify_signature(
            sub["secret"],
            request.content,
            int(request.headers[TIMESTAMP_HEADER]),
            request.headers[SIGNATURE_HEADER],
        )


def test_failed_delivery_is_recorded(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).respond(500)
    make_subscription(target_url=HOOK_URL)

    delivery = client.post("/events", json={"type": "order.created"}).json()["deliveries"][0]

    assert delivery["status_code"] == 500
    assert delivery["success"] is False
    assert delivery["error"] is None


def test_connection_error_is_recorded(
    client: TestClient, receiver: respx.MockRouter, make_subscription: SubscriptionFactory
) -> None:
    receiver.post(HOOK_URL).mock(side_effect=httpx.ConnectTimeout("timed out"))
    make_subscription(target_url=HOOK_URL)

    delivery = client.post("/events", json={"type": "order.created"}).json()["deliveries"][0]

    assert delivery["status_code"] is None
    assert delivery["success"] is False
    assert delivery["error"] == "ConnectTimeout: timed out"


def test_event_with_no_subscribers_is_accepted(client: TestClient) -> None:
    response = client.post("/events", json={"type": "ping"})

    assert response.status_code == 202
    assert response.json()["deliveries"] == []


def test_event_type_is_validated(client: TestClient) -> None:
    assert client.post("/events", json={"type": "order.*"}).status_code == 422
    assert client.post("/events", json={"payload": {}}).status_code == 422
