from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas

from database import engine, get_db, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"mensagem": "API da Pizzaria Online"}


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
        return {"erro": "Pizza não encontrada"}

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
        return {"erro": "Pizza não encontrada"}

    db.delete(pizza_db)
    db.commit()

    return {"mensagem": "Pizza removida"}