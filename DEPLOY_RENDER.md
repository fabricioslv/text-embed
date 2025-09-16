# Deployment no Render

## Passos para deployment:

1. Crie uma conta no [Render](https://render.com/)
2. Conecte sua conta do GitHub
3. Clique em "New Web Service"
4. Selecione o repositório onde está seu projeto
5. Configure as seguintes opções:
   - Name: nome-do-seu-app
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: streamlit run src/app.py --server.port=$PORT --server.address=0.0.0.0
   - Instance Type: Free

6. Clique em "Create Web Service"

## Configurações adicionais:

- O banco de dados SQLite não será persistido entre reinicializações no plano gratuito
- Para persistência de dados, considere usar um banco de dados externo como PostgreSQL
- Variáveis de ambiente podem ser configuradas na seção "Environment" do seu serviço