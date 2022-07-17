import json
from typing import Callable, List, Optional

import pika


class SagaStateRepository:
    def action_started(self, saga_id: str, step_name: str):
        raise NotImplementedError()

    def action_succeeded(self, saga_id: str, step_name: str):
        raise NotImplementedError()

    def action_failed(self, saga_id: str, step_name: str, error_type: str, error: str):
        raise NotImplementedError()

    def compensation_started(self, saga_id: str, step_name: str):
        raise NotImplementedError()

    def compensation_succeeded(self, saga_id: str, step_name: str):
        raise NotImplementedError()

    def compensation_failed(
        self, saga_id: str, step_name: str, error_type: str, error: str
    ):
        raise NotImplementedError()

    def saga_compensate_failed(
        self, saga_id: str, step_name: str, error_type: str, error: str
    ):
        raise NotImplementedError()

    def saga_completed(self, saga_id: str):
        raise NotImplementedError()

    def saga_failed(self, saga_id: str, step_name: str, error_type: str, error: str):
        raise NotImplementedError()


class SagaStep:
    def __init__(
        self,
        name: str,
        action: Callable,
        compensation: Callable,
        previous_step: Optional["SagaStep"] = None,
        next_step: Optional["SagaStep"] = None,
    ) -> None:
        self.name = name
        self.action = action
        self.compensation = compensation
        self.previous_step = previous_step
        self.next_step = next_step


class Saga:
    def __init__(self, name: str) -> None:
        self.name = name
        self._steps = []
        self._steps_map = {}

    def list_steps(self) -> List[SagaStep]:
        return self._steps

    def first_step(self) -> SagaStep:
        return self._steps[0]

    def last_step(self) -> SagaStep:
        return self._steps[-1]

    def get_step(self, name: str) -> SagaStep:
        return self._steps[self._steps_map[name]]

    def add_step(self, step: SagaStep) -> None:
        self._steps.append(step)
        index = len(self._steps) - 1
        self._steps_map[step.name] = index
        if index != 0:
            step.previous_step = self._steps[index - 1]
            self._steps[index - 1].next_step = step


class SagaWatcher:
    pass


class SagaIgniter:
    pass


class SagaExecutionController:
    def __init__(self, saga_state_repository: SagaStateRepository):
        self._state_repository = saga_state_repository
        self._sagas = {}

    def add_saga(self, saga: Saga):
        self._sagas[saga.name] = saga

    def _send_next_step_command(self, payload):
        raise NotImplementedError()

    def _send_compensation_command(self, payload):
        raise NotImplementedError()

    def _run_action_command(self, step: SagaStep, message):
        saga_id = message["saga_id"]
        self._state_repository.action_started(saga_id, step.name)
        try:
            result = step.action(message)
        except Exception as e:
            self._state_repository.action_failed(
                saga_id, step.name, error_type=type(e).__name__, error=str(e)
            )
            payload = {
                "saga_id": message["saga_id"],
                "saga_name": message["saga_name"],
                "step_name": step.name,
                "step_type": "compensation",
                "payload": message["payload"],
                "error_type": type(e).__name__,
                "error": str(e),
            }
            self._send_compensation_command(payload)
        else:
            self._state_repository.action_succeeded(saga_id, step.name)
            if not step.next_step:
                self._state_repository.saga_completed(saga_id)
            else:
                payload = {
                    "saga_id": message["saga_id"],
                    "saga_name": message["saga_name"],
                    "step_name": step.next_step.name,
                    "step_type": "action",
                    "payload": result,
                }
                self._send_next_step_command(payload)

    def _run_compensation_command(self, step: SagaStep, message):
        saga_id = message["saga_id"]
        self._state_repository.compensation_started(saga_id, step.name)
        try:
            result = step.compensation(message)
        except Exception as e:
            self._state_repository.saga_compensate_failed(
                saga_id, step.name, error_type=type(e).__name__, error=str(e)
            )
        else:
            self._state_repository.compensation_succeeded(saga_id, step.name)
            if not step.previous_step:
                self._state_repository.saga_failed(
                    saga_id,
                    step.name,
                    error_type=message["error_type"],
                    error=message["error"],
                )
            else:
                payload = {
                    "saga_id": message["saga_id"],
                    "saga_name": message["saga_name"],
                    "step_name": step.previous_step.name,
                    "step_type": "compensation",
                    "payload": result,
                    "error_type": message["error_type"],
                    "error": message["error"],
                }
                self._send_compensation_command(payload)

    def _handle_message(self, message):
        saga_id = message["saga_id"]
        saga_name = message["saga_name"]
        step_name = message["step_name"]
        step_type = message["step_type"]
        saga = self._sagas.get(saga_name)
        if not saga:
            raise LookupError(f"[{saga_id}]Saga {saga_name} not found")
        step = saga.get_step(step_name)
        if not step:
            raise LookupError(f"[{saga_id}]Step {step_name} not found")
        if step_type == "action":
            self._run_action_command(step, message)
        elif step_type == "compensation":
            self._run_compensation_command(step, message)
        else:
            raise ValueError(f"[{saga_id}]Unknown step type {step_type}")

    def run(self):
        raise NotImplementedError()


class RabbitMQSagaExecutionController(SagaExecutionController):
    def __init__(
        self,
        saga_state_repository,
        rabbitmq_connection: pika.BlockingConnection,
        exchange: str,
        queue: str,
    ):
        super().__init__(saga_state_repository)
        self._rabbitmq_connection = rabbitmq_connection
        self._exchange = exchange
        self._queue = queue

    def _send_next_step_command(self, payload):
        channel = self._rabbitmq_connection.channel()
        channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._queue,
            body=json.dumps(payload),
        )
        channel.close()

    def _send_compensation_command(self, payload):
        channel = self._rabbitmq_connection.channel()
        channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._queue,
            body=json.dumps(payload),
        )
        channel.close()

    def _callback(self, ch, method, properties, body):
        message = json.loads(body)
        self._handle_message(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        channel = self._rabbitmq_connection.channel()
        channel.queue_declare(queue=self._queue)
        channel.exchange_declare(exchange=self._exchange)
        channel.queue_bind(
            exchange=self._exchange, queue=self._queue, routing_key=self._queue
        )
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self._queue, self._callback)
        channel.start_consuming()
