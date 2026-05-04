from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Microserviço de Contas")

bd_contas = {
    1: {"id": 1, "titular": "Lorrany", "saldo": 2500.00, "status_bloqueado": False},
}

class ContaCreate(BaseModel):
    id: int
    titular: str
    saldo: float
    status_bloqueado: bool = False

class ContaUpdate(BaseModel):
    status_bloqueado: bool

@app.get("/conta/{conta_id}")
def buscar_conta(conta_id: int):
    if conta_id not in bd_contas:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return bd_contas[conta_id]

# Endpoint que altera o status para o HATEOAS reagir
@app.put("/conta/{conta_id}/bloquear")
def atualizar_status(conta_id: int, dados: ContaUpdate):
    if conta_id not in bd_contas:
         raise HTTPException(status_code=404, detail="Conta não encontrada")
    bd_contas[conta_id]["status_bloqueado"] = dados.status_bloqueado
    return {"mensagem": "Status atualizado"}

@app.post("/conta", status_code=201)
def criar_conta(nova_conta: ContaCreate):
    bd_contas[nova_conta.id] = nova_conta.dict()
    return {"mensagem": "Conta salva no Microserviço de Contas!"}

@app.delete("/conta/{conta_id}")
def deletar_conta(conta_id: int):
    if conta_id not in bd_contas:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    del bd_contas[conta_id]
    return {"mensagem": "Conta apagada com sucesso!"}