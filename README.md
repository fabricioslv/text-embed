# text-embed

Este projeto implementa um vetorizador inteligente de documentos com as seguintes funcionalidades:

- Processamento de PDFs, DOCX e TXT com IA
- Busca semântica
- Exportação de embeddings
- Dashboard completo

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
  utils.py

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

2. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## Configuração

O projeto utiliza variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto para definir suas variáveis de ambiente.

## Deploy

O projeto pode ser implantado no Streamlit Cloud ou usando Docker Compose.