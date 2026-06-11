import asyncio
import json
import logging
import websockets
from zeep import Client
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
CONEXOES_ATIVAS = set()

WSDL_URL = "http://localhost:8085/quiz?wsdl"
try:
    cliente_soap = Client(wsdl=WSDL_URL)
    logging.info("🔗 Conectado ao Servidor SOAP (Java)!")
except Exception as e:
    logging.error(f"💥 Erro ao conectar no SOAP: {e}")
    sys.exit(1)

async def realizar_broadcast(mensagem_dict):
    if CONEXOES_ATIVAS:
        mensagem_json = json.dumps(mensagem_dict)
        await asyncio.gather(*[cliente.send(mensagem_json) for cliente in CONEXOES_ATIVAS])

async def handler_cliente(websocket):
    logging.info(f"🔌 Novo painel Angular conectado: {websocket.remote_address}")
    CONEXOES_ATIVAS.add(websocket)
    try:
        async for mensagem_bruta in websocket:
            dados = json.loads(mensagem_bruta)
            acao = dados.get("acao")
            
            if acao == "pedir_desafio":
                desafio = cliente_soap.service.obterDesafioAleatorio()
                await websocket.send(json.dumps({
                    "tipo": "novo_desafio", "id": desafio.id, "comando": desafio.comando,
                    "categoria": desafio.categoria, "dica": desafio.dica
                }))
                
            elif acao == "enviar_chute":
                resultado = cliente_soap.service.validarChute(rodadaId=dados.get("id"), chute=dados.get("chute"))
                await realizar_broadcast({
                    "tipo": "resultado_chute", "chute": dados.get("chute"),
                    "acertou": resultado.acertou, "mensagem": resultado.mensagem, "pontos": resultado.pontos
                })
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONEXOES_ATIVAS.remove(websocket)
        logging.info(f"❌ Angular desconectado: {websocket.remote_address}")

async def main():
    async with websockets.serve(handler_cliente, "localhost", 8086):
        logging.info("🚀 MIDDLEWARE (SOAP + WS) ATIVO EM ws://localhost:8086")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())