import json
import os

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 300))

client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

PIZZAS_KEY = "pizzas:all"
PIZZA_KEY_TEMPLATE = "pizzas:{pizza_id}"
PEDIDOS_KEY = "pedidos:all"
PEDIDO_KEY_TEMPLATE = "pedidos:{pedido_id}"


def _safe_get(key):
    try:
        return client.get(key)
    except redis.RedisError:
        return None


def _safe_set(key, value):
    try:
        client.set(key, json.dumps(value), ex=REDIS_CACHE_TTL)
    except redis.RedisError:
        pass


def _safe_delete(*keys):
    try:
        client.delete(*keys)
    except redis.RedisError:
        pass


def _serialize_pizza(pizza):
    return {
        "id": pizza.id,
        "nome": pizza.nome,
        "descricao": pizza.descricao,
        "preco": pizza.preco
    }


def _serialize_pedido(pedido):
    return {
        "id": pedido.id,
        "cliente": pedido.cliente,
        "status": pedido.status
    }


def get_pizzas_cache():
    data = _safe_get(PIZZAS_KEY)
    if data is None:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def set_pizzas_cache(pizzas):
    value = [_serialize_pizza(pizza) for pizza in pizzas]
    _safe_set(PIZZAS_KEY, value)


def get_pizza_cache(pizza_id):
    key = PIZZA_KEY_TEMPLATE.format(pizza_id=pizza_id)
    data = _safe_get(key)
    if data is None:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def set_pizza_cache(pizza_id, pizza):
    key = PIZZA_KEY_TEMPLATE.format(pizza_id=pizza_id)
    _safe_set(key, _serialize_pizza(pizza))


def invalidate_pizzas_cache():
    _safe_delete(PIZZAS_KEY)


def get_pedidos_cache():
    data = _safe_get(PEDIDOS_KEY)
    if data is None:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def set_pedidos_cache(pedidos):
    value = [_serialize_pedido(pedido) for pedido in pedidos]
    _safe_set(PEDIDOS_KEY, value)


def get_pedido_cache(pedido_id):
    key = PEDIDO_KEY_TEMPLATE.format(pedido_id=pedido_id)
    data = _safe_get(key)
    if data is None:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def set_pedido_cache(pedido_id, pedido):
    key = PEDIDO_KEY_TEMPLATE.format(pedido_id=pedido_id)
    _safe_set(key, _serialize_pedido(pedido))


def invalidate_pedidos_cache():
    _safe_delete(PEDIDOS_KEY)


def invalidate_pedido_cache(pedido_id):
    key = PEDIDO_KEY_TEMPLATE.format(pedido_id=pedido_id)
    _safe_delete(key)
