from pydantic import BaseModel


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