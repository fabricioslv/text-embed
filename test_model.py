"""
Script para testar o carregamento do modelo de embeddings
"""
import sys
import os
import traceback

def test_model_loading():
    """Testa o carregamento do modelo de embeddings"""
    print("=== Teste de Carregamento do Modelo ===")
    
    try:
        print("1. Importando bibliotecas necessárias...")
        from sentence_transformers import SentenceTransformer
        import numpy as np
        print("   SUCESSO: Bibliotecas importadas!")
        
        print("2. Carregando modelo...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   SUCESSO: Modelo carregado!")
        
        print("3. Testando o modelo...")
        # Testar com um texto de exemplo
        test_text = "Este é um texto de teste para verificar se o modelo está funcionando."
        embedding = model.encode(test_text)
        print(f"   SUCESSO: Embedding gerado com {len(embedding)} dimensões!")
        
        print("4. Testando FAISS...")
        import faiss
        embedding_dim = 384  # Dimensão do all-MiniLM-L6-v2
        index = faiss.IndexFlatL2(embedding_dim)
        print("   SUCESSO: Índice FAISS criado!")
        
        # Adicionar o embedding ao índice
        index.add(np.array([embedding]))
        print("   SUCESSO: Embedding adicionado ao índice FAISS!")
        
        print("\n[OK] Todos os testes foram bem-sucedidos!")
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_model_loading()