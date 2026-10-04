"""Pydantic models for request and response bodies."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, StringConstraints

EVENT_TYPE_REGEX = r"^[a-z0-9_]+(\.[a-z0-9_]+)*$"
"""A concrete event type, e.g. ``order.created``."""

EVENT_PATTERN_REGEX = r"^(\*|[a-z0-9_]+(\.[a-z0-9_]+)*(\.\*)?)$"
"""An event type, optionally ending in a ``.*`` wildcard, or a bare ``*``."""

EventType = Annotated[str, StringConstraints(pattern=EVENT_TYPE_REGEX, max_length=100)]
EventPattern = Annotated[str, StringConstraints(pattern=EVENT_PATTERN_REGEX, max_length=100)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]


class SubscriptionCreate(BaseModel):
    """Body for ``POST /subscriptions``."""

    model_config = ConfigDict(extra="forbid")

    target_url: AnyHttpUrl
    event_types: list[EventPattern] = Field(min_length=1, max_length=50)
    description: Description | None = None
    active: bool = True


class SubscriptionUpdate(BaseModel):
    """Body for ``PATCH /subscriptions/{id}``. Every field is optional."""

    model_config = ConfigDict(extra="forbid")

    target_url: AnyHttpUrl | None = None
    event_types: list[EventPattern] = Field(default_factory=list, max_length=50)
    description: Description | None = None
    active: bool | None = None


class SubscriptionRead(BaseModel):
    """Public representation of a subscription. Never includes the secret."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    target_url: str
    event_types: list[str]
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class SubscriptionCreated(SubscriptionRead):
    """Returned once, on creation: the only time the signing secret is shown."""

    secret: str


class SubscriptionPage(BaseModel):
    """A page of subscriptions, with the total number of matches."""

    items: list[SubscriptionCreated]
    page: int
    size: int
    total: int


class EventIn(BaseModel):
    """Body for ``POST /events``."""

    model_config = ConfigDict(extra="forbid")

    type: EventType
    payload: dict[str, Any] = Field(default_factory=dict)


class DeliveryRead(BaseModel):
    """A recorded delivery attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    subscription_id: int
    event_id: str
    event_type: str
    status_code: int | None
    success: bool
    error: str | None
    created_at: datetime


class EventAccepted(BaseModel):
    """Response for ``POST /events``."""

    event_id: str
    deliveries: list[DeliveryRead]
