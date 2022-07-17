import json

import pika

from config import settings
from saga.saga import (
    RabbitMQSagaExecutionController,
    Saga,
    SagaStateRepository,
    SagaStep,
)


class SagaStateRepositoryMock(SagaStateRepository):
    def __init__(self, file_name: str):
        self._file_name = file_name
        self._state = {}

    def save(self, data):
        with open(self._file_name, "a") as f:
            f.write(json.dumps(data) + "\n")

    def action_started(self, saga_id: str, step_name: str):
        data = {
            "status": "running",
            "step_status": "action_started",
            "saga_id": saga_id,
            "step_name": step_name,
        }
        self.save(data)

    def action_succeeded(self, saga_id: str, step_name: str):
        data = {
            "status": "running",
            "step_status": "action_succeeded",
            "saga_id": saga_id,
            "step_name": step_name,
        }
        self.save(data)

    def action_failed(self, saga_id: str, step_name: str, error_type: str, error: str):
        data = {
            "status": "running",
            "step_status": "action_failed",
            "saga_id": saga_id,
            "step_name": step_name,
            "error_type": error_type,
            "error": error,
        }
        self.save(data)

    def compensation_started(self, saga_id: str, step_name: str):
        data = {
            "status": "compensation",
            "step_status": "compensation_started",
            "saga_id": saga_id,
            "step_name": step_name,
        }
        self.save(data)

    def compensation_succeeded(self, saga_id: str, step_name: str):
        data = {
            "status": "compensation",
            "step_status": "compensation_succeeded",
            "saga_id": saga_id,
            "step_name": step_name,
        }
        self.save(data)

    def compensation_failed(
        self, saga_id: str, step_name: str, error_type: str, error: str
    ):
        data = {
            "status": "compensation",
            "step_status": "compensation_failed",
            "saga_id": saga_id,
            "step_name": step_name,
            "error_type": error_type,
            "error": error,
        }
        self.save(data)

    def saga_completed(self, saga_id: str):
        data = {"saga_id": saga_id, "status": "completed"}
        self.save(data)

    def saga_failed(self, saga_id: str, step_name: str, error_type: str, error: str):
        data = {
            "status": "failed",
            "saga_id": saga_id,
            "step_name": step_name,
            "error_type": error_type,
            "error": error,
        }
        self.save(data)

    def saga_compensate_failed(
        self, saga_id: str, step_name: str, error_type: str, error: str
    ):
        data = {
            "status": "compensation_failed",
            "saga_id": saga_id,
            "step_name": step_name,
            "error_type": error_type,
            "error": error,
        }
        self.save(data)


def error_func(x):
    raise Exception(f"ERROR + {x}")


def rollback_error(x):
    raise Exception(f"ROLLBACK_ERROR {x}")

def func_1(x):
    print(f"func_1 - Payload={x}")
    return x


def main():
    log_file = "log.txt"
    saga_state_repository = SagaStateRepositoryMock(log_file)

    rabbitmq_connection = pika.BlockingConnection(
        pika.URLParameters(settings.saga_amqp_uri)
    )
    rabbitmq_sec = RabbitMQSagaExecutionController(
        saga_state_repository=saga_state_repository,
        rabbitmq_connection=rabbitmq_connection,
        exchange=settings.saga_exchange,
        queue=settings.saga_queue,
    )
    saga = Saga(name="saga")
    step1 = SagaStep(
        name="step1",
        action=func_1,
        compensation=lambda x: print(f"step1 - Compensation Payload={x}"),
    )
    step2 = SagaStep(
        name="step2",
        action=lambda x: print(f"step2 - Payload={x}"),
        compensation=lambda x: print(f"step2 - Compensation Payload={x}"),
    )
    step3 = SagaStep(
        name="step3",
        action=lambda x: print(f"step3 - Payload={x}"),
        compensation=lambda x: print(f"step3 - Compensation Payload={x}"),
    )

    saga.add_step(step1)
    saga.add_step(step2)
    saga.add_step(step3)

    rabbitmq_sec.add_saga(saga)
    rabbitmq_sec.run()


main()
