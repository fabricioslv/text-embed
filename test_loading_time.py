"""
Script para testar tempo de carregamento dos componentes críticos
"""
import time
import sys
import os
import traceback
from dotenv import load_dotenv

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_loading_time():
    """Testa o tempo de carregamento dos componentes críticos"""
    print("=== Teste de Tempo de Carregamento ===")
    
    try:
        # Testar carregamento do modelo
        print("1. Testando carregamento do modelo de embeddings...")
        start_time = time.time()
        
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        model_time = time.time() - start_time
        print(f"   Tempo de carregamento do modelo: {model_time:.2f} segundos")
        
        # Testar carregamento do OCR
        print("2. Testando carregamento do OCR...")
        start_time = time.time()
        
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        import easyocr
        reader = easyocr.Reader(['pt'], gpu=False, verbose=False)
        
        ocr_time = time.time() - start_time
        print(f"   Tempo de carregamento do OCR: {ocr_time:.2f} segundos")
        
        # Testar imports pesados
        print("3. Testando imports pesados...")
        start_time = time.time()
        
        import torch
        import torchvision
        import numpy as np
        import faiss
        import pandas as pd
        import plotly
        import sklearn
        
        imports_time = time.time() - start_time
        print(f"   Tempo de imports pesados: {imports_time:.2f} segundos")
        
        # Testar carregamento da aplicação
        print("4. Testando carregamento da aplicação completa...")
        start_time = time.time()
        
        from src.supabase_db import SupabaseDBManager
        from src.document_library import DocumentLibrary, DocumentChunker
        
        # Testar conexão com banco
        try:
            db = SupabaseDBManager()
            docs = db.load_documents()
            print(f"   Documentos carregados: {len(docs)}")
        except Exception as e:
            print(f"   Aviso: Erro ao carregar documentos: {e}")
        
        app_time = time.time() - start_time
        print(f"   Tempo de carregamento da aplicação: {app_time:.2f} segundos")
        
        total_time = model_time + ocr_time + imports_time + app_time
        print(f"\nTempo total de inicialização: {total_time:.2f} segundos")
        
        if total_time > 60:
            print("AVISO: Tempo de inicialização alto (> 60 segundos)")
            print("Isso pode causar timeouts no Streamlit Cloud!")
        elif total_time > 30:
            print("INFO: Tempo de inicialização moderado (30-60 segundos)")
        else:
            print("SUCESSO: Tempo de inicialização aceitável (< 30 segundos)")
        
        print("\n[OK] Teste de tempo de carregamento concluído!")
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste de carregamento: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_loading_time()