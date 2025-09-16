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
from src.document_library import DocumentLibrary, DocumentChunker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Depuração - imprimir informações sobre o carregamento das variáveis de ambiente
print("=== Depuração do App ===")
print("Diretório atual:", os.getcwd())
print("Arquivo .env existe:", os.path.exists(".env"))
print("SUPABASE_URL:", os.environ.get("SUPABASE_URL"))
print("SUPABASE_KEY existe:", os.environ.get("SUPABASE_KEY") is not None)
print("========================")

# Configurações iniciais
st.set_page_config(page_title="Vetorizador de Documentos", layout="wide")
st.markdown("""
<style>
.big-title { font-size: 32px; font-weight: bold; color: #4CAF50; }
.subtle { font-size: 16px; color: #777; margin-bottom: 20px; }
.card { background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 10px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); }
.chunk-card { background-color: #e8f5e9; padding: 8px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #4CAF50; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">📚 Vetorizador Inteligente de Documentos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Processamento de PDFs, DOCX e TXT com IA, busca semântica, exportação e dashboard completo.</div>', unsafe_allow_html=True)

# Inicialização
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()
reader = easyocr.Reader(['pt'], gpu=False)
embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)
documentos = []

# Banco de dados - agora usando Supabase
try:
    db = SupabaseDBManager()
    doc_library = DocumentLibrary(db.supabase)
    chunker = DocumentChunker()
    
    # Carrega documentos do banco
    def carregar_documentos():
        try:
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
            st.success(f"Carregados {len(documentos)} documentos do banco de dados.")
        except Exception as e:
            st.warning("Não foi possível carregar documentos do banco de dados. O aplicativo funcionará com dados temporários.")
            st.write(f"Erro: {str(e)}")
            st.write("Tipo de erro:", type(e).__name__)
    
    carregar_documentos()
except Exception as e:
    st.error("Não foi possível conectar ao banco de dados Supabase.")
    st.write(f"Erro: {str(e)}")
    st.write("Tipo de erro:", type(e).__name__)
    db = None
    doc_library = None
    chunker = None

# Funções de extração
def extrair_texto(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext == ".pdf":
        try:
            imagens = convert_from_bytes(file.read())
            texto = ""
            for img in imagens:
                resultado = reader.readtext(np.array(img), detail=0)
                texto += "\n".join(resultado)
            return texto
        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")
            return ""
    elif ext == ".docx":
        try:
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            st.error(f"Erro ao processar DOCX: {e}")
            return ""
    elif ext == ".txt":
        try:
            return file.read().decode('utf-8')
        except Exception as e:
            st.error(f"Erro ao processar TXT: {e}")
            return ""
    else:
        return "Formato não suportado."

# Função para processar e armazenar documento com chunks
def processar_documento(file, db, doc_library):
    texto = extrair_texto(file)
    if texto and len(texto) > 50:
        try:
            # Gerar embedding do documento completo
            embedding = model.encode(texto)
            
            # Determinar tipo do documento
            ext = os.path.splitext(file.name)[1].lower()
            doc_type = ext.replace(".", "") if ext else "txt"
            
            # Metadados adicionais
            metadata = {
                "tamanho_original": len(texto),
                "nome_arquivo": file.name,
                "tipo_arquivo": doc_type,
                "data_processamento": datetime.now().isoformat()
            }
            
            # Salvar documento usando a biblioteca
            doc_id = doc_library.store_document(
                name=file.name,
                text=texto,
                embedding=embedding.tolist(),
                doc_type=doc_type,
                metadata=metadata
            )
            
            return {
                "id": doc_id,
                "nome": file.name,
                "texto": texto,
                "embedding": embedding.tolist(),
                "tipo": doc_type,
                "data": datetime.now().isoformat(),
                "metadata": metadata
            }
        except Exception as e:
            st.error(f"Erro ao processar documento {file.name}: {e}")
            return None
    else:
        return None

# Upload e vetorização
st.header("📂 Upload de Documentos")
uploaded_files = st.file_uploader("Selecione seus arquivos", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files and db is not None and doc_library is not None:
    for file in uploaded_files:
        with st.spinner(f"Processando {file.name}..."):
            documento = processar_documento(file, db, doc_library)
            if documento:
                # Adicionar ao índice FAISS
                index.add(np.array([documento["embedding"]]))
                documentos.append(documento)
                st.success(f"✅ {file.name} processado com sucesso.")
            else:
                st.warning(f"⚠️ {file.name} não pôde ser processado ou está vazio.")
elif uploaded_files and (db is None or doc_library is None):
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