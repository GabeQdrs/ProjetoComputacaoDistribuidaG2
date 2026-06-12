import pika
import json
import time

def callback(ch, method, properties, body):

    data = json.loads(body)

    order_id = data["order_id"]

    print(f"Processando pedido {order_id}")

    # status = PREPARING

    time.sleep(5)

    # status = READY

    print(f"Pedido {order_id} pronto")


connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost")
)

channel = connection.channel()

channel.queue_declare(queue="pizza_orders")

channel.basic_consume(
    queue="pizza_orders",
    on_message_callback=callback,
    auto_ack=True
)

print("Aguardando pedidos...")

channel.start_consuming()