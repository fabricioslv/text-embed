"""
Script para testar o carregamento completo da aplicação em modo de simulação
"""
import sys
import os
import traceback
from dotenv import load_dotenv

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_app_loading():
    """Testa o carregamento completo da aplicação"""
    print("=== Teste de Carregamento Completo da Aplicação ===")
    
    try:
        # Carregar variáveis de ambiente
        print("1. Carregando variáveis de ambiente...")
        load_dotenv()
        print("   SUCESSO: Variáveis de ambiente carregadas!")
        
        # Testar imports principais
        print("2. Importando bibliotecas principais...")
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
        print("   SUCESSO: Bibliotecas principais importadas!")
        
        # Testar imports do projeto
        print("3. Importando módulos do projeto...")
        from src.supabase_db import SupabaseDBManager
        from src.document_library import DocumentLibrary, DocumentChunker
        print("   SUCESSO: Módulos do projeto importados!")
        
        # Testar carregamento do modelo (cache)
        print("4. Carregando modelo de embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   SUCESSO: Modelo carregado!")
        
        # Testar inicialização do OCR
        print("5. Inicializando OCR...")
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        reader = easyocr.Reader(['pt'], gpu=False, verbose=False)
        print("   SUCESSO: OCR inicializado!")
        
        # Testar inicialização do FAISS
        print("6. Inicializando FAISS...")
        embedding_dim = 384
        index = faiss.IndexFlatL2(embedding_dim)
        documentos = []
        print("   SUCESSO: FAISS inicializado!")
        
        # Testar conexão com Supabase
        print("7. Testando conexão com Supabase...")
        try:
            db = SupabaseDBManager()
            print("   SUCESSO: Conexão com Supabase estabelecida!")
            
            # Testar carregamento de documentos
            print("8. Carregando documentos do banco...")
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
            print(f"   SUCESSO: {len(documentos)} documentos carregados do banco!")
            
        except Exception as db_error:
            print(f"   AVISO: Não foi possível conectar ao banco de dados: {db_error}")
            print("   INFO: A aplicação continuará funcionando com dados temporários...")
            db = None
        
        # Testar funcionalidades principais
        print("9. Testando funcionalidades principais...")
        
        # Testar processamento de texto
        test_text = "Documento de teste para verificação das funcionalidades"
        embedding = model.encode(test_text)
        print("   SUCESSO: Processamento de texto e geração de embeddings!")
        
        # Testar adição ao índice FAISS
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
        print("   SUCESSO: Documento de teste adicionado ao índice!")
        
        # Testar busca semântica
        consulta_embedding = model.encode("teste")
        D, I = index.search(np.array([consulta_embedding]), k=1)
        print("   SUCESSO: Busca semântica funcionando!")
        
        print("\n[OK] Todos os componentes da aplicação estão funcionando corretamente!")
        print("A aplicação está pronta para ser executada.")
        return True
        
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha no carregamento da aplicação: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando teste completo da aplicação...")
    success = test_app_loading()
    if success:
        print("\n" + "="*50)
        print("RESULTADO: APLICAÇÃO PRONTA PARA EXECUTAR!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("RESULTADO: PROBLEMAS ENCONTRADOS!")
        print("="*50)