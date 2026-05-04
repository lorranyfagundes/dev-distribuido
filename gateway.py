from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="API Gateway com HATEOAS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

URL_API_CONTA = "http://127.0.0.1:8001"
URL_API_CREDITO = "http://127.0.0.1:8002"

class NovaContaGateway(BaseModel):
    id: int
    titular: str
    saldo: float
    limite: float

@app.post("/gateway/conta", status_code=201)
async def gateway_criar_conta(dados: NovaContaGateway):
    async with httpx.AsyncClient() as client:
        # Manda criar na porta 8001
        await client.post(f"{URL_API_CONTA}/conta", json={
            "id": dados.id,
            "titular": dados.titular,
            "saldo": dados.saldo,
            "status_bloqueado": False
        })
        # Manda criar na porta 8002
        await client.post(f"{URL_API_CREDITO}/credito", json={
            "id": dados.id,
            "limite": dados.limite
        })
    return {"mensagem": f"Sucesso! A conta de {dados.titular} foi criada em todos os microserviços."}

@app.get("/gateway/conta/{conta_id}")
async def gateway_buscar_conta(conta_id: int):
    async with httpx.AsyncClient() as client:
        resposta_conta = await client.get(f"{URL_API_CONTA}/conta/{conta_id}")
        if resposta_conta.status_code != 200:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        dados_conta = resposta_conta.json()

        resposta_credito = await client.get(f"{URL_API_CREDITO}/credito/{conta_id}")
        dados_credito = resposta_credito.json() if resposta_credito.status_code == 200 else {"limite": 0}

    conta_consolidada = {
        "id": dados_conta["id"],
        "titular": dados_conta["titular"],
        "saldo": dados_conta["saldo"],
        "limite": dados_credito["limite"],
        "status_bloqueado": dados_conta["status_bloqueado"]
    }

    # ----------------------------------------------------
    # HATEOAS 
    # ----------------------------------------------------
    links = {
        "self": f"/gateway/conta/{conta_id}",
        "extrato": f"/gateway/conta/{conta_id}/extrato"
    }
    
    # Se a conta NÃO estiver bloqueada, ele injeta os botões de ação!
    if not conta_consolidada["status_bloqueado"]:
        links["transferir"] = f"/gateway/conta/{conta_id}/transferir"
        links["pagar_boleto"] = f"/gateway/conta/{conta_id}/pagar"

    conta_consolidada["_links"] = links
    return conta_consolidada # <--- AGORA O RETURN ESTÁ NO LUGAR CERTO!

@app.delete("/gateway/conta/{conta_id}")
async def gateway_deletar_conta(conta_id: int):
    async with httpx.AsyncClient() as client:
        # Manda o comando de exclusão para os dois microserviços
        await client.delete(f"{URL_API_CONTA}/conta/{conta_id}")
        await client.delete(f"{URL_API_CREDITO}/credito/{conta_id}")
        
    return {"mensagem": f"A conta {conta_id} foi excluída de todo o sistema."}