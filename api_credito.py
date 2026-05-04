from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Microserviço de Crédito")

bd_credito = {
    1: {"limite": 5000.00},
    2: {"limite": 2000.00}
}

class CreditoCreate(BaseModel):
    id: int
    limite: float

@app.get("/credito/{conta_id}")
def buscar_limite(conta_id: int):
    if conta_id not in bd_credito:
        raise HTTPException(status_code=404, detail="Limite não encontrado")
    return bd_credito[conta_id]

@app.post("/credito", status_code=201)
def criar_limite(novo_credito: CreditoCreate):
    bd_credito[novo_credito.id] = {"limite": novo_credito.limite}
    return {"mensagem": "Limite salvo no Microserviço de Crédito!"}


@app.delete("/credito/{conta_id}")
def deletar_limite(conta_id: int):
    # O "if" garante que não vai dar erro se a pessoa não tiver limite
    if conta_id in bd_credito:
        del bd_credito[conta_id]
    return {"mensagem": "Limite apagado com sucesso!"}