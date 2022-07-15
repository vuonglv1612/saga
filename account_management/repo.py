from typing import Union
from .model import Account


class AccountRepository:
    def create(self, account: Account):
        raise NotImplementedError()
    
    def find(self, account_id: str) -> Union[Account, None]:
        raise NotImplementedError()
    
    def save(self, account: Account):
        raise NotImplementedError()
    
    def update(self, account: Account):
        raise NotImplementedError()
