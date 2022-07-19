import json
import pika


class RabbitMQPublisher:
    def __init__(self, connection: pika.BlockingConnection):
        self._connection = connection
        self._channel = connection.channel()

    def publish(self, message: dict, exchange: str, queue: str):
        self._channel.exchange_declare(exchange=exchange, exchange_type="direct")
        self._channel.queue_declare(queue=queue)
        self._channel.queue_bind(exchange=exchange, queue=queue, routing_key=queue)
        self._channel.basic_publish(
            exchange=exchange, routing_key=queue, body=json.dumps(message)
        )
        print(" [x] Sent %r" % message)
        self._channel.close()
        return True
