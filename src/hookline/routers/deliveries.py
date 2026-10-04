"""Read-only access to the delivery log."""

from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from hookline.deps import DeliveryRepoDep
from hookline.models import Delivery
from hookline.schemas import DeliveryRead

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("", response_model=list[DeliveryRead])
def list_deliveries(
    repo: DeliveryRepoDep,
    subscription_id: int | None = None,
    success: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> Sequence[Delivery]:
    """List recent deliveries, newest first."""
    return repo.find(subscription_id=subscription_id, success=success, limit=limit)


@router.get("/{delivery_id}", response_model=DeliveryRead)
def get_delivery(delivery_id: int, repo: DeliveryRepoDep) -> Delivery:
    """Fetch one delivery attempt."""
    delivery = repo.get(delivery_id)
    if delivery is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return delivery
