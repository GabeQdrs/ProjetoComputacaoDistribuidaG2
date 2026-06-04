import json
import os
import sys
import time

import pika

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_DIR, "Backend"))

from database import SessionLocal
from models import Pedido
from redis_cache import invalidate_pedidos_cache, invalidate_pedido_cache

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "pizza_orders")


def process_pedido(pedido_id):
    session = SessionLocal()
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        session.close()
        return

    pedido.status = "PREPARING"
    session.commit()
    invalidate_pedidos_cache()
    invalidate_pedido_cache(pedido_id)

    time.sleep(3)

    pedido.status = "READY"
    session.commit()
    invalidate_pedidos_cache()
    invalidate_pedido_cache(pedido_id)
    session.close()


def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        pedido_id = payload.get("pedido_id")
    except (json.JSONDecodeError, TypeError):
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    if pedido_id is None:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    process_pedido(pedido_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

    print("Worker aguardando mensagens na fila pizza_orders...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
