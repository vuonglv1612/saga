import pydantic
from config import settings
from fastapi import APIRouter, HTTPException

from .adapter import JsonSubscriptionAdapter
from .model import Subscription
from .service import CreateSubscriptionCommand, SubscriptionService

router = APIRouter()


class CreateSubscriptionAPIRequest(pydantic.BaseModel):
    account_id: str
    price: float = pydantic.Field(..., ge=0)


@router.get("/{sub_id}", response_model=Subscription)
def get_subscription(sub_id: str):
    repo = JsonSubscriptionAdapter(settings.subscription_database_folder)
    service = SubscriptionService(repo)
    sub = service.get(sub_id)
    if not sub:
        raise HTTPException(
            status_code=404, detail={"message": f"Subscription {sub_id} not found"}
        )
    return sub


@router.post("/", response_model=Subscription)
def create_subscription(command: CreateSubscriptionAPIRequest):
    repo = JsonSubscriptionAdapter(settings.subscription_database_folder)
    service = SubscriptionService(repo)
    command = CreateSubscriptionCommand(
        account_id=command.account_id, price=command.price
    )
    sub = service.create(command=command)
    return sub
