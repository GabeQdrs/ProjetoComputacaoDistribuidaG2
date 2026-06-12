import pika
import json

def enviar_pedido(order_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )

    channel = connection.channel()

    channel.queue_declare(queue="pizza_orders")

    channel.basic_publish(
        exchange="",
        routing_key="pizza_orders",
        body=json.dumps({
            "order_id": order_id
        })
    )

    connection.close()