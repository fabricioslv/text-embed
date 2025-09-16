# Estrutura do Banco de Dados

## Extensão Necessária

Antes de criar a tabela, é necessário habilitar a extensão `vector`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Tabela `documentos`

A tabela `documentos` é a principal tabela do sistema, armazenando tanto documentos completos quanto chunks individuais.

### Colunas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | SERIAL PRIMARY KEY | Identificador único do registro |
| `nome` | VARCHAR(255) | Nome do documento ou chunk |
| `texto` | TEXT | Texto completo do documento (para registros principais) |
| `embedding` | VECTOR(384) | Embedding do documento completo (384 dimensões) |
| `data` | TIMESTAMP WITH TIME ZONE | Data de criação/atualização |
| `tamanho` | INTEGER | Tamanho do documento em bytes |
| `tipo` | VARCHAR(50) | Tipo do documento (pdf, docx, txt, chunk, etc.) |
| `chunk_id` | INTEGER | ID do chunk (0 para documento completo) |
| `total_chunks` | INTEGER | Número total de chunks do documento |
| `chunk_text` | TEXT | Texto do chunk específico |
| `chunk_embedding` | VECTOR(384) | Embedding do chunk específico |
| `metadata` | JSONB | Metadados adicionais em formato JSON |
| `documento_principal_id` | INTEGER | Referência ao documento principal (para chunks) |

### Índices

1. `idx_documentos_nome` - Índice na coluna `nome`
2. `idx_documentos_data` - Índice na coluna `data`
3. `idx_documentos_tipo` - Índice na coluna `tipo`
4. `idx_documentos_chunk_id` - Índice na coluna `chunk_id`
5. `idx_documentos_embedding` - Índice IVFFlat no `embedding`
6. `idx_documentos_chunk_embedding` - Índice IVFFlat no `chunk_embedding`
7. `idx_documentos_principal_id` - Índice na coluna `documento_principal_id`

## Estratégia de Chunking

Os documentos são divididos em chunks para:

1. **Melhorar a busca semântica** - Permitir busca em partes específicas
2. **Reduzir o consumo de memória** - Processar partes menores
3. **Aumentar a precisão** - Resultados mais relevantes
4. **Facilitar a atualização** - Atualizar partes individuais

### Configuração padrão

- **Tamanho do chunk**: 1000 caracteres
- **Sobreposição**: 100 caracteres
- **Embedding**: all-MiniLM-L6-v2 (384 dimensões)

## Tipos de Documentos

O sistema suporta os seguintes tipos de documentos:

1. **PDF** - Processados com OCR usando EasyOCR
2. **DOCX** - Processados com python-docx
3. **TXT** - Processados diretamente
4. **Chunks** - Fragmentos de documentos maiores

## Metadados

Os documentos podem incluir metadados no formato JSONB:

```json
{
  "autor": "Nome do autor",
  "versao": "1.0",
  "tags": ["tag1", "tag2"],
  "tamanho_original": 12345,
  "nome_arquivo": "documento.pdf",
  "tipo_arquivo": "pdf",
  "data_processamento": "2023-01-01T00:00:00Z"
}
```

## Instruções de Configuração

1. **Habilitar a extensão vector**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Criar a tabela**:
   ```sql
   CREATE TABLE IF NOT EXISTS documentos (
       id SERIAL PRIMARY KEY,
       nome VARCHAR(255) NOT NULL,
       texto TEXT,
       embedding VECTOR(384),
       data TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       tamanho INTEGER,
       tipo VARCHAR(50),
       chunk_id INTEGER DEFAULT 0,
       total_chunks INTEGER DEFAULT 1,
       chunk_text TEXT,
       chunk_embedding VECTOR(384),
       metadata JSONB,
       documento_principal_id INTEGER REFERENCES documentos(id)
   );
   ```

3. **Criar os índices**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_documentos_nome ON documentos(nome);
   CREATE INDEX IF NOT EXISTS idx_documentos_data ON documentos(data);
   CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(tipo);
   CREATE INDEX IF NOT EXISTS idx_documentos_chunk_id ON documentos(chunk_id);
   CREATE INDEX IF NOT EXISTS idx_documentos_embedding ON documentos USING ivfflat (embedding) WITH (lists = 100);
   CREATE INDEX IF NOT EXISTS idx_documentos_chunk_embedding ON documentos USING ivfflat (chunk_embedding) WITH (lists = 100);
   CREATE INDEX IF NOT EXISTS idx_documentos_principal_id ON documentos(documento_principal_id);
   ```

4. **Adicionar comentários (opcional)**:
   ```sql
   COMMENT ON TABLE documentos IS 'Tabela principal para armazenamento de documentos e seus embeddings';
   ```