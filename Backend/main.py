from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas
import redis_cache
import rabbitmq_producer

from database import engine, Base, get_db

app = FastAPI()

Base.metadata.create_all(bind=engine)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "mensagem": "API da Pizzaria Online"
    }


# ==================================================
# PIZZAS
# ==================================================

@app.post("/pizzas")
def criar_pizza(
    pizza: schemas.PizzaCreate,
    db: Session = Depends(get_db)
):
    nova_pizza = models.Pizza(
        nome=pizza.nome,
        descricao=pizza.descricao,
        preco=pizza.preco
    )

    db.add(nova_pizza)
    db.commit()
    db.refresh(nova_pizza)

    redis_cache.invalidate_pizzas_cache()

    return nova_pizza


@app.get("/pizzas")
def listar_pizzas(
    db: Session = Depends(get_db)
):
    cached_pizzas = redis_cache.get_pizzas_cache()
    if cached_pizzas is not None:
        return cached_pizzas

    pizzas = db.query(models.Pizza).all()
    redis_cache.set_pizzas_cache(pizzas)
    return pizzas


@app.get("/pizzas/{pizza_id}")
def buscar_pizza(
    pizza_id: int,
    db: Session = Depends(get_db)
):
    cached_pizza = redis_cache.get_pizza_cache(pizza_id)
    if cached_pizza is not None:
        return cached_pizza

    pizza_db = db.query(models.Pizza).filter(
        models.Pizza.id == pizza_id
    ).first()
    if pizza_db is not None:
        redis_cache.set_pizza_cache(pizza_id, pizza_db)

    return pizza_db


@app.put("/pizzas/{pizza_id}")
def atualizar_pizza(
    pizza_id: int,
    pizza: schemas.PizzaCreate,
    db: Session = Depends(get_db)
):
    pizza_db = db.query(models.Pizza).filter(
        models.Pizza.id == pizza_id
    ).first()

    if not pizza_db:
        return {
            "erro": "Pizza não encontrada"
        }

    pizza_db.nome = pizza.nome
    pizza_db.descricao = pizza.descricao
    pizza_db.preco = pizza.preco

    db.commit()
    db.refresh(pizza_db)

    redis_cache.invalidate_pizzas_cache()

    return pizza_db


@app.delete("/pizzas/{pizza_id}")
def deletar_pizza(
    pizza_id: int,
    db: Session = Depends(get_db)
):
    pizza_db = db.query(models.Pizza).filter(
        models.Pizza.id == pizza_id
    ).first()

    if not pizza_db:
        return {
            "erro": "Pizza não encontrada"
        }

    db.delete(pizza_db)
    db.commit()

    redis_cache.invalidate_pizzas_cache()

    return {
        "mensagem": "Pizza removida"
    }


# ==================================================
# PEDIDOS
# ==================================================

@app.post("/pedidos")
def criar_pedido(
    pedido: schemas.PedidoCreate,
    db: Session = Depends(get_db)
):
    novo_pedido = models.Pedido(
        cliente=pedido.cliente,
        status="PENDING"
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    redis_cache.invalidate_pedidos_cache()
    rabbitmq_producer.publish_order(novo_pedido.id)

    return novo_pedido


@app.get("/pedidos")
def listar_pedidos(
    db: Session = Depends(get_db)
):
    cached_pedidos = redis_cache.get_pedidos_cache()
    if cached_pedidos is not None:
        return cached_pedidos

    pedidos = db.query(models.Pedido).all()
    redis_cache.set_pedidos_cache(pedidos)
    return pedidos


@app.get("/pedidos/{pedido_id}")
def buscar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    cached_pedido = redis_cache.get_pedido_cache(pedido_id)
    if cached_pedido is not None:
        return cached_pedido

    pedido_db = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()
    if pedido_db is not None:
        redis_cache.set_pedido_cache(pedido_id, pedido_db)

    return pedido_db


@app.put("/pedidos/{pedido_id}/status")
def atualizar_status(
    pedido_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()

    if not pedido:
        return {
            "erro": "Pedido não encontrado"
        }

    pedido.status = status

    db.commit()
    db.refresh(pedido)

    redis_cache.invalidate_pedidos_cache()
    redis_cache.invalidate_pedido_cache(pedido_id)

    return pedido