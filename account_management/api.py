import os

import pydantic
from config import settings
from fastapi import APIRouter, HTTPException

from .adapter import JsonAccountRepository
from .logic import Account, AccountService

router = APIRouter()


class CreateAccountRequest(pydantic.BaseModel):
    balance: float = 0.0


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: str):
    repo = JsonAccountRepository(settings.account_database_folder)
    service = AccountService(account_repository=repo)
    account = service.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail={"message": "Account not found"})
    return account


@router.post("", response_model=Account)
def create_account(request: CreateAccountRequest):
    repo = JsonAccountRepository(settings.account_database_folder)
    service = AccountService(account_repository=repo)
    account = service.create(request.balance)
    return account
