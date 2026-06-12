import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App implements OnInit, OnDestroy {
  ws!: WebSocket;
  statusConexao = '🔴 Desconectado';
  
  // Estado do Jogador
  nicknameUsuario = '';
  conectadoNoQuarto = false;
  vencedorPartida = '';

  // Lista de personagens disponíveis
  personagens = [
    { nome: 'Steven', url: 'https://media.giphy.com/media/xorKMdTO2C28L96e9I/giphy.gif' },
    { nome: 'Garnet', url: 'https://media.giphy.com/media/7ziNKdhqx8VAroK766/giphy.gif' },
    { nome: 'Pérola', url: 'https://media.giphy.com/media/5eFREtnL7WydjjiZpG/giphy.gif' },
    { nome: 'Ametista', url: 'https://media.giphy.com/media/aLZ6CJvuOw3vPvgLKd/giphy.gif' },
    { nome: 'Rose', url: 'https://media.giphy.com/media/NklD1aEdJSpJV0ezzc/giphy.gif' }
  ];

  // Personagem que a pessoa escolheu (Steven é o padrão)
  personagemSelecionado = this.personagens[0].url;

  // Estado da Arena (Multiplayer)
  listaJogadores: any[] = [];
  desafioAtual: any = null;
  chuteUsuario = '';
  feedNotificacoes: any[] = [];

  constructor(private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.conectarWebSocket();
  }

  conectarWebSocket() {
    // ⚠️ ATENÇÃO: Cole aqui o SEU link correto da porta 8086 do Codespaces!
    this.ws = new WebSocket('wss://scaling-acorn-pq4vjq96qg7c6r9x-8086.app.github.dev');

    this.ws.onopen = () => {
      this.statusConexao = '🟢 Conectado ao Middleware';
      this.cdr.detectChanges();
    };

    this.ws.onmessage = (evento) => {
      const dados = JSON.parse(evento.data);

      if (dados.tipo === 'novo_desafio') {
        this.desafioAtual = dados;
        this.vencedorPartida = ''; // Limpa vencedor se uma nova rodada começar
        this.chuteUsuario = '';
      } 
      else if (dados.tipo === 'resultado_chute') {
        this.feedNotificacoes.unshift(dados);
      } 
      else if (dados.tipo === 'atualizacao_sala') {
        // Atualiza a posição de todo mundo nas linhas em tempo real!
        this.listaJogadores = dados.jogadores;
      }
      else if (dados.tipo === 'fim_jogo') {
        this.vencedorPartida = dados.vencedor;
        this.desafioAtual = null;
      }
      
      this.cdr.detectChanges();
    };

    this.ws.onclose = () => {
      this.statusConexao = '🔴 Desconectado. Tentando novamente...';
      this.conectadoNoQuarto = false;
      this.cdr.detectChanges();
      setTimeout(() => this.conectarWebSocket(), 3000);
    };
  }

  // Envia o Nickname pro Python registrar o jogador no quarto
  entrarNoQuarto() {
    if (!this.nicknameUsuario.trim()) return;
    this.ws.send(JSON.stringify({
      acao: 'entrar',
      nickname: this.nicknameUsuario,
      personagemUrl: this.personagemSelecionado 
    }));
    this.conectadoNoQuarto = true;
  }

  pedirDesafio() {
    this.ws.send(JSON.stringify({ acao: 'pedir_desafio' }));
  }

  enviarChute() {
    if (!this.chuteUsuario.trim() || !this.desafioAtual) return;
    this.ws.send(JSON.stringify({
      acao: 'enviar_chute',
      id: this.desafioAtual.id,
      chute: this.chuteUsuario
    }));
    this.chuteUsuario = '';
  }

  ngOnDestroy() {
    if (this.ws) this.ws.close();
  }
}