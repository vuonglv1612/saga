import json

import pika
from common.worker.base import Worker


class RabbitmqWorker(Worker):
    def __init__(self, connection: pika.BlockingConnection, exchange: str, queue: str):

        super().__init__()

        self._connection = connection
        self._channel = connection.channel()
        self._exchange = exchange
        self._queue = queue
        self._channel.exchange_declare(exchange=exchange, exchange_type="direct")
        self._channel.queue_declare(queue=self._queue)
        self._channel.queue_bind(exchange=exchange, queue=self._queue, routing_key=queue)

    def start(self):
        # graceful shutdown of the worker
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self._queue, self._callback)
        self._channel.start_consuming()

    def _callback(self, ch, method, properties, body):
        message = json.loads(body)
        self.handle_message(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
