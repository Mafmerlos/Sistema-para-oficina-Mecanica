from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



client = MongoClient("mongodb://mongo-db:27017/")
db = client.oficina_pecas
collection = db.estoque

class Produto(BaseModel):
    nome: str
    preco: float
    quantidade: int

@app.get("/")
def read_root():
    return {"servico": "API de Produtos/Peças - MongoDB"}

@app.post("/produtos")
def cadastrar_produto(produto: Produto):
    res = collection.insert_one(produto.dict())
    return {"id": str(res.inserted_id), "status": "Produto cadastrado no MongoDB"}

@app.get("/produtos")
def listar_produtos():
    produtos = []
    for p in collection.find():
        p["_id"] = str(p["_id"]) 
        produtos.append(p)
    return produtos

@app.delete("/produtos/{nome}")
def remover_produto(nome: str):
    res = collection.delete_one({"nome": nome})
    return {"removidos": res.deleted_count}