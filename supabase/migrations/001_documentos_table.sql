-- Migration script for documentos table
-- This script creates the documentos table with optimized structure for chunked document storage

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documentos table
CREATE TABLE IF NOT EXISTS documentos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    texto TEXT,
    embedding VECTOR(384), -- Assuming 384 dimensions for all-MiniLM-L6-v2
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documentos_nome ON documentos(nome);
CREATE INDEX IF NOT EXISTS idx_documentos_data ON documentos(data);
CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(tipo);
CREATE INDEX IF NOT EXISTS idx_documentos_chunk_id ON documentos(chunk_id);
CREATE INDEX IF NOT EXISTS idx_documentos_embedding ON documentos USING ivfflat (embedding) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documentos_chunk_embedding ON documentos USING ivfflat (chunk_embedding) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documentos_principal_id ON documentos(documento_principal_id);

-- Create a view for document statistics
CREATE OR REPLACE VIEW documentos_stats AS
SELECT 
    COUNT(*) as total_documentos,
    SUM(tamanho) as tamanho_total,
    AVG(tamanho) as tamanho_medio,
    MIN(data) as data_primeiro,
    MAX(data) as data_ultimo,
    COUNT(DISTINCT tipo) as tipos_diferentes
FROM documentos;

-- Create a function to get document chunks
CREATE OR REPLACE FUNCTION get_document_chunks(doc_id INTEGER)
RETURNS TABLE(
    chunk_id INTEGER,
    chunk_text TEXT,
    chunk_embedding VECTOR(384)
) AS $
BEGIN
    RETURN QUERY
    SELECT d.chunk_id, d.chunk_text, d.chunk_embedding
    FROM documentos d
    WHERE d.id = doc_id OR d.documento_principal_id = doc_id
    ORDER BY d.chunk_id;
END;
$ LANGUAGE plpgsql;

-- Create a function to search similar documents
CREATE OR REPLACE FUNCTION search_similar_documents(query_embedding VECTOR(384), limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    id INTEGER,
    nome VARCHAR(255),
    texto TEXT,
    similarity FLOAT
) AS $
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.nome,
        d.texto,
        (1 - (d.embedding <=> query_embedding)) as similarity
    FROM documentos d
    WHERE d.embedding IS NOT NULL
    ORDER BY d.embedding <=> query_embedding
    LIMIT limit_count;
END;
$ LANGUAGE plpgsql;

-- Add comments to tables and columns for documentation
COMMENT ON TABLE documentos IS 'Tabela principal para armazenamento de documentos e seus embeddings';
COMMENT ON COLUMN documentos.id IS 'Identificador único do documento';
COMMENT ON COLUMN documentos.nome IS 'Nome do documento';
COMMENT ON COLUMN documentos.texto IS 'Texto completo do documento';
COMMENT ON COLUMN documentos.embedding IS 'Embedding do documento completo (384 dimensões)';
COMMENT ON COLUMN documentos.data IS 'Data de criação/atualização do documento';
COMMENT ON COLUMN documentos.tamanho IS 'Tamanho do documento em bytes';
COMMENT ON COLUMN documentos.tipo IS 'Tipo do documento (pdf, docx, txt, etc.)';
COMMENT ON COLUMN documentos.chunk_id IS 'Identificador do chunk (0 para documento completo)';
COMMENT ON COLUMN documentos.total_chunks IS 'Número total de chunks do documento';
COMMENT ON COLUMN documentos.chunk_text IS 'Texto do chunk específico';
COMMENT ON COLUMN documentos.chunk_embedding IS 'Embedding do chunk específico';
COMMENT ON COLUMN documentos.metadata IS 'Metadados adicionais em formato JSON';
COMMENT ON COLUMN documentos.documento_principal_id IS 'Referência ao documento principal para chunks';