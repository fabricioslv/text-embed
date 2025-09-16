# text-embed

Este projeto implementa um vetorizador inteligente de documentos com as seguintes funcionalidades:

- Processamento de PDFs, DOCX e TXT com IA
- Busca semântica
- Exportação de embeddings
- Dashboard completo

## Estrutura do Projeto

```
src/
  __init__.py
  app.py
  database.py
  document_processor.py
  search_engine.py
  utils.py

tests/
  __init__.py
  test_app.py
  test_database.py
  test_document_processor.py
  test_search_engine.py

.github/
  workflows/
    ci-cd.yml

.devcontainer/
  devcontainer.json

Dockerfile
docker-compose.yml
requirements.txt
README.md
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
   streamlit run src/app.py
   ```

## Configuração

O projeto utiliza variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto para definir suas variáveis de ambiente.

## Deploy

O projeto pode ser implantado no Streamlit Cloud ou usando Docker Compose.