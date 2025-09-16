# text-embed

Este projeto implementa um vetorizador inteligente de documentos com as seguintes funcionalidades:

- Processamento de PDFs, DOCX e TXT com IA
- Busca semântica
- Exportação de embeddings
- Dashboard completo
- Sistema de chunks para documentos grandes

## Estrutura do Projeto

```
.devcontainer/
  devcontainer.json

.github/
  workflows/
    ci-cd.yml

src/
  database.py
  supabase_db.py
  document_library.py
  utils.py

supabase/
  migrations/
    001_documentos_table.sql
  DATABASE_SCHEMA.md
  init_db.py
  apply_migrations.py

app.py
Dockerfile
docker-compose.yml
Procfile
README.md
requirements.txt
runtime.txt
.env
documentos.db
```

## Como Executar

### Com Docker

```bash
docker-compose up
```

### Localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure o banco de dados Supabase (veja seção abaixo)

3. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## Configuração do Banco de Dados

### Supabase

1. Crie um projeto no [Supabase](https://supabase.io/)
2. Obtenha sua `SUPABASE_URL` e `SUPABASE_KEY` no dashboard
3. Crie um arquivo `.env` na raiz do projeto:
   ```
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_chave_do_supabase
   ```

4. Execute as migrações:
   ```bash
   python supabase/apply_migrations.py
   ```
   
   Ou copie e execute o SQL do arquivo `supabase/migrations/001_documentos_table.sql` no SQL Editor do Supabase.

### Estrutura da Tabela

O sistema utiliza uma única tabela `documentos` que armazena tanto documentos completos quanto chunks individuais. Veja `supabase/DATABASE_SCHEMA.md` para detalhes completos.

## Deploy

O projeto pode ser implantado no Streamlit Cloud ou usando Docker Compose.