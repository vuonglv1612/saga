from fastapi import FastAPI

from account_management.api import router as account_management_router
from subscription_management.api import router as subscription_management_router

app = FastAPI(title="Billing Service")


app.include_router(account_management_router, prefix="/accounts", tags=["accounts"])
app.include_router(
    subscription_management_router, prefix="/subscriptions", tags=["subscriptions"]
)
