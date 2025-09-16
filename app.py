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
from src.supabase_db import SupabaseDBManager
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações iniciais
st.set_page_config(page_title="Vetorizador de Documentos", layout="wide")
st.markdown("""
<style>
.big-title { font-size: 32px; font-weight: bold; color: #4CAF50; }
.subtle { font-size: 16px; color: #777; margin-bottom: 20px; }
.card { background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 10px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">📚 Vetorizador Inteligente de Documentos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Processamento de PDFs, DOCX e TXT com IA, busca semântica, exportação e dashboard completo.</div>', unsafe_allow_html=True)

# Inicialização
model = SentenceTransformer('all-MiniLM-L6-v2')
reader = easyocr.Reader(['pt'], gpu=False)
embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)
documentos = []

# Banco de dados - agora usando Supabase
try:
    db = SupabaseDBManager()
    # Carrega documentos do banco
    def carregar_documentos():
        try:
            docs = db.load_documents()
            for doc in docs:
                emb = doc["embedding"]
                documentos.append({"nome": doc["nome"], "texto": doc["texto"], "embedding": emb})
                index.add(np.array([emb]))
        except Exception as e:
            st.warning("Não foi possível carregar documentos do banco de dados. O aplicativo funcionará com dados temporários.")
            st.write(f"Erro: {str(e)}")
    
    carregar_documentos()
except Exception as e:
    st.error("Não foi possível conectar ao banco de dados Supabase.")
    st.write(f"Erro: {str(e)}")
    db = None

# Funções de extração
def extrair_texto(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext == ".pdf":
        imagens = convert_from_bytes(file.read())
        texto = ""
        for img in imagens:
            resultado = reader.readtext(np.array(img), detail=0)
            texto += "\n".join(resultado)
        return texto
    elif ext == ".docx":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == ".txt":
        return file.read().decode('utf-8')
    else:
        return "Formato não suportado."

# Upload e vetorização
st.header("📂 Upload de Documentos")
uploaded_files = st.file_uploader("Selecione seus arquivos", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files and db is not None:
    for file in uploaded_files:
        texto = extrair_texto(file)
        if texto and len(texto) > 50:
            embedding = model.encode(texto)
            index.add(np.array([embedding]))
            documentos.append({"nome": file.name, "texto": texto, "embedding": embedding.tolist()})
            try:
                db.save_document(file.name, texto, embedding.tolist())
                st.success(f"✅ {file.name} processado com sucesso.")
            except Exception as e:
                st.warning(f"⚠️ {file.name} processado localmente, mas não foi possível salvar no banco de dados.")
                st.write(f"Erro: {str(e)}")
        else:
            st.warning(f"⚠️ {file.name} não pôde ser processado ou está vazio.")
elif uploaded_files and db is None:
    st.error("Não é possível salvar documentos porque não há conexão com o banco de dados.")

# Busca semântica
st.header("🔍 Busca Semântica")
consulta = st.text_input("Digite sua pergunta")

if consulta and len(documentos) > 0:
    consulta_embedding = model.encode(consulta)
    D, I = index.search(np.array([consulta_embedding]), k=3)
    for i in I[0]:
        if i < len(documentos):  # Verificar se o índice é válido
            doc = documentos[i]
            st.markdown(f"<div class='card'><strong>📄 {doc['nome']}</strong><br>{doc['texto'][:500]}...</div>", unsafe_allow_html=True)
elif consulta and len(documentos) == 0:
    st.info("Nenhum documento disponível para busca. Faça upload de alguns documentos primeiro.")

# Chat com documentos
st.header("💬 Chat com os Documentos")
pergunta = st.text_input("Pergunte algo sobre seus arquivos")

if pergunta and len(documentos) > 0:
    pergunta_emb = model.encode(pergunta)
    melhores = sorted(documentos, key=lambda d: cosine_similarity([pergunta_emb], [d["embedding"]])[0][0], reverse=True)
    if len(melhores) > 0:
        trecho = melhores[0]["texto"][:500]
        st.markdown(f"<div class='card'><strong>📄 {melhores[0]['nome']}</strong><br>{trecho}...</div>", unsafe_allow_html=True)
elif pergunta and len(documentos) == 0:
    st.info("Nenhum documento disponível para consulta. Faça upload de alguns documentos primeiro.")

# Exportação
st.header("📤 Exportar Embeddings")
if st.button("Exportar como JSON") and db is not None:
    try:
        docs = db.load_documents()
        export = [{"nome": doc["nome"], "embedding": doc["embedding"]} for doc in docs]
        st.download_button("📥 Baixar JSON", data=json.dumps(export, indent=2), file_name="embeddings.json")
    except Exception as e:
        st.error("Não foi possível exportar os embeddings.")
        st.write(f"Erro: {str(e)}")
elif st.button("Exportar como JSON") and db is None:
    st.error("Não é possível exportar porque não há conexão com o banco de dados.")

# Dashboard
st.header("📊 Resumo de Uso")
if db is not None:
    try:
        total_docs, total_bytes = db.get_document_stats()
        st.metric("📄 Documentos processados", total_docs or 0)
        st.metric("💾 Espaço ocupado", f"{(total_bytes or 0) / 1024 / 1024:.2f} MB")

        st.subheader("📋 Últimos documentos")
        recent_docs = db.get_recent_documents()
        for nome, data in recent_docs:
            st.markdown(f"<div class='card'>📄 <strong>{nome}</strong><br><span class='subtle'>Processado em {data}</span></div>", unsafe_allow_html=True)

        # Gráfico de documentos por data
        all_docs = db.get_all_documents_for_chart()
        if all_docs:
            df = pd.DataFrame(all_docs, columns=["nome", "data"])
            df["data"] = pd.to_datetime(df["data"])
            fig = px.histogram(df, x="data", nbins=20, title="Documentos por Data")
            st.plotly_chart(fig)
    except Exception as e:
        st.warning("Não foi possível carregar as estatísticas do banco de dados.")
        st.write(f"Erro: {str(e)}")
else:
    st.info("As estatísticas do dashboard não estão disponíveis devido à falta de conexão com o banco de dados.")

# Gerenciador de documentos
st.header("🗂️ Gerenciador de Arquivos")
if db is not None:
    try:
        nome_busca = st.text_input("🔎 Buscar documento por nome")
        docs = db.search_documents(nome_busca)

        for doc_id, nome, data, tamanho in docs:
            st.markdown(f"<div class='card'>📄 <strong>{nome}</strong><br><span class='subtle'>{data} — {tamanho / 1024:.1f} KB</span></div>", unsafe_allow_html=True)
            if st.button(f"🗑️ Excluir {nome}", key=doc_id):
                try:
                    db.delete_document(doc_id)
                    st.success(f"{nome} excluído.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Não foi possível excluir {nome}.")
                    st.write(f"Erro: {str(e)}")
    except Exception as e:
        st.warning("Não foi possível carregar os documentos do banco de dados.")
        st.write(f"Erro: {str(e)}")
else:
    st.info("O gerenciador de arquivos não está disponível devido à falta de conexão com o banco de dados.")