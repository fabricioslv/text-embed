"""
Script simples para testar a conexão com o Supabase e verificar a tabela documentos
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_simple_connection():
    """Testa a conexão com o Supabase de forma simples"""
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
            # Tentar inserir um registro de teste
            test_data = {
                "nome": "teste_conexao",
                "texto": "Teste de conexão com o banco de dados",
                "tipo": "teste"
            }
            
            response = supabase.table("documentos").insert(test_data).execute()
            print("Inserção de teste bem-sucedida!")
            print(f"ID do registro inserido: {response.data[0]['id']}")
            
            # Tentar selecionar o registro
            select_response = supabase.table("documentos").select("id, nome, tipo").eq("id", response.data[0]['id']).execute()
            print(f"Registro recuperado: {select_response.data}")
            
            # Deletar o registro de teste
            delete_response = supabase.table("documentos").delete().eq("id", response.data[0]['id']).execute()
            print("Registro de teste deletado com sucesso!")
            
            print("\n[OK] Todos os testes de conexão foram bem-sucedidos!")
            return True
            
        except Exception as e:
            print(f"ERRO: Falha no teste de operações: {e}")
            return False
        
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Supabase: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste Simples de Conexão com Supabase ===")
    test_simple_connection()