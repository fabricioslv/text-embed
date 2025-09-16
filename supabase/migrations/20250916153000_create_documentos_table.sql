-- Criação da tabela documentos
CREATE TABLE IF NOT EXISTS documentos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome TEXT,
    texto TEXT,
    embedding JSONB,
    data TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comentários sobre a tabela
COMMENT ON TABLE documentos IS 'Tabela para armazenar documentos e seus embeddings';
COMMENT ON COLUMN documentos.id IS 'Identificador único do documento';
COMMENT ON COLUMN documentos.nome IS 'Nome do documento';
COMMENT ON COLUMN documentos.texto IS 'Texto completo do documento';
COMMENT ON COLUMN documentos.embedding IS 'Embedding do documento em formato JSON';
COMMENT ON COLUMN documentos.data IS 'Data de criação do registro';