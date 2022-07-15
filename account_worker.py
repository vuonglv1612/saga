import pika

from account_management.adapter import JsonAccountRepository
from account_management.logic import AccountService
from common.publisher import RabbitMQPublisher
from common.worker.rabbitmq_worker import RabbitmqWorker
from config import settings


def deposit_account_balance_factory(publisher, exchange, queue):
    def deposit_account_balance(message: dict):
        repo = JsonAccountRepository(settings.account_database_folder)
        service = AccountService(account_repository=repo)
        command_id = message.get("command_id")
        account_id = message["account_id"]
        amount = float(message["amount"])
        try:
            account = service.deposit(account_id, amount)
        except ValueError as e:
            publisher.publish(
                {"command_id": command_id, "status": "failed", "reason": str(e)},
                exchange,
                queue,
            )
        else:
            publisher.publish(
                {
                    "command_id": command_id,
                    "status": "succeeded",
                    "account": account.dict(),
                },
                exchange,
                queue,
            )
            print("DEPOSIT ACCOUNT: ", account.dict())
        return account.dict()

    return deposit_account_balance


def withdraw_account_balance_factory(publisher, exchange, queue):
    def withdraw_account_balance(message: dict):
        repo = JsonAccountRepository(settings.account_database_folder)
        service = AccountService(account_repository=repo)
        command_id = message.get("command_id")
        account_id = message["account_id"]
        amount = float(message["amount"])
        try:
            account = service.withdraw(account_id, amount)
        except ValueError as e:
            publisher.publish(
                {"command_id": command_id, "status": "failed", "reason": str(e)},
                exchange,
                queue,
            )
        else:
            publisher.publish(
                {
                    "command_id": command_id,
                    "status": "succeeded",
                    "account": account.dict(),
                },
                exchange,
                queue,
            )
        print("WITHDRAW ACCOUNT: ", account.dict())
        return account.dict()

    return withdraw_account_balance


def main():
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.account_worker_amqp_uri)
    )
    publisher_connection = pika.BlockingConnection(
        pika.URLParameters(settings.account_worker_amqp_uri)
    )
    publisher = RabbitMQPublisher(publisher_connection)
    worker = RabbitmqWorker(connection, settings.account_worker_exchange, settings.account_worker_queue)
    worker.register_callback(
        "deposit_account_balance",
        deposit_account_balance_factory(publisher, "something", "somequeue"),
    )
    worker.register_callback(
        "withdraw_account_balance",
        withdraw_account_balance_factory(
            publisher,
            settings.account_withdraw_response_exchange,
            settings.account_withdraw_response_queue,
        ),
    )
    worker.start()


if __name__ == "__main__":
    main()
