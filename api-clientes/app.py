from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from pydantic import BaseModel
import time

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_CONFIG = {
    "host": "postgres-db",
    "database": "oficina_db",
    "user": "admin",
    "password": "123"
}

class Cliente(BaseModel):
    nome: str
    veiculo: str

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

@app.on_event("startup")
def startup_db():
    attempt = 0
    while attempt < 10:
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nome TEXT,
                    veiculo TEXT
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Conectado ao PostgreSQL!")
            break
        except Exception as e:
            attempt += 1
            print(f"Tentativa {attempt}: aguardando banco... {e}")
            time.sleep(3)

@app.post("/clientes", status_code=201)
def cadastrar(cliente: Cliente):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clientes (nome, veiculo) VALUES (%s, %s) RETURNING id",
        (cliente.nome, cliente.veiculo)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": new_id, "status": "Cliente cadastrado com sucesso!"}

@app.get("/clientes")
def listar():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "nome": r[1], "veiculo": r[2]} for r in rows]

@app.get("/clientes/{cliente_id}")
def buscar(cliente_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"id": row[0], "nome": row[1], "veiculo": row[2]}

@app.put("/clientes/{cliente_id}")
def atualizar(cliente_id: int, cliente: Cliente):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE clientes SET nome = %s, veiculo = %s WHERE id = %s",
        (cliente.nome, cliente.veiculo, cliente_id)
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if updated == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"status": "Cliente atualizado com sucesso!"}

@app.delete("/clientes/{cliente_id}")
def remover(cliente_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"status": "Cliente removido com sucesso!"}