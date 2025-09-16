"""
Script simples para verificar se a extensão vector está habilitada no Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_vector_extension():
    """Testa se a extensão vector está habilitada"""
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
        
        # Tentar criar uma tabela com tipo vector para testar se a extensão está habilitada
        try:
            # Primeiro, tentar deletar a tabela de teste se ela existir
            try:
                supabase.rpc("execute_sql", {
                    "sql": "DROP TABLE IF EXISTS teste_vector"
                }).execute()
            except:
                pass  # Ignorar erros na limpeza
            
            # Tentar criar uma tabela com tipo vector
            response = supabase.rpc("execute_sql", {
                "sql": """
                    CREATE TABLE teste_vector (
                        id SERIAL PRIMARY KEY,
                        embedding VECTOR(384)
                    )
                """
            }).execute()
            
            print("SUCESSO: Extensão 'vector' está habilitada!")
            
            # Limpar a tabela de teste
            try:
                supabase.rpc("execute_sql", {
                    "sql": "DROP TABLE IF EXISTS teste_vector"
                }).execute()
            except:
                pass  # Ignorar erros na limpeza
                
            return True
            
        except Exception as e:
            print(f"ERRO: Extensão 'vector' não está habilitada ou há um problema: {e}")
            return False
            
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Supabase: {e}")
        return False

def check_table_exists():
    """Verifica se a tabela documentos existe"""
    try:
        # Obter URL e chave do Supabase das variáveis de ambiente
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("ERRO: SUPABASE_URL ou SUPABASE_KEY não estão definidos!")
            return False
            
        # Criar cliente Supabase
        supabase = create_client(url, key)
        
        # Tentar acessar a tabela documentos
        try:
            response = supabase.table("documentos").select("count").limit(1).execute()
            print("SUCESSO: Tabela 'documentos' existe!")
            return True
        except Exception as e:
            print(f"ERRO: Tabela 'documentos' não existe ou há um problema: {e}")
            return False
            
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Supabase: {e}")
        return False

if __name__ == "__main__":
    print("=== Verificação Simples do Supabase ===")
    vector_ok = test_vector_extension()
    table_ok = check_table_exists()
    
    if vector_ok and table_ok:
        print("\n[OK] Tudo parece estar configurado corretamente!")
    else:
        print("\n[PROBLEMA] Há problemas com a configuração do Supabase.")
        print("Você precisa verificar:")
        if not vector_ok:
            print("- Se a extensão 'vector' está habilitada no Supabase")
        if not table_ok:
            print("- Se a tabela 'documentos' foi criada corretamente")