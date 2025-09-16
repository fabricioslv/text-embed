"""
Script para inicializar e configurar o banco de dados Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

def init_supabase() -> Client:
    """Inicializa o cliente Supabase"""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos nas variáveis de ambiente")
    
    return create_client(url, key)

def create_documentos_table(supabase: Client):
    """Cria a tabela documentos no Supabase"""
    # Esta função seria usada se estivéssemos usando o serviço de database do Supabase
    # Mas como estamos usando SQL migrations, vamos apenas verificar se a tabela existe
    pass

def check_table_exists(supabase: Client, table_name: str) -> bool:
    """Verifica se uma tabela existe no banco de dados"""
    try:
        # Tenta selecionar um registro da tabela
        response = supabase.table(table_name).select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Erro ao verificar tabela {table_name}: {e}")
        return False

def insert_sample_document(supabase: Client):
    """Insere um documento de exemplo para teste"""
    sample_doc = {
        "nome": "Documento de Exemplo",
        "texto": "Este é um documento de exemplo para testar o sistema de armazenamento.",
        "embedding": [0.1] * 384,  # Embedding de exemplo com 384 dimensões
        "tamanho": 73,
        "tipo": "txt",
        "metadata": {
            "autor": "Sistema",
            "versao": "1.0",
            "tags": ["exemplo", "teste"]
        }
    }
    
    try:
        response = supabase.table("documentos").insert(sample_doc).execute()
        print("Documento de exemplo inserido com sucesso!")
        return response
    except Exception as e:
        print(f"Erro ao inserir documento de exemplo: {e}")
        return None

def get_document_stats(supabase: Client):
    """Obtém estatísticas dos documentos"""
    try:
        # Contagem de documentos
        count_response = supabase.table("documentos").select("*", count="exact").execute()
        total_docs = count_response.count or 0
        
        # Tamanho total
        size_response = supabase.table("documentos").select("tamanho").execute()
        total_size = sum(row["tamanho"] for row in size_response.data if row["tamanho"]) if size_response.data else 0
        
        print(f"Total de documentos: {total_docs}")
        print(f"Tamanho total: {total_size} bytes ({total_size / 1024 / 1024:.2f} MB)")
        
        return {
            "total_documentos": total_docs,
            "tamanho_total": total_size
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")
        return None

def main():
    """Função principal para inicializar o banco de dados"""
    try:
        # Inicializar Supabase
        supabase = init_supabase()
        print("Cliente Supabase inicializado com sucesso!")
        
        # Verificar se a tabela existe
        if check_table_exists(supabase, "documentos"):
            print("Tabela 'documentos' encontrada!")
        else:
            print("Tabela 'documentos' não encontrada. Execute as migrações SQL primeiro.")
            return
        
        # Inserir documento de exemplo
        print("\nInserindo documento de exemplo...")
        insert_sample_document(supabase)
        
        # Obter estatísticas
        print("\nEstatísticas do banco de dados:")
        get_document_stats(supabase)
        
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")

if __name__ == "__main__":
    main()