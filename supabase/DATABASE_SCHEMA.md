# Estrutura do Banco de Dados

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

### Views

#### `documentos_stats`

View que fornece estatísticas agregadas dos documentos:

```sql
SELECT 
    COUNT(*) as total_documentos,
    SUM(tamanho) as tamanho_total,
    AVG(tamanho) as tamanho_medio,
    MIN(data) as data_primeiro,
    MAX(data) as data_ultimo,
    COUNT(DISTINCT tipo) as tipos_diferentes
FROM documentos;
```

### Funções

#### `get_document_chunks(doc_id INTEGER)`

Retorna todos os chunks de um documento específico:

```sql
SELECT chunk_id, chunk_text, chunk_embedding
FROM documentos
WHERE id = doc_id OR nome = (SELECT nome FROM documentos WHERE id = doc_id LIMIT 1)
ORDER BY chunk_id;
```

#### `search_similar_documents(query_embedding VECTOR(384), limit_count INTEGER)`

Busca documentos similares com base em um embedding de consulta:

```sql
SELECT 
    id,
    nome,
    texto,
    (1 - (embedding <=> query_embedding)) as similarity
FROM documentos
WHERE embedding IS NOT NULL
ORDER BY embedding <=> query_embedding
LIMIT limit_count;
```

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