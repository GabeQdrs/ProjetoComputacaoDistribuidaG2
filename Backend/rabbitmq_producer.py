import json
import os

import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "pizza_orders")


def publish_order(pedido_id: int):
    message = json.dumps({"pedido_id": pedido_id})
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
