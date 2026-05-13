from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CLIENTES_URL = "http://api-clientes:8000"
PRODUTOS_URL = "http://api-produtos:8000"

pedidos_db = []
proximo_id = 1

@app.post("/pedidos/gerar", status_code=201)
def gerar_ordem(cliente_id: int, nome_produto: str):
    global proximo_id
    try:
        clientes = requests.get(f"{CLIENTES_URL}/clientes").json()
        cliente = next((c for c in clientes if c["id"] == cliente_id), None)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado na api-clientes")

        produto = requests.get(f"{PRODUTOS_URL}/produtos/{nome_produto}").json()
        if "detail" in produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado na api-produtos")

        pedido = {
            "id": proximo_id,
            "cliente_id": cliente_id,
            "cliente_nome": cliente["nome"],
            "veiculo": cliente["veiculo"],
            "produto": nome_produto,
            "preco": produto["preco"],
            "status": "aberto"
        }
        pedidos_db.append(pedido)
        proximo_id += 1
        return {"status": "Ordem de Serviço Criada", "pedido": pedido}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Falha na comunicação: {str(e)}")

@app.get("/pedidos")
def listar():
    return pedidos_db

@app.get("/pedidos/{pedido_id}")
def buscar(pedido_id: int):
    pedido = next((p for p in pedidos_db if p["id"] == pedido_id), None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@app.put("/pedidos/{pedido_id}")
def atualizar(pedido_id: int, status: str):
    pedido = next((p for p in pedidos_db if p["id"] == pedido_id), None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    pedido["status"] = status
    return {"status": "Pedido atualizado!", "pedido": pedido}

@app.delete("/pedidos/{pedido_id}")
def remover(pedido_id: int):
    global pedidos_db
    tamanho = len(pedidos_db)
    pedidos_db = [p for p in pedidos_db if p["id"] != pedido_id]
    if len(pedidos_db) == tamanho:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"status": "Pedido removido com sucesso!"}

@app.get("/resumo-oficina")
def resumo():
    c = requests.get(f"{CLIENTES_URL}/clientes").json()
    p = requests.get(f"{PRODUTOS_URL}/produtos").json()
    return {
        "total_clientes": len(c),
        "total_pecas_estoque": len(p),
        "total_pedidos": len(pedidos_db)
    }