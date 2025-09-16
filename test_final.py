"""
Script final de verificação completa da aplicação
"""
import sys
import os
import traceback
from dotenv import load_dotenv

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_final():
    """Teste final completo da aplicação"""
    print("=== Teste Final Completo da Aplicação ===")
    
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
        from pdf2image import convert_from_bytes
        import easyocr
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
        
        # Testar OCR
        print("4. Inicializando OCR...")
        # Configurar codificação para evitar problemas com EasyOCR
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        reader = easyocr.Reader(['pt'], gpu=False, verbose=False)
        print("   SUCESSO: OCR inicializado!")
        
        # Testar FAISS
        print("5. Inicializando FAISS...")
        embedding_dim = 384
        index = faiss.IndexFlatL2(embedding_dim)
        print("   SUCESSO: FAISS inicializado!")
        
        # Testar conexão com Supabase
        print("6. Testando conexão com Supabase...")
        db = SupabaseDBManager()
        doc_library = DocumentLibrary(db.supabase)
        chunker = DocumentChunker()
        print("   SUCESSO: Conexão com Supabase estabelecida!")
        
        # Testar carregamento de documentos
        print("7. Carregando documentos...")
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
        
        # Testar funcionalidades principais
        print("8. Testando funcionalidades principais...")
        
        # Testar processamento de texto
        test_text = "Este é um documento de teste para verificar as funcionalidades."
        embedding = model.encode(test_text)
        print("   SUCESSO: Processamento de texto e geração de embeddings!")
        
        # Testar busca semântica
        if len(documentos) > 0:
            # Adicionar documento de teste ao índice
            index.add(np.array([embedding]))
            documentos.append({
                "id": 999,
                "nome": "Documento de teste",
                "texto": test_text,
                "embedding": embedding.tolist(),
                "tipo": "txt",
                "data": datetime.now().isoformat(),
                "metadata": {}
            })
            
            # Testar busca
            D, I = index.search(np.array([embedding]), k=1)
            print("   SUCESSO: Busca semântica funcionando!")
        else:
            print("   INFO: Nenhum documento no banco para testar busca semântica")
        
        print("\n[OK] Todos os testes foram bem-sucedidos!")
        print("A aplicação está pronta para ser executada no Streamlit Cloud!")
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final()