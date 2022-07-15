import pydantic

class Account(pydantic.BaseModel):
    id: str
    balance: float

    def deposit(self, amount: float = pydantic.Field(..., gt=0)):
        self.balance += amount
    
    def withdraw(self, amount: float = pydantic.Field(..., gt=0)):
        if amount > self.balance:
            raise ValueError("Cannot deposit more than balance")
        self.balance -= amount
