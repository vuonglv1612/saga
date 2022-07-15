import os
import pydantic


class Settings(pydantic.BaseSettings):
    account_worker_amqp_uri: str
    account_worker_exchange: str = "account_management"
    account_worker_queue: str
    account_database_folder: str
    account_withdraw_response_exchange: str
    account_withdraw_response_queue: str

    subscription_database_folder: str
    subscription_worker_amqp_uri: str
    subscription_worker_exchange: str = "subscription_management"
    subscription_worker_queue: str


if os.getenv("DEBUG", "0") == "1":
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

settings = Settings()
