import os
from .repo import AccountRepository, Account
import json


class JsonAccountRepository(AccountRepository):
    def __init__(self, folder: str):
        self.folder = folder
    
    def _get_file_name(self, account_id: str):
        return self.folder + "/" + account_id + ".json"

    def create(self, account: Account):
        with open(self._get_file_name(account.id), "w") as f:
            json.dump(account.dict(), f)
    
    def find(self, account_id: str):
        # check if file not exist
        if not os.path.isfile(self._get_file_name(account_id)):
            return None
        with open(self._get_file_name(account_id), "r") as f:
            data = json.load(f)
            return Account(**data)
    
    def update(self, account: Account):
        with open(self._get_file_name(account.id), "w") as f:
            json.dump(account.dict(), f)
        
    def save(self, account: Account):
        with open(self._get_file_name(account.id), "w") as f:
            json.dump(account.dict(), f)
