from uuid import uuid4

import pydantic

from .model import Subscription
from .repo import SubscriptionRepository


class CreateSubscriptionCommand(pydantic.BaseModel):
    account_id: str
    price: float = pydantic.Field(..., ge=0)


class SubscriptionService:
    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repository = subscription_repository

    def create(self, command: CreateSubscriptionCommand) -> Subscription:
        sub_id = uuid4().hex
        sub = Subscription(
            id=sub_id,
            account_id=command.account_id,
            price=command.price,
        )
        self.subscription_repository.save(sub)
        return sub

    def get(self, sub_id: str) -> Subscription:
        sub = self.subscription_repository.find(sub_id)
        return sub

    def accept(self, sub_id: str) -> Subscription:
        sub = self.subscription_repository.find(sub_id)
        if not sub:
            raise ValueError(f"Subscription {sub_id} not found")
        sub.accept()
        self.subscription_repository.update(sub)
        return sub

    def reject(self, sub_id: str) -> Subscription:
        sub = self.subscription_repository.find(sub_id)
        if not sub:
            raise ValueError(f"Subscription {sub_id} not found")
        sub.reject()
        self.subscription_repository.update(sub)
        return sub
