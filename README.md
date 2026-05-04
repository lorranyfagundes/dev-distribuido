## Desenvolvimento de Sistemas Distribuídos
### Aluna: Lorrany Silva
## Projeto REST - Sistema Bancário

### instalar:
pip install httpx
npm install
npm install -g @angular/cli

### rodar:
uvicorn api_conta:app --port 8001 --reload 
uvicorn api_credito:app --port 8002 --reload
uvicorn gateway:app --port 8000 --reload
ng serve
