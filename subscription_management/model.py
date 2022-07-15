import pydantic


class Subscription(pydantic.BaseModel):
    id: str
    account_id: str
    price: float
    state: str = "pending"

    def accept(self):
        if self.state == "pending":
            self.state = "accepted"
        else:
            raise ValueError("Subscription is not pending")

    def reject(self):
        if self.state == "pending":
            self.state = "rejected"
        else:
            raise ValueError("Subscription is not pending")


class CreateSubscriptionSagaState(pydantic.BaseModel):
    id: str
    state: str = "not_started"
    failed_reason: str = None

    def account_validated(self):
        self.state = "account_validated"

    def succeeded(self):
        self.state = "succeeded"

    def failed(self, reason: str):
        self.state = "failed"
        self.failed_reason = reason

    def is_finished(self):
        return self.state in ["succeeded", "failed"]
