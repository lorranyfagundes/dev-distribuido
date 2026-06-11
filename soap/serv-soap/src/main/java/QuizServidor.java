import jakarta.jws.WebMethod;
import jakarta.jws.WebParam;
import jakarta.jws.WebService;
import jakarta.xml.ws.Endpoint;
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.util.concurrent.Executors;
import java.util.Random;

class Desafio {
    public int id;
    public String comando;    
    public String categoria;  
    public String dica;       

    public Desafio() {} 

    public Desafio(int id, String comando, String categoria, String dica) {
        this.id = id;
        this.comando = comando;
        this.categoria = categoria;
        this.dica = dica;
    }
}

class ResultadoChute {
    public boolean acertou;
    public String mensagem;   
    public int pontos;

    public ResultadoChute() {} 

    public ResultadoChute(boolean acertou, String mensagem, int pontos) {
        this.acertou = acertou;
        this.mensagem = mensagem; // Atributo mapeado para o XML
        this.pontos = pontos;
    }
}

@WebService(targetNamespace = "http://stevenhotel.quiz.com/")
public class QuizServidor {

    // 1. BANCO DE DADOS AMPLIADO! 🚀
    private final String[][] bancoDados = {
        {"Comida com a letra Q", "queijo", "Alimentos", "Ametista comeria isso com saco plastico e tudo!"},
        {"Animal com a letra L", "leao", "Zoologia", "Eh rosa, fofinho e guarda coisas na juba."},
        {"Objeto com a letra C", "caneta", "Escritorio", "A Perola usa para organizar seus relatorios."},
        {"Fusao com a letra G", "garnet", "Steven Universo", "Feita de a-m-o-r, amor."},
        {"Planeta com a letra M", "marte", "Astronomia", "O planeta vermelho, mas nao eh a Terra Natal."},
        {"Elemento com a letra O", "oxigenio", "Quimica", "Essencial para os humanos, mas Gems nao precisam para respirar."},
        {"Vilao com a letra J", "jasper", "Steven Universo", "Uma Gem ranzinza que adora uma luta e odeia a Rose Quartz."}
    };

    private final Random random = new Random();

    // Método antigo continua funcionando por ID (para não quebrar os clientes antigos!)
    @WebMethod
    public Desafio obterDesafio(@WebParam(name = "rodadaId") int id) {
        if (id < 0 || id >= bancoDados.length) {
            throw new IllegalArgumentException("Rodada nao existe.");
        }
        return new Desafio(id, bancoDados[id][0], bancoDados[id][2], bancoDados[id][3]);
    }

    // 2. NOVO MÉTODO: Sorteia um desafio aleatório! 🎲
    @WebMethod
    public Desafio obterDesafioAleatorio() {
        int idAleatorio = random.nextInt(bancoDados.length);
        return new Desafio(idAleatorio, bancoDados[idAleatorio][0], bancoDados[idAleatorio][2], bancoDados[idAleatorio][3]);
    }

    @WebMethod
    public ResultadoChute validarChute(@WebParam(name = "rodadaId") int id, @WebParam(name = "chute") String chute) {
        if (id < 0 || id >= bancoDados.length) {
            throw new IllegalArgumentException("Rodada invalida.");
        }

        String respostaCorreta = bancoDados[id][1].trim().toLowerCase();
        String chuteUsuario = chute.trim().toLowerCase();

        if (respostaCorreta.equals(chuteUsuario)) {
            return new ResultadoChute(true, "🌟 Incrivel! Voce acertou! A Perola ficou orgulhosa.", 10);
        } else {
            return new ResultadoChute(false, "💥 Errado! Steven acha que voce consegue tentar melhor na proxima.", 0);
        }
    }

    public static void main(String[] args) {
        String url = "http://localhost:8085/quiz";
        try {
            ClassLoader mavenClassLoader = QuizServidor.class.getClassLoader();
            HttpServer server = HttpServer.create(new InetSocketAddress(8085), 0);
            
            server.setExecutor(Executors.newFixedThreadPool(10, runnable -> {
                Thread t = new Thread(runnable);
                t.setContextClassLoader(mavenClassLoader);
                return t;
            }));
            
            Endpoint endpoint = Endpoint.create(new QuizServidor());
            endpoint.publish(server.createContext("/quiz"));
            
            server.start();
            
            System.out.println("===============================================");
            System.out.println("✨ SERVIDOR SOAP ATUALIZADO E ATIVO! ✨");
            System.out.println("Contrato WSDL: " + url + "?wsdl");
            System.out.println("===============================================");
        } catch (Exception e) {
            System.err.println("Erro ao iniciar o servidor SOAP:");
            e.printStackTrace();
        }
    }
}