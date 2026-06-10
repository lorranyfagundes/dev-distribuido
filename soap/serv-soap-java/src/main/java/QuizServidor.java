import jakarta.jws.WebMethod;
import jakarta.jws.WebParam;
import jakarta.jws.WebService;
import jakarta.xml.ws.Endpoint;
//mvn compile exec:java

@WebService(targetNamespace = "http://stevenhotel.quiz.com/")
public class QuizServidor {

    // Simulação do nosso banco de dados de rodadas (Perguntas e Respostas)
    private final String[][] rodadas = {
        {"Comida com a letra Q", "queijo"},
        {"Animal com a letra L", "leao"},
        {"Objeto com a letra C", "caneta"},
        {"Cor com a letra A", "azul"}
    };

    @WebMethod
    public String obterPergunta(@WebParam(name = "rodadaId") int id) {
        // REQUISITO: Tratamento de erro básico / Exceção simulada
        if (id < 0 || id >= rodadas.length) {
            // No SOAP, disparar uma RuntimeException gera automaticamente um "SOAP Fault"
            throw new IllegalArgumentException("Erro: Rodada ID " + id + " nao existe no Steven Hotel!");
        }
        
        // Retorna apenas o texto da pergunta para o jogo
        return rodadas[id][0];
    }

    @WebMethod
    public boolean validarResposta(@WebParam(name = "rodadaId") int id, @WebParam(name = "chute") String chute) {
        if (id < 0 || id >= rodadas.length) {
            throw new IllegalArgumentException("Erro: Rodada invalida para validacao.");
        }

        // Pega a resposta correta e limpa espaços e letras maiúsculas
        String respostaCorreta = rodadas[id][1].trim().toLowerCase();
        String chuteUsuario = chute.trim().toLowerCase();

        // Retorna true se o jogador acertou o chute rápido!
        return respostaCorreta.equals(chuteUsuario);
    }

    public static void main(String[] args) {
        String url = "http://localhost:8085/quiz";
        
        // REQUISITO: Publicação local do endpoint
        Endpoint.publish(url, new QuizServidor());
        
        System.out.println("===============================================");
        System.out.println("✨ SERVIDOR SOAP DO STEVEN HOTEL ATIVO! ✨");
        System.out.println("Contrato WSDL disponivel em: " + url + "?wsdl");
        System.out.println("===============================================");
    }
}