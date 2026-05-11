from fastapi import FastAPI
import requests
import os

app = FastAPI()

CLIENTES_URL = "http://api-clientes:8000/clientes"
PRODUTOS_URL = "http://api-produtos:8000/produtos"

@app.get("/")
def home():
    return {"servico": "Gerenciador de Pedidos - Oficina"}

@app.post("/pedidos/gerar")
def gerar_ordem_servico(cliente_id: int, nome_produto: str):
    try:
        clientes = requests.get(CLIENTES_URL).json()
        cliente_valido = any(c['id'] == cliente_id for c in clientes)
        
        produtos = requests.get(PRODUTOS_URL).json()
        produto_valido = any(p['nome'] == nome_produto for p in produtos)

        if cliente_valido and produto_valido:
            return {
                "status": "Ordem de Serviço Criada",
                "detalhes": f"Cliente {cliente_id} solicitou peça: {nome_produto}"
            }
        return {"erro": "Cliente ou Produto não encontrado nas outras APIs"}
        
    except Exception as e:
        return {"erro": f"Falha na comunicação entre containers: {str(e)}"}

@app.get("/resumo-oficina")
def resumo():
    c = requests.get(CLIENTES_URL).json()
    p = requests.get(PRODUTOS_URL).json()
    return {
        "total_clientes": len(c),
        "total_pecas_estoque": len(p)
    }