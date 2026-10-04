"""Event ingestion: accept an event and deliver it to matching subscribers."""

import uuid

from fastapi import APIRouter, status

from hookline.deps import DeliveryRepoDep, DispatcherDep, SubscriptionRepoDep
from hookline.schemas import DeliveryRead, EventAccepted, EventIn

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=EventAccepted)
async def publish_event(
    event: EventIn,
    subscriptions: SubscriptionRepoDep,
    deliveries: DeliveryRepoDep,
    dispatcher: DispatcherDep,
) -> EventAccepted:
    """Deliver ``event`` to every active, matching subscription."""
    event_id = str(uuid.uuid4())
    targets = subscriptions.matching(event.type)
    attempts = await dispatcher.dispatch(event_id, event.type, event.payload, targets)
    stored = deliveries.record(event_id, event.type, attempts)
    return EventAccepted(
        event_id=event_id,
        deliveries=[DeliveryRead.model_validate(d) for d in stored],
    )
