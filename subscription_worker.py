import pika

from common.publisher import RabbitMQPublisher
from common.worker.rabbitmq_worker import RabbitmqWorker
from config import settings
from subscription_management.adapter import JsonSubscriptionAdapter
from subscription_management.service import (
    CreateSubscriptionCommand,
    SubscriptionService,
)


def subscribe_factory(publisher_connection, exchange, queue):
    publisher = RabbitMQPublisher(publisher_connection)

    def create_sub_handler(message: dict):
        repo = JsonSubscriptionAdapter(settings.subscription_database_folder)
        service = SubscriptionService(subscription_repository=repo)
        command_id = message.get("command_id")
        command = CreateSubscriptionCommand(
            account_id=message["account_id"], price=message["price"]
        )
        try:
            sub = service.create(command)
        except ValueError as e:
            publisher.publish(
                {"command_id": command_id, "status": "failed", "reason": str(e)},
                exchange,
                queue,
            )
            return
        else:
            publisher.publish(
                {
                    "command_id": command_id,
                    "status": "succeeded",
                    "subscription": sub.dict(),
                },
                exchange,
                queue,
            )
            print("CREATED SUB: ", sub.dict())
        return sub.dict()

    return create_sub_handler


def accept_subscribe_factory(publisher_connection, exchange, queue):
    publisher = RabbitMQPublisher(publisher_connection)

    def accept_subscribe_handler(message: dict):
        repo = JsonSubscriptionAdapter(settings.subscription_database_folder)
        service = SubscriptionService(subscription_repository=repo)
        command_id = message.get("command_id")
        sub_id = message["subscription_id"]
        try:
            sub = service.accept(sub_id=sub_id)
        except ValueError as e:
            publisher.publish(
                {"command_id": command_id, "status": "failed", "reason": str(e)},
                exchange,
                queue,
            )
            return
        else:
            publisher.publish(
                {
                    "command_id": command_id,
                    "status": "succeeded",
                    "account": sub.dict(),
                },
                exchange,
                queue,
            )
        print("ACCEPTED SUBSCRIBE: ", sub.dict())
        return sub.dict()

    return accept_subscribe_handler


def reject_subscribe_factory(publisher_connection, exchange, queue):
    publisher = RabbitMQPublisher(publisher_connection)

    def reject_subscribe_handler(message: dict):
        repo = JsonSubscriptionAdapter(settings.subscription_database_folder)
        service = SubscriptionService(subscription_repository=repo)
        command_id = message.get("command_id")
        sub_id = message["subscription_id"]
        try:
            sub = service.reject(sub_id=sub_id)
        except ValueError as e:
            publisher.publish(
                {"command_id": command_id, "status": "failed", "reason": str(e)},
                exchange,
                queue,
            )
            return
        else:
            publisher.publish(
                {
                    "command_id": command_id,
                    "status": "succeeded",
                    "account": sub.dict(),
                },
                exchange,
                queue,
            )
        print("REJECTED SUBSCRIBE: ", sub.dict())
        return sub.dict()

    return reject_subscribe_handler


def main():
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.subscription_worker_amqp_uri)
    )
    publisher_connection = pika.BlockingConnection(
        pika.URLParameters(settings.saga_amqp_uri)
    )
    worker = RabbitmqWorker(
        connection,
        settings.subscription_worker_exchange,
        settings.subscription_worker_queue,
    )
    worker.register_callback(
        "subscribe",
        subscribe_factory(
            publisher_connection,
            exchange=settings.saga_exchange,
            queue=settings.saga_queue,
        ),
    )
    worker.register_callback(
        "accept_subscribe",
        accept_subscribe_factory(
            publisher_connection,
            settings.saga_exchange,
            settings.saga_queue,
        ),
    )
    worker.register_callback(
        "reject_subscribe",
        reject_subscribe_factory(
            publisher_connection,
            settings.saga_exchange,
            settings.saga_queue,
        ),
    )
    worker.start()


if __name__ == "__main__":
    main()
