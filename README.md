# Projeto Computacao Distribuida G2

Sistema simples de pizzaria online desenvolvido para a disciplina de Computacao Distribuida.

O projeto possui um backend em FastAPI, um frontend em HTML/CSS/JavaScript, banco SQLite, cache com Redis e fila de mensagens com RabbitMQ.

## Tecnologias utilizadas

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Redis
- RabbitMQ
- HTML, CSS e JavaScript
- Docker Compose

## Estrutura do projeto

```text
ProjetoComputacaoDistribuidaG2/
  Backend/
    main.py
    database.py
    models.py
    schemas.py
    redis_cache.py
    rabbitmq_producer.py
    rabbitmq_consumer.py
  Frotnend/
    index.html
    admin.html
    script.js
    style.css
  docker-compose.yml
requirements.txt
README.md
```

## Funcao de cada arquivo principal

### Backend

- `main.py`: arquivo principal da API. Define as rotas de pizzas e pedidos.
- `database.py`: configura a conexao com o banco SQLite.
- `models.py`: define as tabelas do banco usando SQLAlchemy.
- `schemas.py`: define os formatos dos dados recebidos pela API usando Pydantic.
- `redis_cache.py`: possui funcoes para salvar, buscar e remover dados do Redis.
- `rabbitmq_producer.py`: envia mensagens para a fila do RabbitMQ quando um pedido e criado.
- `rabbitmq_consumer.py`: consome mensagens da fila e simula o processamento de pedidos.

### Frontend

- `index.html`: tela principal do cliente, usada para visualizar pizzas e criar pedidos.
- `admin.html`: tela administrativa, usada para cadastrar, buscar, editar e excluir pizzas.
- `script.js`: script auxiliar do frontend.
- `style.css`: estilos da interface.

## Como executar o projeto

### 1. Instalar dependencias Python

Na raiz do projeto, execute:

```powershell
pip install -r requirements.txt
```

### 2. Subir Redis e RabbitMQ

Entre na pasta do projeto e execute:

```powershell
cd ProjetoComputacaoDistribuidaG2
docker compose up -d
```

Esse comando sobe:

- Redis na porta `6379`
- RabbitMQ na porta `5672`
- Painel do RabbitMQ na porta `15672`

### 3. Iniciar o backend

Em outro terminal:

```powershell
cd ProjetoComputacaoDistribuidaG2\Backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 4. Iniciar o frontend

Em outro terminal:

```powershell
cd ProjetoComputacaoDistribuidaG2\Frotnend
python -m http.server 8080
```

## Links de acesso

- Frontend cliente: http://127.0.0.1:8080
- Painel admin: http://127.0.0.1:8080/admin.html
- Backend/API: http://127.0.0.1:8000
- Swagger/FastAPI docs: http://127.0.0.1:8000/docs
- RabbitMQ: http://127.0.0.1:15672

Login padrao do RabbitMQ:

```text
usuario: guest
senha: guest
```

## Rotas principais da API

### Home

```text
GET /
```

Retorna uma mensagem simples confirmando que a API esta funcionando.

### Pizzas

```text
POST /pizzas
```

Cadastra uma nova pizza.

```text
GET /pizzas
```

Lista todas as pizzas cadastradas.

```text
GET /pizzas/{pizza_id}
```

Busca uma pizza pelo ID.

```text
PUT /pizzas/{pizza_id}
```

Atualiza uma pizza existente.

```text
DELETE /pizzas/{pizza_id}
```

Remove uma pizza.

### Pedidos

```text
POST /pedidos
```

Cria um novo pedido e envia o ID do pedido para a fila RabbitMQ.

```text
GET /pedidos
```

Lista os pedidos. Essa rota usa Redis para cachear a resposta por um curto periodo.

```text
GET /pedidos/{pedido_id}
```

Busca um pedido pelo ID.

```text
PUT /pedidos/{pedido_id}/status
```

Atualiza o status de um pedido.

## Fluxo da aplicacao

1. O usuario acessa o frontend.
2. O frontend faz requisicoes HTTP para o backend FastAPI.
3. O backend salva e consulta dados no SQLite usando SQLAlchemy.
4. A listagem de pedidos pode ser armazenada temporariamente no Redis.
5. Ao criar um pedido, o backend envia uma mensagem para o RabbitMQ.
6. O consumer pode processar mensagens da fila de pedidos.

## Observacoes

- O banco SQLite e criado automaticamente como `pizzaria.db`.
- O Redis e usado como cache para a listagem de pedidos.
- O RabbitMQ e usado para simular processamento assincrono de pedidos.
- A documentacao interativa da API fica disponivel no Swagger em `/docs`.
