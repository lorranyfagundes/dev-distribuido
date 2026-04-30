import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ButtonModule, TagModule],
  template: `
    <div style="padding: 2rem; max-width: 600px; margin: auto; font-family: sans-serif;">
      <h2>Meu Perfil - Banco Digital</h2>
      
      <div *ngIf="dados" style="background: #2a2a2a; padding: 20px; border-radius: 8px; color: white;">
        <h3>Titular: {{ dados.dados_principais.titular }}</h3>
        <p>Saldo: <p-tag severity="success" value="R$ {{ dados.dados_principais.saldo }}"></p-tag></p>
        <p>Limite Cartão: R$ {{ dados.dados_extras.limite_pre_aprovado }}</p>
        
        <hr style="border-color: #444;" />
        <h4>O que você deseja fazer hoje?</h4>
        
        <!-- Mágica do HATEOAS: Os botões são gerados com base nos links que a API manda -->
        <div style="display: flex; gap: 10px;">
           <p-button *ngIf="dados._links.transferir" label="Transferir" icon="pi pi-send"></p-button>
           <p-button *ngIf="dados._links.pagar_boleto" label="Pagar Boleto" icon="pi pi-barcode" severity="warn"></p-button>
           <p-button *ngIf="dados._links.extrato" label="Ver Extrato" icon="pi pi-list" severity="help"></p-button>
        </div>
      </div>

      <div *ngIf="!dados">
        <p-button label="Acessar Minha Conta" (click)="buscarDados()" icon="pi pi-link"></p-button>
      </div>
    </div>
  `
})
export class AppComponent {
  http = inject(HttpClient);
  dados: any = null;

  buscarDados() {
    // ATENÇÃO: Se der erro de conexão, troque este link pelo link gerado na aba "Ports" do seu Codespaces
    const urlGateway = 'https://cautious-space-rotary-phone-446w7475wg3jrgr-8000.app.github.dev/gateway/conta/1';
    
    this.http.get(urlGateway).subscribe({
      next: (resposta) => {
        this.dados = resposta;
        console.log("HATEOAS Recebido:", this.dados._links);
      },
      error: (erro) => alert('Erro! O Gateway está rodando na porta 8000?')
    });
  }
}