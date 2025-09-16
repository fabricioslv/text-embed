"""
Script para testar a conexão com o Supabase e verificar a estrutura do banco de dados
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão com o Supabase e verifica a estrutura do banco de dados"""
    try:
        # Obter URL e chave do Supabase das variáveis de ambiente
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        print("=== Informações de Conexão ===")
        print(f"URL: {url}")
        print(f"Key existe: {key is not None}")
        
        if not url or not key:
            print("ERRO: SUPABASE_URL ou SUPABASE_KEY não estão definidos!")
            return False
            
        # Criar cliente Supabase
        supabase = create_client(url, key)
        print("Cliente Supabase criado com sucesso!")
        
        # Testar conexão com uma operação simples
        try:
            response = supabase.table("documentos").select("id").limit(1).execute()
            print("Conexão com a tabela 'documentos' bem-sucedida!")
        except Exception as e:
            print(f"AVISO: Não foi possível acessar a tabela 'documentos': {e}")
        
        # Verificar se a extensão vector está habilitada
        try:
            response = supabase.rpc("execute_sql", {"sql": "SELECT * FROM pg_extension WHERE extname = 'vector'"}).execute()
            if response.data:
                print("Extensão 'vector' está habilitada!")
            else:
                print("AVISO: Extensão 'vector' não está habilitada!")
        except Exception as e:
            print(f"AVISO: Não foi possível verificar a extensão 'vector': {e}")
            
        # Listar todas as tabelas
        try:
            response = supabase.rpc("execute_sql", {"sql": "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"}).execute()
            print("\n=== Tabelas no Banco de Dados ===")
            for table in response.data:
                print(f"- {table['tablename']}")
        except Exception as e:
            print(f"AVISO: Não foi possível listar as tabelas: {e}")
            
        # Verificar estrutura da tabela documentos
        try:
            response = supabase.rpc("execute_sql", {"sql": """
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'documentos' 
                ORDER BY ordinal_position
            """}).execute()
            
            if response.data:
                print("\n=== Estrutura da Tabela 'documentos' ===")
                for column in response.data:
                    print(f"- {column['column_name']}: {column['data_type']} ({'NULL' if column['is_nullable'] == 'YES' else 'NOT NULL'})")
            else:
                print("AVISO: Tabela 'documentos' não encontrada ou vazia!")
        except Exception as e:
            print(f"AVISO: Não foi possível obter a estrutura da tabela 'documentos': {e}")
            
        return True
        
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Supabase: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Conexão com Supabase ===")
    test_supabase_connection()
