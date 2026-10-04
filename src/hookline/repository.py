"""Persistence for subscriptions and deliveries."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from hookline.models import Delivery, Subscription
from hookline.schemas import SubscriptionCreate, SubscriptionUpdate
from hookline.services.dispatcher import DeliveryAttempt
from hookline.services.matching import matches_any
from hookline.services.signing import generate_secret


class SubscriptionRepository:
    """CRUD operations for :class:`Subscription`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, data: SubscriptionCreate) -> Subscription:
        """Create a subscription with a newly generated signing secret."""
        subscription = Subscription(
            target_url=str(data.target_url),
            event_types=list(data.event_types),
            description=data.description,
            active=data.active,
            secret=generate_secret(),
        )
        self._session.add(subscription)
        self._session.commit()
        return subscription

    def get(self, subscription_id: int) -> Subscription | None:
        """Return the subscription with ``subscription_id``, or ``None``."""
        return self._session.get(Subscription, subscription_id)

    def find(self, *, active: bool | None = None) -> Sequence[Subscription]:
        """Return subscriptions ordered by id, optionally filtered by ``active``."""
        query = select(Subscription).order_by(Subscription.id)
        if active is not None:
            query = query.where(Subscription.active == active)
        return self._session.scalars(query).all()

    def update(self, subscription: Subscription, changes: SubscriptionUpdate) -> Subscription:
        """Apply ``changes`` to ``subscription``."""
        for field, value in changes.model_dump(exclude_none=True).items():
            if field == "target_url":
                value = str(value)
            setattr(subscription, field, value)
        self._session.commit()
        return subscription

    def delete(self, subscription: Subscription) -> None:
        """Delete ``subscription`` and its delivery history."""
        self._session.delete(subscription)
        self._session.commit()

    def matching(self, event_type: str) -> list[Subscription]:
        """Return active subscriptions with a pattern that selects ``event_type``."""
        return [sub for sub in self.find(active=True) if matches_any(sub.event_types, event_type)]


class DeliveryRepository:
    """Storage for delivery attempts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def record(
        self, event_id: str, event_type: str, attempts: Sequence[DeliveryAttempt]
    ) -> list[Delivery]:
        """Save ``attempts`` for an event and return the stored rows."""
        deliveries = [
            Delivery(
                subscription_id=attempt.subscription_id,
                event_id=event_id,
                event_type=event_type,
                status_code=attempt.status_code,
                success=attempt.success,
                error=attempt.error,
            )
            for attempt in attempts
        ]
        self._session.add_all(deliveries)
        self._session.commit()
        return deliveries

    def get(self, delivery_id: int) -> Delivery | None:
        """Return the delivery with ``delivery_id``, or ``None``."""
        return self._session.get(Delivery, delivery_id)

    def find(
        self,
        *,
        subscription_id: int | None = None,
        success: bool | None = None,
        limit: int = 50,
    ) -> Sequence[Delivery]:
        """Return the most recent deliveries first, with optional filters."""
        query = select(Delivery).order_by(Delivery.id.desc()).limit(limit)
        if subscription_id is not None:
            query = query.where(Delivery.subscription_id == subscription_id)
        if success is not None:
            query = query.where(Delivery.success == success)
        return self._session.scalars(query).all()
