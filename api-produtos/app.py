from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = MongoClient("mongodb://mongo-db:27017/")
db = client.oficina_pecas
collection = db.estoque

class Produto(BaseModel):
    nome: str
    preco: float
    quantidade: int

class ProdutoUpdate(BaseModel):
    preco: float
    quantidade: int

@app.post("/produtos", status_code=201)
def cadastrar(produto: Produto):
    res = collection.insert_one(produto.dict())
    return {"id": str(res.inserted_id), "status": "Produto cadastrado no MongoDB"}

@app.get("/produtos")
def listar():
    produtos = []
    for p in collection.find():
        p["_id"] = str(p["_id"])
        produtos.append(p)
    return produtos

@app.get("/produtos/{nome}")
def buscar(nome: str):
    p = collection.find_one({"nome": nome})
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    p["_id"] = str(p["_id"])
    return p

@app.put("/produtos/{nome}")
def atualizar(nome: str, dados: ProdutoUpdate):
    res = collection.update_one(
        {"nome": nome},
        {"$set": {"preco": dados.preco, "quantidade": dados.quantidade}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"status": "Produto atualizado com sucesso!"}

@app.delete("/produtos/{nome}")
def remover(nome: str):
    res = collection.delete_one({"nome": nome})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"status": "Produto removido com sucesso!"}