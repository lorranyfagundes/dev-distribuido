import asyncio
import websockets
import json
from zeep import Client

# 🌐 Configuração do Servidor Java SOAP
JAVA_SOAP_URL = "http://localhost:8085/quiz?wsdl" 
# Cria o "Cliente" que vai traduzir o WSDL
cliente_soap = Client(wsdl=JAVA_SOAP_URL)


# 🏨 ESTADO GLOBAL DO JOGO
JOGADORES_CONECTADOS = {}
DESAFIO_ATUAL = None
LINHAS_PARA_VENCER = 5

async def broadcast(mensagem_dict):
    if JOGADORES_CONECTADOS:
        payload = json.dumps(mensagem_dict)
        await asyncio.gather(*[ws.send(payload) for ws in JOGADORES_CONECTADOS.keys()])

async def transmitir_estado_do_quarto():
    lista_jogadores = [
        {"nickname": info["nickname"], "linha": info["linha"]}
        for info in JOGADORES_CONECTADOS.values()
        if info["nickname"] is not None
    ]
    await broadcast({
        "tipo": "atualizacao_sala",
        "jogadores": lista_jogadores
    })

# 🎲 NOVA FUNÇÃO: Sorteia e transmite a pergunta para TODO MUNDO ao mesmo tempo
async def sortear_e_transmitir_desafio():
    global DESAFIO_ATUAL
    try:
        desafio = buscar_desafio_no_java() 
        DESAFIO_ATUAL = {
            "tipo": "novo_desafio",
            "id": desafio["id"],
            "categoria": desafio["categoria"],
            "comando": desafio["comando"],
            "dica": desafio["dica"]
        }
        await broadcast(DESAFIO_ATUAL)
        print("📝 Novo desafio enviado para todos os jogadores!")
    except Exception as e:
        print(f"❌ Erro ao buscar desafio no Java SOAP: {e}")

def buscar_desafio_no_java():
    # 🌟 AQUI ESTÁ A MÁGICA: O Python chama o método obterDesafioAleatorio() do Java!
    resposta_java = cliente_soap.service.obterDesafioAleatorio()
    
    # Pegamos o objeto Java e transformamos em Dicionário Python
    return {
        "id": resposta_java.id,
        "categoria": resposta_java.categoria,
        "comando": resposta_java.comando,
        "dica": resposta_java.dica
    }

def validar_chute_no_java(id_desafio, chute):
    # 🌟 AQUI A MÁGICA 2: O Python envia o chute e o ID da rodada pro Java julgar
    resultado_java = cliente_soap.service.validarChute(rodadaId=id_desafio, chute=chute)
    
    # O Java retorna um objeto 'ResultadoChute' que tem o boolean 'acertou'
    return resultado_java.acertou

# 🎮 Gerenciador de conexões e jogadas
async def gerenciar_jogo(websocket):
    global DESAFIO_ATUAL
    JOGADORES_CONECTADOS[websocket] = {"nickname": None, "linha": 0}
    print("✨ Alguém entrou no link do hotel...")

    try:
        async for mensagem_crua in websocket:
            dados = json.loads(mensagem_crua)
            acao = dados.get("acao")

            if acao == "entrar":
                nick = dados.get("nickname", "Habbo_Anônimo")
                JOGADORES_CONECTADOS[websocket]["nickname"] = nick
                JOGADORES_CONECTADOS[websocket]["linha"] = 0
                
                await broadcast({
                    "tipo": "resultado_chute",
                    "acertou": True,
                    "mensagem": f"🌟 {nick} acabou de entrar no Steven Hotel!"
                })
                await transmitir_estado_do_quarto()
                
                # A MÁGICA DO AUTO-START ACONTECE AQUI:
                if DESAFIO_ATUAL:
                    # Se já tem um desafio rolando na tela dos outros, apenas mostra para o novato
                    await websocket.send(json.dumps(DESAFIO_ATUAL))
                else:
                    # Se NÃO tem desafio (quarto estava vazio ou jogo acabou de resetar), 
                    # o Python vira o "Mestre do Jogo" e puxa a alavanca sozinho!
                    await broadcast({
                        "tipo": "resultado_chute",
                        "acertou": True,
                        "mensagem": f"🚦 Mestre do Jogo: Preparando o desafio em 3 segundos..."
                    })
                    await asyncio.sleep(3) # Dá 3 segundinhos de suspense
                    
                    if not DESAFIO_ATUAL: # Garante que outro evento não sorteou nesse meio tempo
                        await sortear_e_transmitir_desafio()

            # 2️⃣ BOTÃO MANUAL (Roda apenas para iniciar a primeira partida)
            elif acao == "pedir_desafio":
                await sortear_e_transmitir_desafio()

            # 3️⃣ A DISPUTA DO CHUTE (AQUI ACONTECE A MÁGICA)
            elif acao == "enviar_chute":
                if not DESAFIO_ATUAL:
                    continue

                nick_autor = JOGADORES_CONECTADOS[websocket]["nickname"]
                chute = dados.get("chute", "")
                acertou = validar_chute_no_java(dados.get("id"), chute)

                if acertou:
                    # Avança o jogador veloz de linha
                    JOGADORES_CONECTADOS[websocket]["linha"] += 1
                    linha_atual = JOGADORES_CONECTADOS[websocket]["linha"]
                    
                    # 1. Avisa todo mundo quem foi o mito da rodada
                    await broadcast({
                        "tipo": "resultado_chute",
                        "acertou": True,
                        "mensagem": f"🎉 {nick_autor} FOI MAIS RÁPIDO! Acertou e avançou para a linha {linha_atual}!"
                    })
                    await transmitir_estado_do_quarto()

                    # 2. Verifica se ele ganhou o jogo inteiro
                    if linha_atual >= LINHAS_PARA_VENCER:
                        await broadcast({
                            "tipo": "fim_jogo",
                            "vencedor": nick_autor,
                            "mensagem": f"🏆 {nick_autor} CHEGOU À ÚLTIMA LINHA E GANHOU O JOGO!"
                        })
                        for ws in JOGADORES_CONECTADOS: JOGADORES_CONECTADOS[ws]["linha"] = 0
                        DESAFIO_ATUAL = None
                        await transmitir_estado_do_quarto()
                    else:
                        # 3. SE NINGUÉM GANHOU AINDA: Reseta a pergunta e puxa uma nova AUTOMATICAMENTE!
                        DESAFIO_ATUAL = None 
                        print(f"🔄 {nick_autor} acertou. Sorteando o próximo desafio em 2 segundos...")
                        await asyncio.sleep(2) # Delay pro pessoal conseguir ler quem ganhou o ponto
                        await sortear_e_transmitir_desafio()
                else:
                    # Se errou, só joga a mensagem no chat pra todo mundo ver o mico, mas não mexe na pergunta
                    await broadcast({
                        "tipo": "resultado_chute",
                        "acertou": False,
                        "mensagem": f"💬 {nick_autor} chutou '{chute}' e ERROU!"
                    })

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        info_saindo = JOGADORES_CONECTADOS.pop(websocket, None)
        if info_saindo and info_saindo["nickname"]:
            await broadcast({
                "tipo": "resultado_chute",
                "acertou": False,
                "mensagem": f"👣 {info_saindo['nickname']} saiu do quarto."
            })
            await transmitir_estado_do_quarto()

async def main():
    print("🏨 Servidor Steven Habbo Hotel Arena na porta 8086...")
    async with websockets.serve(gerenciar_jogo, "0.0.0.0", 8086):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())