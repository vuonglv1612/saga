from uuid import uuid4
from .model import Account
from .repo import AccountRepository


class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository
    
    def create(self, balance: float = 0.0):
        account_id = uuid4().hex
        account = Account(id=account_id, balance=balance)
        self.account_repository.save(account)
        return account
    
    def get(self, account_id: str):
        account = self.account_repository.find(account_id)
        return account
    
    def deposit(self, account_id: str, amount: float):
        account = self.account_repository.find(account_id)
        account.deposit(amount)
        self.account_repository.update(account)
        return account
    
    def withdraw(self, account_id: str, amount: float):
        account = self.account_repository.find(account_id)
        account.withdraw(amount)
        self.account_repository.update(account)
        return account
