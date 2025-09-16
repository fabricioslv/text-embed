"""
Script para testar todo o processo de inicialização da aplicação (versão simplificada)
"""
import sys
import os
import traceback
from dotenv import load_dotenv

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_full_initialization():
    """Testa todo o processo de inicialização da aplicação"""
    print("=== Teste Completo de Inicialização ===")
    
    try:
        # Carregar variáveis de ambiente
        print("1. Carregando variáveis de ambiente...")
        load_dotenv()
        print("   SUCESSO: Variáveis de ambiente carregadas!")
        
        # Testar imports
        print("2. Importando bibliotecas...")
        import streamlit as st
        from sentence_transformers import SentenceTransformer
        import json
        import faiss
        import numpy as np
        from datetime import datetime
        import os
        #from pdf2image import convert_from_bytes
        #import easyocr
        from docx import Document
        import pandas as pd
        import plotly.express as px
        from sklearn.metrics.pairwise import cosine_similarity
        from supabase_db import SupabaseDBManager
        from document_library import DocumentLibrary, DocumentChunker
        print("   SUCESSO: Todas as bibliotecas importadas!")
        
        # Testar carregamento do modelo
        print("3. Carregando modelo de embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   SUCESSO: Modelo carregado!")
        
        # Testar FAISS
        print("4. Inicializando FAISS...")
        embedding_dim = 384
        index = faiss.IndexFlatL2(embedding_dim)
        print("   SUCESSO: FAISS inicializado!")
        
        # Testar conexão com Supabase
        print("5. Testando conexão com Supabase...")
        db = SupabaseDBManager()
        doc_library = DocumentLibrary(db.supabase)
        chunker = DocumentChunker()
        print("   SUCESSO: Conexão com Supabase estabelecida!")
        
        # Testar carregamento de documentos
        print("6. Carregando documentos...")
        documentos = []
        docs = db.load_documents()
        for doc in docs:
            emb = doc["embedding"]
            documentos.append({
                "id": doc["id"],
                "nome": doc["nome"], 
                "texto": doc["texto"], 
                "embedding": emb,
                "tipo": doc["tipo"],
                "data": doc["data"],
                "metadata": doc["metadata"]
            })
            if emb:  # Apenas adicionar ao índice se houver embedding
                index.add(np.array([emb]))
        print(f"   SUCESSO: {len(documentos)} documentos carregados!")
        
        print("\n[OK] Todos os testes de inicialização foram bem-sucedidos!")
        print("A aplicação deve funcionar corretamente.")
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_full_initialization()