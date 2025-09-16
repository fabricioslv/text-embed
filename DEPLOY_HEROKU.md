# Deployment no Heroku

## Passos para deployment:

1. Crie uma conta no [Heroku](https://www.heroku.com/)
2. Instale o Heroku CLI
3. No diretório do projeto, execute:
   ```bash
   heroku login
   heroku create nome-do-seu-app
   ```

4. Crie um arquivo `Procfile` com o seguinte conteúdo:
   ```
   web: streamlit run src/app.py --server.port=$PORT --server.address=0.0.0.0
   ```

5. Crie um arquivo `runtime.txt` com a versão do Python:
   ```
   python-3.11.9
   ```

6. Faça deploy:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## Configurações adicionais:

- O banco de dados SQLite não será persistido entre reinicializações no plano gratuito
- Para persistência de dados, considere usar um banco de dados externo como PostgreSQL