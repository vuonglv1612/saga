import json

import pika

from config import settings

message = {
    "command_id": "123",
    "type": "deposit_account_balance",
    "account_id": "74a35cae933a4e4892d7d49543867ef8",
    "amount": "10000",
}


def main():
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.account_worker_amqp_uri)
    )
    channel = connection.channel()
    channel.basic_publish(
        exchange=settings.account_worker_exchange,
        routing_key=settings.account_worker_queue,
        body=json.dumps(message),
    )
    connection.close()
    print(" [x] Sent message {} to {}".format(message, settings.account_worker_queue))


if __name__ == "__main__":
    main()
