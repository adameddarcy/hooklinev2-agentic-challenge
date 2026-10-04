"""CRUD endpoints for subscriptions."""

from collections.abc import Sequence

from fastapi import APIRouter, Response, status

from hookline.deps import SubscriptionDep, SubscriptionRepoDep
from hookline.models import Subscription
from hookline.schemas import (
    SubscriptionCreate,
    SubscriptionCreated,
    SubscriptionRead,
    SubscriptionUpdate,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SubscriptionCreated)
def create_subscription(data: SubscriptionCreate, repo: SubscriptionRepoDep) -> Subscription:
    """Create a subscription. The response is the only place the secret is shown."""
    return repo.create(data)


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(
    repo: SubscriptionRepoDep, active: bool | None = None
) -> Sequence[Subscription]:
    """List subscriptions, optionally only active or inactive ones."""
    return repo.find(active=active)


@router.get("/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(subscription: SubscriptionDep) -> Subscription:
    """Fetch one subscription."""
    return subscription


@router.patch("/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(
    subscription: SubscriptionDep, changes: SubscriptionUpdate, repo: SubscriptionRepoDep
) -> Subscription:
    """Partially update a subscription."""
    return repo.update(subscription, changes)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(subscription: SubscriptionDep, repo: SubscriptionRepoDep) -> Response:
    """Delete a subscription and its delivery history."""
    repo.delete(subscription)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
