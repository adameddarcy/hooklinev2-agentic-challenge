"""CRUD endpoints for subscriptions."""

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from hookline.deps import SubscriptionDep, SubscriptionRepoDep
from hookline.models import Subscription
from hookline.schemas import (
    SubscriptionCreate,
    SubscriptionCreated,
    SubscriptionPage,
    SubscriptionRead,
    SubscriptionUpdate,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SubscriptionCreated)
def create_subscription(data: SubscriptionCreate, repo: SubscriptionRepoDep) -> Subscription:
    """Create a subscription. The response is the only place the secret is shown."""
    return repo.create(data)


@router.get("", response_model=SubscriptionPage)
def list_subscriptions(
    repo: SubscriptionRepoDep,
    active: bool | None = None,
    target_url: str | None = None,
    event_type: str | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: int = 20,
) -> SubscriptionPage:
    """List subscriptions, filtered and paginated.

    ``target_url`` matches any part of the URL; ``event_type`` returns the subscriptions
    that would receive that event.
    """
    items, total = repo.search(
        active=active, target_url=target_url, event_type=event_type, page=page, size=size
    )
    return SubscriptionPage.model_validate(
        {"items": items, "page": page, "size": size, "total": total}, from_attributes=True
    )


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
