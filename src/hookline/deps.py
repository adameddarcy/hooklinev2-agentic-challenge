"""FastAPI dependencies shared by the routers."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from hookline.db import session_scope
from hookline.models import Subscription
from hookline.repository import DeliveryRepository, SubscriptionRepository
from hookline.services.dispatcher import Dispatcher


def get_session(request: Request) -> Iterator[Session]:
    """Yield a database session for the length of one request."""
    yield from session_scope(request.app.state.session_factory)


SessionDep = Annotated[Session, Depends(get_session)]


def get_subscription_repository(session: SessionDep) -> SubscriptionRepository:
    return SubscriptionRepository(session)


def get_delivery_repository(session: SessionDep) -> DeliveryRepository:
    return DeliveryRepository(session)


def get_dispatcher(request: Request) -> Dispatcher:
    dispatcher: Dispatcher = request.app.state.dispatcher
    return dispatcher


SubscriptionRepoDep = Annotated[SubscriptionRepository, Depends(get_subscription_repository)]
DeliveryRepoDep = Annotated[DeliveryRepository, Depends(get_delivery_repository)]
DispatcherDep = Annotated[Dispatcher, Depends(get_dispatcher)]


def get_subscription_or_404(subscription_id: int, repo: SubscriptionRepoDep) -> Subscription:
    """Look up the subscription in the path, or raise a 404."""
    subscription = repo.get(subscription_id)
    if subscription is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return subscription


SubscriptionDep = Annotated[Subscription, Depends(get_subscription_or_404)]
