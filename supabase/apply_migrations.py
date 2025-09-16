"""
Script para aplicar migrações no Supabase
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.supabase_db import SupabaseDBManager

# Carregar variáveis de ambiente
load_dotenv()

def apply_migrations():
    """Aplica as migrações no banco de dados Supabase"""
    try:
        # Inicializar conexão
        db = SupabaseDBManager()
        supabase = db.supabase
        
        print("Conexão com Supabase estabelecida com sucesso!")
        
        # Verificar se a tabela já existe
        try:
            response = supabase.table("documentos").select("id").limit(1).execute()
            print("Tabela 'documentos' já existe.")
            return True
        except Exception:
            print("Tabela 'documentos' não encontrada. Criando...")
        
        # Como estamos usando SQL migrations, vamos apenas mostrar as instruções
        print("\nPara criar a tabela 'documentos', execute o seguinte SQL no Supabase:")
        print("""
-- Habilitar a extensão vector (necessária para embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar a tabela documentos
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

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_documentos_nome ON documentos(nome);
CREATE INDEX IF NOT EXISTS idx_documentos_data ON documentos(data);
CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(tipo);
CREATE INDEX IF NOT EXISTS idx_documentos_chunk_id ON documentos(chunk_id);
CREATE INDEX IF NOT EXISTS idx_documentos_embedding ON documentos USING ivfflat (embedding) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documentos_chunk_embedding ON documentos USING ivfflat (chunk_embedding) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documentos_principal_id ON documentos(documento_principal_id);

-- Adicionar comentário à tabela
COMMENT ON TABLE documentos IS 'Tabela principal para armazenamento de documentos e seus embeddings';
        """)
        
        return True
        
    except Exception as e:
        print(f"Erro ao aplicar migrações: {e}")
        return False

def test_connection():
    """Testa a conexão com o Supabase"""
    try:
        db = SupabaseDBManager()
        # Tentar uma operação simples
        response = db.supabase.table("documentos").select("id").limit(1).execute()
        print("Conexão com Supabase funcionando corretamente!")
        return True
    except Exception as e:
        print(f"Erro na conexão com Supabase: {e}")
        return False

if __name__ == "__main__":
    print("=== Script de Migração do Supabase ===")
    
    # Testar conexão
    if test_connection():
        # Aplicar migrações
        if apply_migrations():
            print("\n✅ Migrações prontas para serem aplicadas!")
            print("Copie o SQL acima e execute no painel do Supabase em SQL Editor.")
        else:
            print("\n❌ Erro ao preparar migrações.")
    else:
        print("\n❌ Não foi possível conectar ao Supabase. Verifique suas credenciais.")
