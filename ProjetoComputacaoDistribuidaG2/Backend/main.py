from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from redis_cache import (
    get_cache,
    set_cache,
    delete_cache
)
from rabbitmq_producer import enviar_pedido

import models
import schemas

from database import engine, Base, get_db

app = FastAPI()

# Enable CORS for development (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    return nova_pizza


@app.get("/pizzas")
def listar_pizzas(
    db: Session = Depends(get_db)
):
    return db.query(models.Pizza).all()


@app.get("/pizzas/{pizza_id}")
def buscar_pizza(
    pizza_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Pizza).filter(
        models.Pizza.id == pizza_id
    ).first()


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
        cliente=pedido.cliente
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    enviar_pedido(novo_pedido.id)

    delete_cache("pedidos")

    return novo_pedido


@app.get("/pedidos")
def listar_pedidos(
    db: Session = Depends(get_db)
):

    cache = get_cache("pedidos")

    if cache:
        print("Retornando do Redis")
        return cache

    print("Retornando do Banco")

    pedidos = db.query(models.Pedido).all()

    resultado = []

    for pedido in pedidos:
        resultado.append({
            "id": pedido.id,
            "cliente": pedido.cliente,
            "status": pedido.status
        })

    set_cache("pedidos", resultado)

    return resultado


@app.get("/pedidos/{pedido_id}")
def buscar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()


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

    delete_cache("pedidos")

    return pedido