const baseUrl = "http://127.0.0.1:8000";

const pizzaForm = document.getElementById("pizza-form");
const pedidoForm = document.getElementById("pedido-form");
const pizzaList = document.getElementById("pizza-list");
const pedidoList = document.getElementById("pedido-list");

async function fetchPizzas() {
    try {
        const response = await fetch(`${baseUrl}/pizzas`);
        const pizzas = await response.json();
        renderPizzas(pizzas);
    } catch (error) {
        pizzaList.innerHTML = `<p class="message">Erro ao carregar pizzas. Verifique se o backend está rodando.</p>`;
    }
}

async function fetchPedidos() {
    try {
        const response = await fetch(`${baseUrl}/pedidos`);
        const pedidos = await response.json();
        renderPedidos(pedidos);
    } catch (error) {
        pedidoList.innerHTML = `<p class="message">Erro ao carregar pedidos. Verifique se o backend está rodando.</p>`;
    }
}

function renderPizzas(pizzas) {
    if (!pizzas.length) {
        pizzaList.innerHTML = `<p class="message">Nenhuma pizza encontrada.</p>`;
        return;
    }

    pizzaList.innerHTML = `
        <table>
            <thead>
                <tr><th>ID</th><th>Nome</th><th>Descrição</th><th>Preço</th></tr>
            </thead>
            <tbody>
                ${pizzas
                    .map(
                        pizza => `
                    <tr>
                        <td>${pizza.id}</td>
                        <td>${pizza.nome}</td>
                        <td>${pizza.descricao}</td>
                        <td>R$ ${pizza.preco.toFixed(2)}</td>
                    </tr>`
                    )
                    .join("")}
            </tbody>
        </table>
    `;
}

function renderPedidos(pedidos) {
    if (!pedidos.length) {
        pedidoList.innerHTML = `<p class="message">Nenhum pedido registrado.</p>`;
        return;
    }

    pedidoList.innerHTML = `
        <table>
            <thead>
                <tr><th>ID</th><th>Cliente</th><th>Status</th><th>Ação</th></tr>
            </thead>
            <tbody>
                ${pedidos
                    .map(
                        pedido => `
                    <tr>
                        <td>${pedido.id}</td>
                        <td>${pedido.cliente}</td>
                        <td>${pedido.status}</td>
                        <td><button class="status-button" onclick="updateStatus(${pedido.id})">Atualizar status</button></td>
                    </tr>`
                    )
                    .join("")}
            </tbody>
        </table>
    `;
}

pizzaForm.addEventListener("submit", async event => {
    event.preventDefault();

    const nome = document.getElementById("pizza-nome").value.trim();
    const descricao = document.getElementById("pizza-descricao").value.trim();
    const preco = parseFloat(document.getElementById("pizza-preco").value);

    if (!nome || !descricao || Number.isNaN(preco)) return;

    try {
        await fetch(`${baseUrl}/pizzas`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ nome, descricao, preco })
        });

        pizzaForm.reset();
        fetchPizzas();
    } catch (error) {
        alert("Erro ao cadastrar pizza. Verifique o backend.");
    }
});

pedidoForm.addEventListener("submit", async event => {
    event.preventDefault();

    const cliente = document.getElementById("pedido-cliente").value.trim();
    if (!cliente) return;

    try {
        await fetch(`${baseUrl}/pedidos`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ cliente })
        });

        pedidoForm.reset();
        fetchPedidos();
    } catch (error) {
        alert("Erro ao criar pedido. Verifique o backend.");
    }
});

window.updateStatus = async function (pedidoId) {
    const novoStatus = prompt("Novo status do pedido:", "Em preparo");
    if (!novoStatus) return;

    try {
        const url = new URL(`${baseUrl}/pedidos/${pedidoId}/status`);
        url.searchParams.set("status", novoStatus);

        await fetch(url.toString(), {
            method: "PUT"
        });

        fetchPedidos();
    } catch (error) {
        alert("Erro ao atualizar status. Verifique o backend.");
    }
};

fetchPizzas();
fetchPedidos();
