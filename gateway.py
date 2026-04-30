from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gateway de Contas Online", description="API Gateway com HATEOAS")

#para o Angular conseguir acessar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Na vida real, colocaríamos a porta do Angular aqui
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# As 2 APIs
def api_interna_conta(id: int):
    # Simula a API 1: Dados conta corrente
    return {"id": id, "titular": "Lorrany", "saldo": 2500.0, "status_bloqueado": False}

def api_interna_credito(id: int):
    # Simula a API 2: Serviço de crédito
    return {"limite_pre_aprovado": 5000.0, "cartao_liberado": True}

# ---------------------------------------------------------
# O GATEWAY 
@app.get("/gateway/conta/{conta_id}")
def obter_resumo_conta(conta_id: int):
    
    # 1. O Gateway consome as duas APIs internas
    dados_conta = api_interna_conta(conta_id)
    dados_credito = api_interna_credito(conta_id)
    
    # 2. O Gateway monta o pacote para o Cliente e adiciona o HATEOAS (links)
    resposta = {
        "dados_principais": dados_conta,
        "dados_extras": dados_credito,
        "_links": {
            "self": f"/gateway/conta/{conta_id}",
            "extrato": f"/gateway/conta/{conta_id}/extrato"
        }
    }
    
    # 3. MÁGICA DO HATEOAS: O Gateway decide quais ações o Front-end pode fazer
    if not dados_conta["status_bloqueado"]:
        # Se a conta NÃO estiver bloqueada, manda o link para liberar transações
        resposta["_links"]["transferir"] = f"/gateway/conta/{conta_id}/transferir"
        resposta["_links"]["pagar_boleto"] = f"/gateway/conta/{conta_id}/pagar"
        
    return resposta