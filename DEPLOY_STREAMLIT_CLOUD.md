# Deployment no Streamlit Cloud

## Passos para deployment:

1. Acesse [Streamlit Cloud](https://streamlit.io/cloud) e faça login com sua conta GitHub
2. Clique em "New app"
3. Selecione o repositório onde está seu projeto
4. Configure as seguintes opções:
   - Branch: main
   - Main file: src/app.py
   - Python version: 3.11
5. Clique em "Deploy"

## Configurações adicionais:

- O Streamlit Cloud automaticamente detectará seu `requirements.txt`
- Variáveis de ambiente podem ser configuradas na seção "Settings" do seu app
- O banco de dados SQLite será persistido entre reinicializações