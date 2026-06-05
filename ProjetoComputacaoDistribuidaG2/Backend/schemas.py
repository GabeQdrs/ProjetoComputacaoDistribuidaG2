from pydantic import BaseModel


# ---------- PIZZAS ----------

class PizzaCreate(BaseModel):
    nome: str
    descricao: str
    preco: float


class PizzaResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float

    class Config:
        from_attributes = True


# ---------- PEDIDOS ----------

class PedidoCreate(BaseModel):
    cliente: str


class PedidoResponse(BaseModel):
    id: int
    cliente: str
    status: str

    class Config:
        from_attributes = True