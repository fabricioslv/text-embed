"""
Script para testar carregamento progressivo e identificar onde trava
"""
import time
import sys
import os

def test_progressive_loading():
    """Testa o carregamento progressivo dos componentes"""
    print("=== Teste de Carregamento Progressivo ===")
    print("Iniciando teste...")
    
    # Etapa 1: Imports básicos
    print("1. Testando imports basicos...")
    start_time = time.time()
    
    try:
        import streamlit as st
        import os
        from dotenv import load_dotenv
        basic_time = time.time() - start_time
        print(f"   [OK] Imports basicos: {basic_time:.2f}s")
    except Exception as e:
        print(f"   [ERRO] Erro nos imports basicos: {e}")
        return False
    
    # Etapa 2: Carregar variáveis de ambiente
    print("2. Testando carregamento de variaveis de ambiente...")
    start_time = time.time()
    
    try:
        load_dotenv()
        env_time = time.time() - start_time
        print(f"   [OK] Variaveis de ambiente: {env_time:.2f}s")
    except Exception as e:
        print(f"   [ERRO] Erro no carregamento de variaveis: {e}")
        return False
    
    # Etapa 3: Imports pesados
    print("3. Testando imports pesados...")
    start_time = time.time()
    
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        heavy_time = time.time() - start_time
        print(f"   [OK] Imports pesados: {heavy_time:.2f}s")
    except Exception as e:
        print(f"   [ERRO] Erro nos imports pesados: {e}")
        return False
    
    # Etapa 4: Carregamento do modelo
    print("4. Testando carregamento do modelo...")
    start_time = time.time()
    
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        model_time = time.time() - start_time
        print(f"   [OK] Modelo carregado: {model_time:.2f}s")
    except Exception as e:
        print(f"   [ERRO] Erro no carregamento do modelo: {e}")
        return False
    
    # Etapa 5: Teste de funcionalidade
    print("5. Testando funcionalidade basica...")
    start_time = time.time()
    
    try:
        test_text = "Documento de teste"
        embedding = model.encode(test_text)
        func_time = time.time() - start_time
        print(f"   [OK] Funcionalidade basica: {func_time:.2f}s")
        print(f"   [OK] Embedding gerado: {len(embedding)} dimensoes")
    except Exception as e:
        print(f"   [ERRO] Erro na funcionalidade basica: {e}")
        return False
    
    total_time = basic_time + env_time + heavy_time + model_time + func_time
    print(f"\n[OK] Todos os testes concluidos em {total_time:.2f}s")
    return True

if __name__ == "__main__":
    print("Iniciando diagnostico de carregamento...")
    success = test_progressive_loading()
    if success:
        print("\n[SUCCESS] Todos os componentes carregaram corretamente!")
    else:
        print("\n[FAILURE] Houve um problema no carregamento.")