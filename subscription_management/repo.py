from typing import Union
from .model import CreateSubscriptionSagaState, Subscription


class SubscriptionRepository:
    def save(self, subscription: Subscription):
        raise NotImplementedError()

    def find(self, sub_id) -> Union[Subscription, None]:
        raise NotImplementedError()

    def update(self, subscription: Subscription):
        raise NotImplementedError()


class CreateSubscriptionSagaStateRepo:
    def save(self, state: CreateSubscriptionSagaState):
        raise NotImplementedError()

    def find(self, state_id) -> Union[CreateSubscriptionSagaState, None]:
        raise NotImplementedError()

    def update(self, state: CreateSubscriptionSagaState):
        raise NotImplementedError()
