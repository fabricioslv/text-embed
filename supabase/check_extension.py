"""
Script para verificar se a extensão vector está habilitada no Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def check_vector_extension():
    """Verifica se a extensão vector está habilitada"""
    try:
        # Obter URL e chave do Supabase das variáveis de ambiente
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("ERRO: SUPABASE_URL ou SUPABASE_KEY não estão definidos!")
            return False
            
        # Criar cliente Supabase
        supabase = create_client(url, key)
        print("Cliente Supabase criado com sucesso!")
        
        # Verificar se a extensão vector está habilitada
        try:
            # Usar uma consulta direta para verificar a extensão
            response = supabase.rpc("execute_sql", {
                "sql": "SELECT name FROM pg_available_extensions WHERE name = 'vector'"
            }).execute()
            
            if response.data and len(response.data) > 0:
                print("Extensão 'vector' está disponível!")
                
                # Verificar se está instalada
                installed_response = supabase.rpc("execute_sql", {
                    "sql": "SELECT extname FROM pg_extension WHERE extname = 'vector'"
                }).execute()
                
                if installed_response.data and len(installed_response.data) > 0:
                    print("Extensão 'vector' está instalada!")
                    return True
                else:
                    print("AVISO: Extensão 'vector' está disponível mas não está instalada!")
                    return False
            else:
                print("AVISO: Extensão 'vector' não está disponível!")
                return False
                
        except Exception as e:
            print(f"AVISO: Não foi possível verificar a extensão 'vector' diretamente: {e}")
            
            # Tentar uma abordagem alternativa
            try:
                # Tentar criar um tipo vector (isso falhará se a extensão não estiver habilitada)
                test_response = supabase.rpc("execute_sql", {
                    "sql": "SELECT vector_dims('1,2,3'::vector) as dims"
                }).execute()
                
                if test_response.data:
                    print("Extensão 'vector' está habilitada (teste com tipo vector bem-sucedido)!")
                    return True
            except Exception as test_e:
                print(f"AVISO: Extensão 'vector' provavelmente não está habilitada: {test_e}")
                
        return False
        
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Supabase: {e}")
        return False

def check_table_structure():
    """Verifica a estrutura da tabela documentos"""
    try:
        # Obter URL e chave do Supabase das variáveis de ambiente
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("ERRO: SUPABASE_URL ou SUPABASE_KEY não estão definidos!")
            return False
            
        # Criar cliente Supabase
        supabase = create_client(url, key)
        
        # Verificar se a tabela existe e sua estrutura
        try:
            response = supabase.rpc("execute_sql", {
                "sql": """
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'documentos' 
                    ORDER BY ordinal_position
                """
            }).execute()
            
            if response.data:
                print("\n=== Estrutura da Tabela 'documentos' ===")
                for column in response.data:
                    print(f"- {column['column_name']}: {column['data_type']} ({'NULL' if column['is_nullable'] == 'YES' else 'NOT NULL'})")
                return True
            else:
                print("AVISO: Tabela 'documentos' não encontrada!")
                return False
        except Exception as e:
            print(f"AVISO: Não foi possível obter a estrutura da tabela: {e}")
            return False
            
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Supabase: {e}")
        return False

if __name__ == "__main__":
    print("=== Verificação do Supabase ===")
    check_vector_extension()
    check_table_structure()