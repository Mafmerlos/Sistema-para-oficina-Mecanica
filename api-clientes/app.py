from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel
import os
import time

app = FastAPI()

DB_CONFIG = {
    "host": "postgres-db",
    "database": "oficina_db",
    "user": "admin",
    "password": "123"
}

class Cliente(BaseModel):
    nome: str
    veiculo: str

@app.on_event("startup")
def startup_db():
    attempt = 0
    while attempt < 10:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS clientes (id SERIAL PRIMARY KEY, nome TEXT, veiculo TEXT);")
            conn.commit()
            cur.close()
            conn.close()
            print("Conectado ao PostgreSQL com sucesso!")
            break
        except Exception as e:
            attempt += 1
            print(f"Tentativa {attempt}: Banco ainda não pronto... aguardando 3s.")
            time.sleep(3)

@app.post("/clientes")
def cadastrar(cliente: Cliente):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome, veiculo) VALUES (%s, %s)", (cliente.nome, cliente.veiculo))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "Cliente cadastrado com sucesso!"}

@app.get("/clientes")
def listar():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "nome": r[1], "veiculo": r[2]} for r in rows]