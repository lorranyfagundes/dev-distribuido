import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';   

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ButtonModule, CardModule, TagModule], 
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  
  dadosCliente: any = null; 

  constructor(private http: HttpClient) {}

  buscarDados(id_digitado: string) {
    const id_da_conta = Number(id_digitado);

    if (!id_da_conta) {
      alert("Por favor, digite um número de ID válido!");
      return;
    }

    // link do gateway
    const urlGateway = `https://cautious-space-rotary-phone-446w7475wg3jrgr-8000.app.github.dev/gateway/conta/${id_da_conta}`;

    this.http.get(urlGateway).subscribe({
      next: (resposta: any) => {
        this.dadosCliente = resposta; 
        console.log("Sucesso! Dados recebidos do Gateway:", resposta);
      },
      error: (erro: any) => {
        alert("Erro: Conta não encontrada ou Gateway indisponível!");
        console.error("Detalhes do erro:", erro);
        this.dadosCliente = null; 
      }
    });
  }
}