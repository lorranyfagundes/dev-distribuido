import { Component, OnInit, OnDestroy } from '@angular/core';
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
  
  desafioAtual: any = null;
  chuteUsuario: string = '';
  feedNotificacoes: any[] = [];

  ngOnInit() {
    this.conectarWebSocket();
  }

  conectarWebSocket() {
  this.ws = new WebSocket('wss://scaling-acorn-pq4vjq96qg7c6r9x-8086.app.github.dev');
    this.ws.onopen = () => {
      this.statusConexao = '🟢 Conectado ao Middleware';
    };

    this.ws.onmessage = (evento) => {
      const dados = JSON.parse(evento.data);

      if (dados.tipo === 'novo_desafio') {
        this.desafioAtual = dados;
        this.chuteUsuario = '';
      } else if (dados.tipo === 'resultado_chute') {
        this.feedNotificacoes.unshift(dados);
      }
    };

    this.ws.onclose = () => {
      this.statusConexao = '🔴 Desconectado. Tentando novamente...';
      setTimeout(() => this.conectarWebSocket(), 3000);
    };
  }

  pedirDesafio() {
    this.ws.send(JSON.stringify({ acao: 'pedir_desafio' }));
  }

  enviarChute() {
    if (!this.chuteUsuario.trim()) return;
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