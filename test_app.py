"""
Script para testar a conexão com o Supabase e carregar documentos
"""
import os
import sys
import traceback
from dotenv import load_dotenv

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from supabase_db import SupabaseDBManager

# Carregar variáveis de ambiente
load_dotenv()

def test_full_connection():
    """Testa a conexão completa e carregamento de documentos"""
    print("=== Teste Completo de Conexão ===")
    
    try:
        # Testar criação do gerenciador de banco de dados
        print("1. Criando gerenciador de banco de dados...")
        db = SupabaseDBManager()
        print("   SUCESSO: Gerenciador criado!")
        
        # Testar carregamento de documentos
        print("2. Carregando documentos...")
        documentos = db.load_documents()
        print(f"   SUCESSO: {len(documentos)} documentos carregados!")
        
        # Mostrar detalhes dos documentos carregados
        for i, doc in enumerate(documentos[:3]):  # Mostrar os 3 primeiros
            print(f"   Documento {i+1}: {doc.get('nome', 'Sem nome')} - {doc.get('tipo', 'Sem tipo')}")
            
        if len(documentos) > 3:
            print(f"   ... e mais {len(documentos) - 3} documentos")
            
        print("\n[OK] Todos os testes foram bem-sucedidos!")
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_full_connection()