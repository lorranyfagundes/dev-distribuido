## Desenvolvimento de Sistemas Distribuídos
### Aluna: Lorrany Fagundes
## Projeto REST - Sistema Bancário

### Instalar Dependências:
```pip install -r requirements.txt```

### Execute cada comando em um terminal diferente dentro da pasta raiz:

Microserviço de Contas:     
```python -m uvicorn api_conta:app --port 8001```

Microserviço de Crédito:    
```python -m uvicorn api_credito:app --port 8002```

API Gateway:    
```python -m uvicorn gateway:app --port 8000```

### Configuração do Front-end:
- Abra um quarto terminal
- Entre na pasta do projeto Angular (cliente-web-gateway):
1) Instalar dependências:   
```npm install```

2) Configurar o Endereço do Gateway:    
Abra o arquivo src/app/app.ts e certifique-se de que a urlGateway aponta para o seu localhost: const urlGateway = 'http://localhost:8000/gateway/conta/' + id_da_conta;
3) Iniciar o servidor:  
```ng serve```



## Apresentação (Canva)
https://canva.link/9t5aja73rhgdwpy
