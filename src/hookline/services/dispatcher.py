"""Fan-out of a single event to every matching subscription."""

import asyncio
import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import httpx

from hookline.models import Subscription
from hookline.services.signing import sign_payload

SIGNATURE_HEADER = "X-Hookline-Signature"
TIMESTAMP_HEADER = "X-Hookline-Timestamp"
EVENT_HEADER = "X-Hookline-Event"
EVENT_ID_HEADER = "X-Hookline-Event-Id"


@dataclass(frozen=True, slots=True)
class DeliveryAttempt:
    """The outcome of a single POST to a subscriber."""

    subscription_id: int
    status_code: int | None
    success: bool
    error: str | None = None


def encode_body(event_id: str, event_type: str, payload: dict[str, Any]) -> bytes:
    """Serialise the webhook body deterministically, so signatures are reproducible."""
    envelope = {"id": event_id, "type": event_type, "payload": payload}
    return json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode()


class Dispatcher:
    """Sends signed webhook requests concurrently."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        timeout_seconds: float,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._client = client
        self._timeout = timeout_seconds
        self._clock = clock

    async def dispatch(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        subscriptions: Sequence[Subscription],
    ) -> list[DeliveryAttempt]:
        """Deliver one event to each subscription and return every attempt."""
        body = encode_body(event_id, event_type, payload)
        timestamp = int(self._clock())
        return list(
            await asyncio.gather(
                *(
                    self._deliver(sub, event_id, event_type, body, timestamp)
                    for sub in subscriptions
                )
            )
        )

    async def _deliver(
        self,
        subscription: Subscription,
        event_id: str,
        event_type: str,
        body: bytes,
        timestamp: int,
    ) -> DeliveryAttempt:
        headers = {
            "Content-Type": "application/json",
            SIGNATURE_HEADER: sign_payload(subscription.secret, body, timestamp),
            TIMESTAMP_HEADER: str(timestamp),
            EVENT_HEADER: event_type,
            EVENT_ID_HEADER: event_id,
        }
        try:
            response = await self._client.post(
                subscription.target_url, content=body, headers=headers, timeout=self._timeout
            )
        except httpx.HTTPError as exc:
            return DeliveryAttempt(
                subscription_id=subscription.id,
                status_code=None,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )
        return DeliveryAttempt(
            subscription_id=subscription.id,
            status_code=response.status_code,
            success=response.is_success,
        )
